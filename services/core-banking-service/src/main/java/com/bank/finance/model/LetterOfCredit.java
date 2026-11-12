package com.bank.finance.model;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "letters_of_credit")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class LetterOfCredit {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private UUID id;

    @Column(name = "lc_number", unique = true, nullable = false)
    private String lcNumber;

    @Column(name = "issuing_bank_bic", length = 11, nullable = false)
    private String issuingBankBic;

    @Column(name = "advising_bank_bic", length = 11, nullable = false)
    private String advisingBankBic;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "applicant_id", nullable = false)
    private CorporateAccount applicant;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "beneficiary_id", nullable = false)
    private CorporateAccount beneficiary;

    @Column(name = "currency", length = 3, nullable = false)
    private String currency;

    @Column(name = "amount", nullable = false)
    private BigDecimal amount;

    @Column(name = "tolerance_percentage", nullable = false)
    private BigDecimal tolerancePercentage;

    @Column(name = "applicable_rules", nullable = false)
    private String applicableRules;

    @Column(name = "issue_date", nullable = false)
    private LocalDate issueDate;

    @Column(name = "expiry_date", nullable = false)
    private LocalDate expiryDate;

    @Column(name = "latest_shipment_date", nullable = false)
    private LocalDate latestShipmentDate;

    @Column(name = "port_of_loading", nullable = false)
    private String portOfLoading;

    @Column(name = "port_of_discharge", nullable = false)
    private String portOfDischarge;

    @Column(name = "partial_shipment_allowed", nullable = false)
    private Boolean partialShipmentAllowed;

    @Column(name = "transshipment_allowed", nullable = false)
    private Boolean transshipmentAllowed;

    @Column(name = "incoterm", length = 10, nullable = false)
    private String incoterm;

    @Column(name = "goods_description", columnDefinition = "TEXT", nullable = false)
    private String goodsDescription;

    @Column(name = "status", length = 30, nullable = false)
    private String status;

    @Column(name = "created_at")
    private OffsetDateTime createdAt;

    @Column(name = "updated_at")
    private OffsetDateTime updatedAt;

    @PrePersist
    public void prePersist() {
        OffsetDateTime now = OffsetDateTime.now();
        this.createdAt = now;
        this.updatedAt = now;
        if (this.status == null) {
            this.status = "ISSUED";
        }
        if (this.tolerancePercentage == null) {
            this.tolerancePercentage = BigDecimal.ZERO;
        }
        if (this.applicableRules == null) {
            this.applicableRules = "UCP LATEST VERSION";
        }
    }

    @PreUpdate
    public void preUpdate() {
        this.updatedAt = OffsetDateTime.now();
    }
}
