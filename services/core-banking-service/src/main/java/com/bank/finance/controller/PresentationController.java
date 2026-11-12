package com.bank.finance.controller;

import com.bank.finance.dto.MakerCheckerReviewRequest;
import com.bank.finance.model.DocumentPresentation;
import com.bank.finance.service.PresentationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/presentations")
@RequiredArgsConstructor
@Tag(name = "Document Examination Workbench", description = "Document presentations, Maker-Checker reviews, and Four-Eyes approval")
@CrossOrigin(origins = "*")
public class PresentationController {

    private final PresentationService presentationService;

    @PostMapping
    @Operation(summary = "Submit shipping documents for examination under an LC")
    public ResponseEntity<DocumentPresentation> submitPresentation(
            @RequestParam String lcNumber,
            @RequestParam(defaultValue = "doc_packet_default") String mongoPacketId
    ) {
        DocumentPresentation presentation = presentationService.submitPresentation(lcNumber, mongoPacketId);
        return new ResponseEntity<>(presentation, HttpStatus.CREATED);
    }

    @GetMapping
    @Operation(summary = "List all document presentations")
    public ResponseEntity<List<DocumentPresentation>> getAllPresentations() {
        return ResponseEntity.ok(presentationService.getAllPresentations());
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get document presentation details by ID")
    public ResponseEntity<DocumentPresentation> getPresentationById(@PathVariable UUID id) {
        return ResponseEntity.ok(presentationService.getPresentationById(id));
    }

    @PostMapping("/{id}/maker-review")
    @Operation(summary = "Maker Review: Trade analyst records findings (APPROVE / REQUEST_WAIVER / REFUSE)")
    public ResponseEntity<DocumentPresentation> recordMakerReview(
            @PathVariable UUID id,
            @Valid @RequestBody MakerCheckerReviewRequest request
    ) {
        return ResponseEntity.ok(presentationService.recordMakerReview(id, request));
    }

    @PostMapping("/{id}/checker-decision")
    @Operation(summary = "Checker Decision: Senior manager executes Four-Eyes dual control and triggers atomic settlement")
    public ResponseEntity<DocumentPresentation> recordCheckerDecision(
            @PathVariable UUID id,
            @Valid @RequestBody MakerCheckerReviewRequest request
    ) {
        return ResponseEntity.ok(presentationService.recordCheckerDecision(id, request));
    }
}
