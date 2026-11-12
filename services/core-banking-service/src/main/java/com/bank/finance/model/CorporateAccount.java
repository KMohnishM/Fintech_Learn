package com.bank.finance.model;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "corporate_accounts")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CorporateAccount {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private UUID id;

    @Column(name = "customer_id", unique = true, nullable = false)
    private String customerId;

    @Column(name = "company_name", nullable = false)
    private String companyName;

    @Column(name = "country", length = 3, nullable = false)
    private String country;

    @Column(name = "swift_bic", length = 11, nullable = false)
    private String swiftBic;

    @Column(name = "account_role", nullable = false)
    private String accountRole;

    @Column(name = "credit_limit", nullable = false)
    private BigDecimal creditLimit;

    @Column(name = "utilized_credit", nullable = false)
    private BigDecimal utilizedCredit;

    @Column(name = "collateral_balance", nullable = false)
    private BigDecimal collateralBalance;

    @Column(name = "currency", length = 3, nullable = false)
    private String currency;

    @Column(name = "status", nullable = false)
    private String status;

    @Column(name = "created_at")
    private OffsetDateTime createdAt;

    @PrePersist
    public void prePersist() {
        if (this.createdAt == null) {
            this.createdAt = OffsetDateTime.now();
        }
        if (this.status == null) {
            this.status = "ACTIVE";
        }
        if (this.currency == null) {
            this.currency = "USD";
        }
        if (this.utilizedCredit == null) {
            this.utilizedCredit = BigDecimal.ZERO;
        }
    }
}
