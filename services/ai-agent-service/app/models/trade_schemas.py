from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Incoterm(str, Enum):
    CIF = "CIF"
    FOB = "FOB"
    CFR = "CFR"
    CIP = "CIP"
    EXW = "EXW"

class DocumentType(str, Enum):
    BILL_OF_LADING = "BILL_OF_LADING"
    COMMERCIAL_INVOICE = "COMMERCIAL_INVOICE"
    PACKING_LIST = "PACKING_LIST"
    INSURANCE_CERTIFICATE = "INSURANCE_CERTIFICATE"
    CERTIFICATE_OF_ORIGIN = "CERTIFICATE_OF_ORIGIN"

class DiscrepancySeverity(str, Enum):
    FATAL = "FATAL"         # Requires mandatory payment hold / MT734 refusal unless applicant waives
    WARNING = "WARNING"     # Technical ambiguity / non-material typo (ISBP 745)
    ADVISORY = "ADVISORY"   # Best-practice note

class BoundingBox(BaseModel):
    page: int
    x0: float
    top: float
    x1: float
    bottom: float
    text: str

class LetterOfCredit(BaseModel):
    lc_number: str
    issuing_bank_bic: str
    advising_bank_bic: str
    applicant: str
    beneficiary: str
    currency: str = "USD"
    amount: float
    tolerance_percentage: float = 0.0
    issue_date: str
    expiry_date: str
    latest_shipment_date: str
    port_of_loading: str
    port_of_discharge: str
    partial_shipment_allowed: bool = False
    transshipment_allowed: bool = False
    incoterm: Incoterm = Incoterm.CIF
    goods_description: str
    presentation_period_days: int = 21

class ParsedBillOfLading(BaseModel):
    bl_number: Optional[str] = None
    carrier_name: Optional[str] = None
    vessel_name: Optional[str] = None
    shipped_on_board_date: Optional[str] = None
    port_of_loading: Optional[str] = None
    port_of_discharge: Optional[str] = None
    gross_weight_kg: Optional[float] = None
    is_signed_by_carrier: bool = True
    is_clean: bool = True # False if claused/damaged noted
    bounding_boxes: List[BoundingBox] = []

class ParsedCommercialInvoice(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    seller_name: Optional[str] = None
    buyer_name: Optional[str] = None
    currency: Optional[str] = None
    total_amount: Optional[float] = None
    goods_description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    bounding_boxes: List[BoundingBox] = []

class ParsedPackingList(BaseModel):
    packing_list_number: Optional[str] = None
    total_packages: Optional[int] = None
    gross_weight_kg: Optional[float] = None
    net_weight_kg: Optional[float] = None
    bounding_boxes: List[BoundingBox] = []

class ParsedInsuranceCertificate(BaseModel):
    certificate_number: Optional[str] = None
    insured_amount: Optional[float] = None
    insured_currency: Optional[str] = None
    coverage_percentage: Optional[float] = None
    effective_date: Optional[str] = None
    bounding_boxes: List[BoundingBox] = []

class Discrepancy(BaseModel):
    id: str
    ucp_article: str
    title: str
    severity: DiscrepancySeverity
    document_type: DocumentType
    field_name: str
    expected_value: str
    actual_value: str
    legal_rationale: str
    bounding_box: Optional[BoundingBox] = None

class VerificationReport(BaseModel):
    lc_number: str
    presentation_reference: str
    is_compliant: bool
    fatal_discrepancy_count: int
    warning_count: int
    discrepancies: List[Discrepancy] = []
    generated_swift_mt734: Optional[str] = None
    processing_time_ms: float
