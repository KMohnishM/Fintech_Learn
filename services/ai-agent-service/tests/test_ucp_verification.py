import os
import sys
import pytest

# Ensure app is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.trade_schemas import LetterOfCredit, Incoterm, DiscrepancySeverity
from app.agents.langgraph_workflow import TradeFinanceLangGraph

@pytest.fixture
def baseline_lc():
    return LetterOfCredit(
        lc_number="GB-LC-2026-8891",
        issuing_bank_bic="BOTKJPJT",
        advising_bank_bic="BOTKINBB",
        applicant="Toyota Tsusho Corporation",
        beneficiary="Tata Electronics Private Limited",
        currency="USD",
        amount=250000.00,
        tolerance_percentage=5.00,
        issue_date="2026-10-01",
        expiry_date="2026-12-31",
        latest_shipment_date="2026-11-30",
        port_of_loading="PORT OF NHAVA SHEVA, INDIA",
        port_of_discharge="PORT OF YOKOHAMA, JAPAN",
        incoterm=Incoterm.CIF,
        goods_description="10,000 UNITS OF AUTOMOTIVE MICROCONTROLLERS (MODEL MCU-900). UNIT PRICE USD 25.00 CIF YOKOHAMA. PACKED IN 50 CRATES."
    )

@pytest.fixture
def workflow_engine():
    return TradeFinanceLangGraph()

def test_case1_clean_compliant_presentation(workflow_engine, baseline_lc):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "resources", "test-documents", "case1_clean"))
    pdf_paths = {
        "bl": os.path.join(base_dir, "bill_of_lading.pdf"),
        "invoice": os.path.join(base_dir, "commercial_invoice.pdf"),
        "packing_list": os.path.join(base_dir, "packing_list.pdf"),
        "insurance": os.path.join(base_dir, "insurance_certificate.pdf"),
    }

    report = workflow_engine.verify(
        lc=baseline_lc,
        presentation_ref="PRES-TEST-001",
        pdf_paths=pdf_paths
    )

    assert report.is_compliant is True
    assert report.fatal_discrepancy_count == 0
    assert report.generated_swift_mt734 is None
    print(f"\n[TEST PASS] Case 1 Clean Presentation: {report.processing_time_ms} ms")

def test_case2_late_shipment_discrepancy(workflow_engine, baseline_lc):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "resources", "test-documents"))
    pdf_paths = {
        "bl": os.path.join(base_dir, "case2_late_shipment", "bill_of_lading.pdf"),
        "invoice": os.path.join(base_dir, "case1_clean", "commercial_invoice.pdf"),
        "packing_list": os.path.join(base_dir, "case1_clean", "packing_list.pdf"),
        "insurance": os.path.join(base_dir, "case1_clean", "insurance_certificate.pdf"),
    }

    report = workflow_engine.verify(
        lc=baseline_lc,
        presentation_ref="PRES-TEST-002",
        pdf_paths=pdf_paths
    )

    assert report.is_compliant is False
    assert report.fatal_discrepancy_count >= 1
    assert any("Article 20" in d.ucp_article for d in report.discrepancies)
    assert report.generated_swift_mt734 is not None
    print(f"\n[TEST PASS] Case 2 Late Shipment Caught: {report.discrepancies[0].title}")

def test_case3_description_mismatch(workflow_engine, baseline_lc):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "resources", "test-documents"))
    pdf_paths = {
        "bl": os.path.join(base_dir, "case1_clean", "bill_of_lading.pdf"),
        "invoice": os.path.join(base_dir, "case3_description_mismatch", "commercial_invoice.pdf"),
        "packing_list": os.path.join(base_dir, "case1_clean", "packing_list.pdf"),
        "insurance": os.path.join(base_dir, "case1_clean", "insurance_certificate.pdf"),
    }

    report = workflow_engine.verify(
        lc=baseline_lc,
        presentation_ref="PRES-TEST-003",
        pdf_paths=pdf_paths
    )

    assert report.is_compliant is False
    assert any("Article 18" in d.ucp_article for d in report.discrepancies)
    print(f"\n[TEST PASS] Case 3 Description Mismatch Caught: {report.discrepancies[0].title}")

def test_case4_weight_conflict(workflow_engine, baseline_lc):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "resources", "test-documents"))
    pdf_paths = {
        "bl": os.path.join(base_dir, "case1_clean", "bill_of_lading.pdf"),
        "invoice": os.path.join(base_dir, "case1_clean", "commercial_invoice.pdf"),
        "packing_list": os.path.join(base_dir, "case4_weight_conflict", "packing_list.pdf"),
        "insurance": os.path.join(base_dir, "case1_clean", "insurance_certificate.pdf"),
    }

    report = workflow_engine.verify(
        lc=baseline_lc,
        presentation_ref="PRES-TEST-004",
        pdf_paths=pdf_paths
    )

    assert report.is_compliant is False
    assert any("Article 14" in d.ucp_article for d in report.discrepancies)
    print(f"\n[TEST PASS] Case 4 Weight Conflict Caught: {report.discrepancies[0].title}")

def test_case5_under_insurance(workflow_engine, baseline_lc):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "resources", "test-documents"))
    pdf_paths = {
        "bl": os.path.join(base_dir, "case1_clean", "bill_of_lading.pdf"),
        "invoice": os.path.join(base_dir, "case1_clean", "commercial_invoice.pdf"),
        "packing_list": os.path.join(base_dir, "case1_clean", "packing_list.pdf"),
        "insurance": os.path.join(base_dir, "case5_under_insurance", "insurance_certificate.pdf"),
    }

    report = workflow_engine.verify(
        lc=baseline_lc,
        presentation_ref="PRES-TEST-005",
        pdf_paths=pdf_paths
    )

    assert report.is_compliant is False
    assert any("Article 28" in d.ucp_article for d in report.discrepancies)
    print(f"\n[TEST PASS] Case 5 Under-Insurance Caught: {report.discrepancies[0].title}")
