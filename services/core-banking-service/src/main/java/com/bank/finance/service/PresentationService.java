package com.bank.finance.service;

import com.bank.finance.dto.MakerCheckerReviewRequest;
import com.bank.finance.model.DocumentPresentation;
import com.bank.finance.model.LetterOfCredit;
import com.bank.finance.repository.DocumentPresentationRepository;
import com.bank.finance.repository.LetterOfCreditRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.OffsetDateTime;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class PresentationService {

    private final DocumentPresentationRepository presentationRepository;
    private final LetterOfCreditRepository lcRepository;
    private final SettlementService settlementService;
    private final KafkaTemplate<String, Object> kafkaTemplate;

    private static final String DOCS_UPLOADED_TOPIC = "trade.docs.uploaded";

    @Transactional
    public DocumentPresentation submitPresentation(String lcNumber, String mongoPacketId) {
        LetterOfCredit lc = lcRepository.findByLcNumber(lcNumber)
                .orElseThrow(() -> new IllegalArgumentException("Letter of Credit not found: " + lcNumber));

        String ref = "PRES-" + lcNumber + "-" + (System.currentTimeMillis() % 100000);

        DocumentPresentation presentation = DocumentPresentation.builder()
                .presentationReference(ref)
                .letterOfCredit(lc)
                .mongoDocumentPacketId(mongoPacketId)
                .presentationDate(OffsetDateTime.now())
                .examinationDeadline(OffsetDateTime.now().plusDays(5)) // UCP 600 Art 14
                .overallStatus("UNDER_EXAMINATION")
                .discrepancyCount(0)
                .build();

        DocumentPresentation saved = presentationRepository.save(presentation);
        log.info("Document presentation created: {}", ref);

        // Notify AI Agent via Kafka
        kafkaTemplate.send(DOCS_UPLOADED_TOPIC, ref, saved);

        return saved;
    }

    @Transactional
    public DocumentPresentation recordMakerReview(UUID presentationId, MakerCheckerReviewRequest request) {
        DocumentPresentation presentation = presentationRepository.findById(presentationId)
                .orElseThrow(() -> new IllegalArgumentException("Presentation not found: " + presentationId));

        presentation.setMakerUserId(request.getReviewerUserId());
        presentation.setMakerNotes(request.getNotes());

        if ("APPROVE".equalsIgnoreCase(request.getDecision())) {
            presentation.setOverallStatus("PENDING_CHECKER_APPROVAL");
        } else if ("REQUEST_WAIVER".equalsIgnoreCase(request.getDecision())) {
            presentation.setOverallStatus("WAIVER_REQUESTED");
        } else {
            presentation.setOverallStatus("REFUSED");
        }

        return presentationRepository.save(presentation);
    }

    @Transactional
    public DocumentPresentation recordCheckerDecision(UUID presentationId, MakerCheckerReviewRequest request) {
        DocumentPresentation presentation = presentationRepository.findById(presentationId)
                .orElseThrow(() -> new IllegalArgumentException("Presentation not found: " + presentationId));

        // Enforce Four-Eyes Principle: Checker CANNOT be the same user as the Maker!
        if (request.getReviewerUserId().equalsIgnoreCase(presentation.getMakerUserId())) {
            throw new SecurityException("Four-Eyes Principle Violation: Checker cannot be the same user who made the review.");
        }

        presentation.setCheckerUserId(request.getReviewerUserId());
        presentation.setCheckerDecision(request.getDecision());
        presentation.setCheckerDecisionAt(OffsetDateTime.now());

        if ("APPROVE".equalsIgnoreCase(request.getDecision())) {
            // Trigger atomic double-entry settlement
            settlementService.executeTradeSettlement(presentationId, request.getReviewerUserId());
            presentation.setOverallStatus("SETTLED");
        } else {
            presentation.setOverallStatus("REFUSAL_CONFIRMED");
        }

        return presentationRepository.save(presentation);
    }

    public List<DocumentPresentation> getAllPresentations() {
        return presentationRepository.findAll();
    }

    public DocumentPresentation getPresentationById(UUID id) {
        return presentationRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Presentation not found: " + id));
    }
}
