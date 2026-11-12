package com.bank.finance.repository;

import com.bank.finance.model.LetterOfCredit;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface LetterOfCreditRepository extends JpaRepository<LetterOfCredit, UUID> {
    Optional<LetterOfCredit> findByLcNumber(String lcNumber);
    List<LetterOfCredit> findByApplicantId(UUID applicantId);
    List<LetterOfCredit> findByBeneficiaryId(UUID beneficiaryId);
    List<LetterOfCredit> findByStatus(String status);
}
