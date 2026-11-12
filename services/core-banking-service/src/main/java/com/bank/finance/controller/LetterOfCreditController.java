package com.bank.finance.controller;

import com.bank.finance.dto.CreateLcRequest;
import com.bank.finance.model.LetterOfCredit;
import com.bank.finance.service.LetterOfCreditService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/lc")
@RequiredArgsConstructor
@Tag(name = "Letter of Credit Management", description = "Issuance, querying, and lifecycle of documentary credits")
@CrossOrigin(origins = "*")
public class LetterOfCreditController {

    private final LetterOfCreditService lcService;

    @PostMapping
    @Operation(summary = "Issue a new Letter of Credit", description = "Reserves customer credit line using Redis Redlock and emits trade.lc.issued event to Kafka")
    public ResponseEntity<LetterOfCredit> issueLc(@Valid @RequestBody CreateLcRequest request) {
        LetterOfCredit lc = lcService.issueLetterOfCredit(request);
        return new ResponseEntity<>(lc, HttpStatus.CREATED);
    }

    @GetMapping
    @Operation(summary = "Get all Letters of Credit")
    public ResponseEntity<List<LetterOfCredit>> getAllLcs() {
        return ResponseEntity.ok(lcService.getAllLettersOfCredit());
    }

    @GetMapping("/{lcNumber}")
    @Operation(summary = "Get Letter of Credit by LC Number")
    public ResponseEntity<LetterOfCredit> getLcByNumber(@PathVariable String lcNumber) {
        return ResponseEntity.ok(lcService.getLetterOfCreditByNumber(lcNumber));
    }
}
