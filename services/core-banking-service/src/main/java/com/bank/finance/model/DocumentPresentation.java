package com.bank.finance.model;

import jakarta.persistence.*;
import lombok.*;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "document_presentations")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DocumentPresentation {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private UUID id;

    @Column(name = "presentation_reference", unique = true, nullable = false)
    private String presentationReference;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "lc_id", nullable = false)
    private LetterOfCredit letterOfCredit;

    @Column(name = "mongo_document_packet_id", nullable = false)
    private String mongoDocumentPacketId;

    @Column(name = "presentation_date")
    private OffsetDateTime presentationDate;

    @Column(name = "examination_deadline", nullable = false)
    private OffsetDateTime examinationDeadline;

    @Column(name = "overall_status", length = 30, nullable = false)
    private String overallStatus;

    @Column(name = "discrepancy_count", nullable = false)
    private Integer discrepancyCount;

    @Column(name = "maker_user_id")
    private String makerUserId;

    @Column(name = "maker_notes", columnDefinition = "TEXT")
    private String makerNotes;

    @Column(name = "checker_user_id")
    private String checkerUserId;

    @Column(name = "checker_decision", length = 30)
    private String checkerDecision;

    @Column(name = "checker_decision_at")
    private OffsetDateTime checkerDecisionAt;

    @Column(name = "created_at")
    private OffsetDateTime createdAt;

    @PrePersist
    public void prePersist() {
        OffsetDateTime now = OffsetDateTime.now();
        this.createdAt = now;
        if (this.presentationDate == null) {
            this.presentationDate = now;
        }
        if (this.overallStatus == null) {
            this.overallStatus = "UNDER_EXAMINATION";
        }
        if (this.discrepancyCount == null) {
            this.discrepancyCount = 0;
        }
        // UCP 600 Article 14: 5 banking days deadline
        if (this.examinationDeadline == null) {
            this.examinationDeadline = now.plusDays(5);
        }
    }
}
