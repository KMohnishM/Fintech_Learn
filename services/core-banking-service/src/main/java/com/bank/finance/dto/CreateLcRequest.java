package com.bank.finance.dto;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDate;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CreateLcRequest {

    @NotBlank(message = "LC number is required")
    private String lcNumber;

    @NotBlank(message = "Issuing bank BIC is required")
    private String issuingBankBic;

    @NotBlank(message = "Advising bank BIC is required")
    private String advisingBankBic;

    @NotBlank(message = "Applicant customer ID is required")
    private String applicantCustomerId;

    @NotBlank(message = "Beneficiary customer ID is required")
    private String beneficiaryCustomerId;

    @NotBlank(message = "Currency is required")
    private String currency;

    @NotNull(message = "Amount is required")
    @DecimalMin(value = "1.00", message = "Amount must be at least 1.00")
    private BigDecimal amount;

    private BigDecimal tolerancePercentage;

    @NotNull(message = "Issue date is required")
    private LocalDate issueDate;

    @NotNull(message = "Expiry date is required")
    private LocalDate expiryDate;

    @NotNull(message = "Latest shipment date is required")
    private LocalDate latestShipmentDate;

    @NotBlank(message = "Port of loading is required")
    private String portOfLoading;

    @NotBlank(message = "Port of discharge is required")
    private String portOfDischarge;

    private Boolean partialShipmentAllowed;
    private Boolean transshipmentAllowed;

    @NotBlank(message = "Incoterm is required")
    private String incoterm;

    @NotBlank(message = "Goods description is required")
    private String goodsDescription;
}
