package com.bank.finance.model;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "double_entry_ledger")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DoubleEntryLedger {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private UUID id;

    @Column(name = "transaction_reference", nullable = false)
    private String transactionReference;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "presentation_id")
    private DocumentPresentation presentation;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "source_account_id", nullable = false)
    private CorporateAccount sourceAccount;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "destination_account_id", nullable = false)
    private CorporateAccount destinationAccount;

    @Column(name = "entry_type", nullable = false)
    private String entryType;

    @Column(name = "amount", nullable = false)
    private BigDecimal amount;

    @Column(name = "currency", length = 3, nullable = false)
    private String currency;

    @Column(name = "posted_at")
    private OffsetDateTime postedAt;

    @PrePersist
    public void prePersist() {
        if (this.postedAt == null) {
            this.postedAt = OffsetDateTime.now();
        }
    }
}
