package com.bank.finance.service;

import com.bank.finance.dto.CreateLcRequest;
import com.bank.finance.model.CorporateAccount;
import com.bank.finance.model.LetterOfCredit;
import com.bank.finance.repository.CorporateAccountRepository;
import com.bank.finance.repository.LetterOfCreditRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.redisson.api.RLock;
import org.redisson.api.RedissonClient;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.concurrent.TimeUnit;

@Service
@RequiredArgsConstructor
@Slf4j
public class LetterOfCreditService {

    private final LetterOfCreditRepository lcRepository;
    private final CorporateAccountRepository accountRepository;
    private final RedissonClient redissonClient;
    private final KafkaTemplate<String, Object> kafkaTemplate;

    private static final String LC_ISSUED_TOPIC = "trade.lc.issued";

    @Transactional
    public LetterOfCredit issueLetterOfCredit(CreateLcRequest request) {
        // Distributed Lock on Applicant Customer ID via Redlock
        String lockKey = "lock:customer:credit:" + request.getApplicantCustomerId();
        RLock lock = redissonClient.getLock(lockKey);

        try {
            boolean acquired = lock.tryLock(5, 10, TimeUnit.SECONDS);
            if (!acquired) {
                throw new IllegalStateException("Could not acquire lock for customer credit line. Please retry.");
            }

            CorporateAccount applicant = accountRepository.findByCustomerId(request.getApplicantCustomerId())
                    .orElseThrow(() -> new IllegalArgumentException("Applicant account not found: " + request.getApplicantCustomerId()));

            CorporateAccount beneficiary = accountRepository.findByCustomerId(request.getBeneficiaryCustomerId())
                    .orElseThrow(() -> new IllegalArgumentException("Beneficiary account not found: " + request.getBeneficiaryCustomerId()));

            // Verify credit limit availability
            BigDecimal availableCredit = applicant.getCreditLimit().subtract(applicant.getUtilizedCredit());
            if (availableCredit.compareTo(request.getAmount()) < 0) {
                throw new IllegalStateException(String.format(
                        "Insufficient credit facility. Available: %s %s, Requested: %s",
                        applicant.getCurrency(), availableCredit, request.getAmount()
                ));
            }

            // Reserve the credit facility
            applicant.setUtilizedCredit(applicant.getUtilizedCredit().add(request.getAmount()));
            accountRepository.save(applicant);

            // Create and persist the Letter of Credit
            LetterOfCredit lc = LetterOfCredit.builder()
                    .lcNumber(request.getLcNumber())
                    .issuingBankBic(request.getIssuingBankBic())
                    .advisingBankBic(request.getAdvisingBankBic())
                    .applicant(applicant)
                    .beneficiary(beneficiary)
                    .currency(request.getCurrency())
                    .amount(request.getAmount())
                    .tolerancePercentage(request.getTolerancePercentage() != null ? request.getTolerancePercentage() : BigDecimal.ZERO)
                    .applicableRules("UCP LATEST VERSION")
                    .issueDate(request.getIssueDate())
                    .expiryDate(request.getExpiryDate())
                    .latestShipmentDate(request.getLatestShipmentDate())
                    .portOfLoading(request.getPortOfLoading())
                    .portOfDischarge(request.getPortOfDischarge())
                    .partialShipmentAllowed(Boolean.TRUE.equals(request.getPartialShipmentAllowed()))
                    .transshipmentAllowed(Boolean.TRUE.equals(request.getTransshipmentAllowed()))
                    .incoterm(request.getIncoterm())
                    .goodsDescription(request.getGoodsDescription())
                    .status("ISSUED")
                    .build();

            LetterOfCredit savedLc = lcRepository.save(lc);
            log.info("Letter of Credit successfully issued: {}", savedLc.getLcNumber());

            // Publish event to Kafka
            kafkaTemplate.send(LC_ISSUED_TOPIC, savedLc.getLcNumber(), savedLc);

            return savedLc;

        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Thread interrupted while waiting for credit lock", e);
        } finally {
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }

    public List<LetterOfCredit> getAllLettersOfCredit() {
        return lcRepository.findAll();
    }

    public LetterOfCredit getLetterOfCreditByNumber(String lcNumber) {
        return lcRepository.findByLcNumber(lcNumber)
                .orElseThrow(() -> new IllegalArgumentException("Letter of Credit not found: " + lcNumber));
    }
}
