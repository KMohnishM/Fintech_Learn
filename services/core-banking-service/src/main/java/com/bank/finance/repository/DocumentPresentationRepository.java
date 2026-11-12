package com.bank.finance.repository;

import com.bank.finance.model.DocumentPresentation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface DocumentPresentationRepository extends JpaRepository<DocumentPresentation, UUID> {
    Optional<DocumentPresentation> findByPresentationReference(String presentationReference);
    List<DocumentPresentation> findByLetterOfCreditId(UUID lcId);
    List<DocumentPresentation> findByOverallStatus(String status);
}
