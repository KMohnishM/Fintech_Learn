package com.bank.finance.repository;

import com.bank.finance.model.DoubleEntryLedger;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface DoubleEntryLedgerRepository extends JpaRepository<DoubleEntryLedger, UUID> {
    List<DoubleEntryLedger> findByTransactionReference(String transactionReference);
    List<DoubleEntryLedger> findByPresentationId(UUID presentationId);
}
