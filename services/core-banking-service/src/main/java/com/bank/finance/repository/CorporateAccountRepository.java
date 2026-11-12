package com.bank.finance.repository;

import com.bank.finance.model.CorporateAccount;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface CorporateAccountRepository extends JpaRepository<CorporateAccount, UUID> {
    Optional<CorporateAccount> findByCustomerId(String customerId);
    Optional<CorporateAccount> findBySwiftBic(String swiftBic);
}
