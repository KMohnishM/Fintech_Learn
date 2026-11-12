package com.bank.finance.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MakerCheckerReviewRequest {

    @NotBlank(message = "Reviewer user ID is required")
    private String reviewerUserId;

    @NotBlank(message = "Decision is required (APPROVE, REQUEST_WAIVER, REFUSE)")
    private String decision;

    private String notes;
}
