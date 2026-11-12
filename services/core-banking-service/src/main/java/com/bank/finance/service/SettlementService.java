package com.bank.finance.service;

import com.bank.finance.model.CorporateAccount;
import com.bank.finance.model.DocumentPresentation;
import com.bank.finance.model.DoubleEntryLedger;
import com.bank.finance.model.LetterOfCredit;
import com.bank.finance.repository.CorporateAccountRepository;
import com.bank.finance.repository.DocumentPresentationRepository;
import com.bank.finance.repository.DoubleEntryLedgerRepository;
import com.bank.finance.repository.LetterOfCreditRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class SettlementService {

    private final DocumentPresentationRepository presentationRepository;
    private final LetterOfCreditRepository lcRepository;
    private final CorporateAccountRepository accountRepository;
    private final DoubleEntryLedgerRepository ledgerRepository;
    private final KafkaTemplate<String, Object> kafkaTemplate;

    private static final String PAYMENT_SETTLED_TOPIC = "trade.payment.settled";

    @Transactional
    public DoubleEntryLedger executeTradeSettlement(UUID presentationId, String authorizedCheckerId) {
        DocumentPresentation presentation = presentationRepository.findById(presentationId)
                .orElseThrow(() -> new IllegalArgumentException("Document presentation not found: " + presentationId));

        LetterOfCredit lc = presentation.getLetterOfCredit();
        CorporateAccount importer = lc.getApplicant();
        CorporateAccount exporter = lc.getBeneficiary();

        BigDecimal settlementAmount = lc.getAmount();
        String txRef = "TX-SETTLE-" + System.currentTimeMillis();

        // 1. Deduct Collateral from Importer
        if (importer.getCollateralBalance().compareTo(settlementAmount) < 0) {
            throw new IllegalStateException("Insufficient collateral to settle trade presentation: " + presentation.getPresentationReference());
        }
        importer.setCollateralBalance(importer.getCollateralBalance().subtract(settlementAmount));
        // Release utilized credit line
        importer.setUtilizedCredit(importer.getUtilizedCredit().subtract(settlementAmount));
        accountRepository.save(importer);

        // 2. Credit Exporter Settlement Account
        exporter.setCollateralBalance(exporter.getCollateralBalance().add(settlementAmount));
        accountRepository.save(exporter);

        // 3. Post Immutable Double-Entry Ledger Record
        DoubleEntryLedger entry = DoubleEntryLedger.builder()
                .transactionReference(txRef)
                .presentation(presentation)
                .sourceAccount(importer)
                .destinationAccount(exporter)
                .entryType("SETTLEMENT_LC_DRAWDOWN")
                .amount(settlementAmount)
                .currency(lc.getCurrency())
                .build();

        DoubleEntryLedger savedEntry = ledgerRepository.save(entry);

        // 4. Update Presentation & LC status
        presentation.setOverallStatus("SETTLED");
        presentation.setCheckerUserId(authorizedCheckerId);
        presentation.setCheckerDecision("APPROVED_FOR_PAYMENT");
        presentationRepository.save(presentation);

        lc.setStatus("SETTLED");
        lcRepository.save(lc);

        log.info("Trade presentation {} successfully settled. TX Ref: {}", presentation.getPresentationReference(), txRef);

        // 5. Emit settlement event to Kafka
        kafkaTemplate.send(PAYMENT_SETTLED_TOPIC, txRef, savedEntry);

        return savedEntry;
    }
}
