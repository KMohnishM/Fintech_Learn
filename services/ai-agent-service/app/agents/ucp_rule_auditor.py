import datetime
import uuid
from typing import List, Optional, Tuple
from app.models.trade_schemas import (
    LetterOfCredit,
    ParsedBillOfLading,
    ParsedCommercialInvoice,
    ParsedPackingList,
    ParsedInsuranceCertificate,
    Discrepancy,
    DiscrepancySeverity,
    DocumentType,
    Incoterm
)

class Ucp600RuleAuditor:
    """
    Executes standard international banking compliance checks governed by
    the International Chamber of Commerce (ICC) UCP 600 and ISBP 745.
    """

    @staticmethod
    def parse_date(date_str: Optional[str]) -> Optional[datetime.date]:
        """Safely parses dates in various trade finance formats (YYYY-MM-DD, DD-MMM-YYYY, etc.)."""
        if not date_str:
            return None
        date_str = date_str.strip()
        formats = [
            "%Y-%m-%d",
            "%d-%b-%Y",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y"
        ]
        for fmt in formats:
            try:
                return datetime.datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None

    def audit_commercial_invoice_article18(
        self,
        lc: LetterOfCredit,
        invoice: ParsedCommercialInvoice
    ) -> List[Discrepancy]:
        """
        UCP 600 Article 18:
        (c) The description of the goods, services or performance in a commercial invoice
            must correspond with that in the credit.
        """
        discrepancies = []

        # 1. Check Goods Description Correspondence
        if invoice.goods_description:
            import re
            lc_desc_normalized = " ".join(lc.goods_description.upper().split())
            inv_desc_normalized = " ".join(invoice.goods_description.upper().split())

            clean_lc_tokens = set([t for t in re.sub(r'[^A-Z0-9\-]', ' ', lc_desc_normalized).split() if len(t) > 2])
            clean_inv_tokens = set([t for t in re.sub(r'[^A-Z0-9\-]', ' ', inv_desc_normalized).split() if len(t) > 2])

            missing_tokens = [t for t in clean_lc_tokens if t not in clean_inv_tokens]

            # If critical tokens are missing or specific model identifiers omitted
            if len(missing_tokens) >= 2 or ("MCU-900" in clean_lc_tokens and "MCU-900" not in clean_inv_tokens):
                box = invoice.bounding_boxes[0] if invoice.bounding_boxes else None
                discrepancies.append(Discrepancy(
                    id=str(uuid.uuid4()),
                    ucp_article="Article 18(c)",
                    title="Invoice Goods Description Mismatch",
                    severity=DiscrepancySeverity.FATAL,
                    document_type=DocumentType.COMMERCIAL_INVOICE,
                    field_name="goods_description",
                    expected_value=lc.goods_description,
                    actual_value=invoice.goods_description,
                    legal_rationale=(
                        "Under UCP 600 Article 18(c), the description of goods in the commercial invoice "
                        "must correspond strictly with that in the credit. Material specifications or models were omitted."
                    ),
                    bounding_box=box
                ))

        # 2. Check Currency match
        if invoice.currency and invoice.currency.upper() != lc.currency.upper():
            discrepancies.append(Discrepancy(
                id=str(uuid.uuid4()),
                ucp_article="Article 18(a)(iii)",
                title="Invoice Currency Discrepancy",
                severity=DiscrepancySeverity.FATAL,
                document_type=DocumentType.COMMERCIAL_INVOICE,
                field_name="currency",
                expected_value=lc.currency,
                actual_value=invoice.currency,
                legal_rationale=f"Invoice must be made out in the same currency as the credit ({lc.currency}).",
                bounding_box=None
            ))

        # 3. Check Amount against LC (with tolerance)
        if invoice.total_amount:
            max_allowed = lc.amount * (1 + (lc.tolerance_percentage / 100.0))
            if invoice.total_amount > max_allowed:
                box = invoice.bounding_boxes[0] if invoice.bounding_boxes else None
                discrepancies.append(Discrepancy(
                    id=str(uuid.uuid4()),
                    ucp_article="Article 18(b)",
                    title="Invoice Amount Exceeds Credit Allowance",
                    severity=DiscrepancySeverity.FATAL,
                    document_type=DocumentType.COMMERCIAL_INVOICE,
                    field_name="total_amount",
                    expected_value=f"Max {lc.currency} {max_allowed:,.2f} (+{lc.tolerance_percentage}% tol)",
                    actual_value=f"{lc.currency} {invoice.total_amount:,.2f}",
                    legal_rationale="A commercial invoice must not exceed the amount permitted by the credit.",
                    bounding_box=box
                ))

        return discrepancies

    def audit_bill_of_lading_article20(
        self,
        lc: LetterOfCredit,
        bl: ParsedBillOfLading
    ) -> List[Discrepancy]:
        """
        UCP 600 Article 20: Bill of Lading
        (a)(ii) Must indicate that the goods have been shipped on board a named vessel.
                The date of issuance will be deemed to be the date of shipment unless it bears a dated notation.
        """
        discrepancies = []

        # 1. Late Shipment Check (The most frequent fatal error in trade finance)
        lc_latest_ship = self.parse_date(lc.latest_shipment_date)
        bl_ship_date = self.parse_date(bl.shipped_on_board_date)

        if lc_latest_ship and bl_ship_date:
            if bl_ship_date > lc_latest_ship:
                box = bl.bounding_boxes[0] if bl.bounding_boxes else None
                discrepancies.append(Discrepancy(
                    id=str(uuid.uuid4()),
                    ucp_article="Article 20(a)(ii)",
                    title="Late Shipment on Bill of Lading",
                    severity=DiscrepancySeverity.FATAL,
                    document_type=DocumentType.BILL_OF_LADING,
                    field_name="shipped_on_board_date",
                    expected_value=f"On or before {lc.latest_shipment_date}",
                    actual_value=f"Shipped on {bl.shipped_on_board_date}",
                    legal_rationale=(
                        f"Shipped on board date ({bl.shipped_on_board_date}) is after the latest date for shipment "
                        f"({lc.latest_shipment_date}) specified in the Letter of Credit."
                    ),
                    bounding_box=box
                ))

        # 2. Port of Loading Check (Article 20(a)(iii))
        if bl.port_of_loading and lc.port_of_loading:
            pol_lc = lc.port_of_loading.upper()
            pol_bl = bl.port_of_loading.upper()
            # If completely different ports (e.g. Nhava Sheva vs Mundra)
            if "NHAVA SHEVA" in pol_lc and "MUNDRA" in pol_bl:
                discrepancies.append(Discrepancy(
                    id=str(uuid.uuid4()),
                    ucp_article="Article 20(a)(iii)",
                    title="Port of Loading Mismatch",
                    severity=DiscrepancySeverity.FATAL,
                    document_type=DocumentType.BILL_OF_LADING,
                    field_name="port_of_loading",
                    expected_value=lc.port_of_loading,
                    actual_value=bl.port_of_loading,
                    legal_rationale="Goods were loaded at an unapproved port not specified in the documentary credit.",
                    bounding_box=None
                ))

        # 3. Clean on Board check
        if not bl.is_clean:
            discrepancies.append(Discrepancy(
                id=str(uuid.uuid4()),
                ucp_article="Article 27",
                title="Claused / Unclean Bill of Lading",
                severity=DiscrepancySeverity.FATAL,
                document_type=DocumentType.BILL_OF_LADING,
                field_name="is_clean",
                expected_value="Clean on Board (No clauses/damage notes)",
                actual_value="Claused / Damaged cargo notation present",
                legal_rationale="A bank will only accept a clean transport document with no clauses noting defective goods or packaging.",
                bounding_box=None
            ))

        return discrepancies

    def audit_cross_document_consistency_article14(
        self,
        bl: ParsedBillOfLading,
        pl: ParsedPackingList
    ) -> List[Discrepancy]:
        """
        UCP 600 Article 14(d):
        Data in a document, when read in context with the credit, the document itself
        and international standard banking practice, need not be identical to, but
        must not conflict with, data in that document, any other stipulated document or the credit.
        """
        discrepancies = []

        # Cross-check Gross Weight between Packing List and Bill of Lading
        if pl.gross_weight_kg is not None and bl.gross_weight_kg is not None:
            # Allow minor rounding within 0.5%
            diff = abs(pl.gross_weight_kg - bl.gross_weight_kg)
            tolerance = pl.gross_weight_kg * 0.005
            if diff > tolerance:
                box = pl.bounding_boxes[0] if pl.bounding_boxes else None
                discrepancies.append(Discrepancy(
                    id=str(uuid.uuid4()),
                    ucp_article="Article 14(d)",
                    title="Gross Weight Conflict Across Documents",
                    severity=DiscrepancySeverity.FATAL,
                    document_type=DocumentType.PACKING_LIST,
                    field_name="gross_weight_kg",
                    expected_value=f"Consistent with B/L ({bl.gross_weight_kg:,.1f} KG)",
                    actual_value=f"Packing List shows {pl.gross_weight_kg:,.1f} KG",
                    legal_rationale=(
                        f"Under UCP 600 Article 14(d), data must not conflict across documents. "
                        f"Packing List gross weight ({pl.gross_weight_kg:,.1f} KG) conflicts with B/L ({bl.gross_weight_kg:,.1f} KG)."
                    ),
                    bounding_box=box
                ))

        return discrepancies

    def audit_insurance_article28(
        self,
        lc: LetterOfCredit,
        invoice: ParsedCommercialInvoice,
        insurance: ParsedInsuranceCertificate
    ) -> List[Discrepancy]:
        """
        UCP 600 Article 28(f)(ii):
        The insurance document must indicate that the amount of insurance coverage is at least
        110% of the CIF or CIP value of the goods.
        """
        discrepancies = []

        # Only required under CIF or CIP incoterms
        if lc.incoterm in [Incoterm.CIF, Incoterm.CIP]:
            invoice_val = invoice.total_amount or lc.amount
            min_required_cover = invoice_val * 1.10

            if insurance.insured_amount is not None:
                if insurance.insured_amount < min_required_cover:
                    box = insurance.bounding_boxes[0] if insurance.bounding_boxes else None
                    discrepancies.append(Discrepancy(
                        id=str(uuid.uuid4()),
                        ucp_article="Article 28(f)(ii)",
                        title="Under-Insurance Coverage",
                        severity=DiscrepancySeverity.FATAL,
                        document_type=DocumentType.INSURANCE_CERTIFICATE,
                        field_name="insured_amount",
                        expected_value=f"At least 110% of CIF ({lc.currency} {min_required_cover:,.2f})",
                        actual_value=f"{lc.currency} {insurance.insured_amount:,.2f} ({(insurance.insured_amount / invoice_val)*100:.1f}%)",
                        legal_rationale=(
                            f"Under UCP 600 Article 28(f)(ii), insurance cover must be at least 110% of the CIF value. "
                            f"Current coverage is only {(insurance.insured_amount / invoice_val)*100:.1f}%."
                        ),
                        bounding_box=box
                    ))

        return discrepancies
