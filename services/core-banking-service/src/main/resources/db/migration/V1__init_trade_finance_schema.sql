-- =========================================================================
-- V1__init_trade_finance_schema.sql
-- Autonomous Trade Finance & UCP 600 Letter of Credit Engine
-- PostgreSQL ACID Ledger, Corporate Accounts, and LC State Machine
-- =========================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Corporate Accounts & Credit Facilities
CREATE TABLE IF NOT EXISTS corporate_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id VARCHAR(50) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    country VARCHAR(3) NOT NULL,
    swift_bic VARCHAR(11) NOT NULL,
    account_role VARCHAR(50) NOT NULL,
    credit_limit DECIMAL(18, 2) NOT NULL DEFAULT 0.00,
    utilized_credit DECIMAL(18, 2) NOT NULL DEFAULT 0.00,
    collateral_balance DECIMAL(18, 2) NOT NULL DEFAULT 0.00,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_positive_credit CHECK (credit_limit >= 0),
    CONSTRAINT chk_credit_utilization CHECK (utilized_credit <= credit_limit)
);

-- 2. Letters of Credit (LC Contract Registry)
CREATE TABLE IF NOT EXISTS letters_of_credit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lc_number VARCHAR(50) UNIQUE NOT NULL,
    issuing_bank_bic VARCHAR(11) NOT NULL,
    advising_bank_bic VARCHAR(11) NOT NULL,
    applicant_id UUID NOT NULL REFERENCES corporate_accounts(id),
    beneficiary_id UUID NOT NULL REFERENCES corporate_accounts(id),
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    amount DECIMAL(18, 2) NOT NULL,
    tolerance_percentage DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    applicable_rules VARCHAR(50) NOT NULL DEFAULT 'UCP LATEST VERSION',
    issue_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    latest_shipment_date DATE NOT NULL,
    port_of_loading VARCHAR(255) NOT NULL,
    port_of_discharge VARCHAR(255) NOT NULL,
    partial_shipment_allowed BOOLEAN NOT NULL DEFAULT FALSE,
    transshipment_allowed BOOLEAN NOT NULL DEFAULT FALSE,
    incoterm VARCHAR(10) NOT NULL,
    goods_description TEXT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'ISSUED',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_lc_amount CHECK (amount > 0),
    CONSTRAINT chk_lc_dates CHECK (expiry_date >= latest_shipment_date AND latest_shipment_date >= issue_date)
);

-- 3. Document Presentations (Lifecycle of shipping docs submitted under an LC)
CREATE TABLE IF NOT EXISTS document_presentations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    presentation_reference VARCHAR(50) UNIQUE NOT NULL,
    lc_id UUID NOT NULL REFERENCES letters_of_credit(id),
    mongo_document_packet_id VARCHAR(100) NOT NULL,
    presentation_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    examination_deadline TIMESTAMP WITH TIME ZONE NOT NULL, -- UCP 600 Art 14: 5 banking days
    overall_status VARCHAR(30) NOT NULL DEFAULT 'UNDER_EXAMINATION',
    discrepancy_count INT NOT NULL DEFAULT 0,
    maker_user_id VARCHAR(100),
    maker_notes TEXT,
    checker_user_id VARCHAR(100),
    checker_decision VARCHAR(30) DEFAULT 'PENDING',
    checker_decision_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Double-Entry Accounting Ledger (Immutable Financial Journal)
CREATE TABLE IF NOT EXISTS double_entry_ledger (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_reference VARCHAR(100) NOT NULL,
    presentation_id UUID REFERENCES document_presentations(id),
    source_account_id UUID NOT NULL REFERENCES corporate_accounts(id),
    destination_account_id UUID NOT NULL REFERENCES corporate_accounts(id),
    entry_type VARCHAR(50) NOT NULL,
    amount DECIMAL(18, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    posted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_positive_ledger_amount CHECK (amount > 0)
);

-- 5. Audit Trails (Enterprise Compliance)
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    actor_id VARCHAR(100) NOT NULL,
    actor_role VARCHAR(50) NOT NULL,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indices for high performance
CREATE INDEX IF NOT EXISTS idx_lc_number ON letters_of_credit(lc_number);
CREATE INDEX IF NOT EXISTS idx_lc_status ON letters_of_credit(status);
CREATE INDEX IF NOT EXISTS idx_presentation_lc_id ON document_presentations(lc_id);
CREATE INDEX IF NOT EXISTS idx_presentation_status ON document_presentations(overall_status);
CREATE INDEX IF NOT EXISTS idx_ledger_tx_ref ON double_entry_ledger(transaction_reference);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_type, entity_id);

-- =========================================================================
-- SEED DATA: Realistic MUFG Corporate Banking Benchmark Entities
-- =========================================================================

-- Toyota Tsusho Corporation (Japan - Importer)
INSERT INTO corporate_accounts (
    id, customer_id, company_name, country, swift_bic, account_role, credit_limit, utilized_credit, collateral_balance, currency
) VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'CUST_JP_TOYOTA_001',
    'Toyota Tsusho Corporation',
    'JPN',
    'BOTKJPJT',
    'APPLICANT_IMPORTER',
    10000000.00,
    1500000.00,
    5000000.00,
    'USD'
) ON CONFLICT (customer_id) DO NOTHING;

-- Tata Electronics Private Limited (India - Exporter)
INSERT INTO corporate_accounts (
    id, customer_id, company_name, country, swift_bic, account_role, credit_limit, utilized_credit, collateral_balance, currency
) VALUES (
    'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
    'CUST_IN_TATA_002',
    'Tata Electronics Private Limited',
    'IND',
    'BOTKINBB',
    'BENEFICIARY_EXPORTER',
    5000000.00,
    0.00,
    1000000.00,
    'USD'
) ON CONFLICT (customer_id) DO NOTHING;

-- Global Commercial Bank Tokyo (Issuing Bank)
INSERT INTO corporate_accounts (
    id, customer_id, company_name, country, swift_bic, account_role, credit_limit, utilized_credit, collateral_balance, currency
) VALUES (
    'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33',
    'BANK_GLOBAL_TOKYO',
    'Global Commercial Bank, Tokyo Head Office',
    'JPN',
    'BOTKJPJT',
    'ISSUING_BANK',
    100000000.00,
    0.00,
    0.00,
    'USD'
) ON CONFLICT (customer_id) DO NOTHING;

-- Baseline Realistic Benchmark Letter of Credit (SWIFT MT 700 format backing)
INSERT INTO letters_of_credit (
    id, lc_number, issuing_bank_bic, advising_bank_bic, applicant_id, beneficiary_id,
    currency, amount, tolerance_percentage, applicable_rules,
    issue_date, expiry_date, latest_shipment_date,
    port_of_loading, port_of_discharge,
    partial_shipment_allowed, transshipment_allowed, incoterm,
    goods_description, status
) VALUES (
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a44',
    'GB-LC-2026-8891',
    'BOTKJPJT',
    'BOTKINBB',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
    'USD',
    250000.00,
    5.00,
    'UCP LATEST VERSION',
    '2026-10-01',
    '2026-12-31',
    '2026-11-30',
    'PORT OF NHAVA SHEVA, INDIA',
    'PORT OF YOKOHAMA, JAPAN',
    FALSE,
    FALSE,
    'CIF',
    '10,000 UNITS OF AUTOMOTIVE MICROCONTROLLERS (MODEL MCU-900). UNIT PRICE USD 25.00 CIF YOKOHAMA. PACKED IN 50 CRATES.',
    'ISSUED'
) ON CONFLICT (lc_number) DO NOTHING;
