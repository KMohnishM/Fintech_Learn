import re
import os
from typing import Dict, Any, List, Optional, Tuple
from app.models.trade_schemas import (
    BoundingBox,
    ParsedBillOfLading,
    ParsedCommercialInvoice,
    ParsedPackingList,
    ParsedInsuranceCertificate,
    DocumentType
)

class TradePdfParser:
    """
    Day-1 PDF OCR & Spatial Bounding Box Extractor for Trade Finance Documents.
    Extracts text, numerical values, and exact pixel coordinates [page, x0, top, x1, bottom]
    for interactive document inspection in the banking workbench.
    """

    def __init__(self):
        pass

    def extract_words_with_boxes(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extracts all words with their bounding boxes across all pages."""
        words_data = []
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for page_idx, page in enumerate(pdf.pages):
                    page_words = page.extract_words()
                    for w in page_words:
                        words_data.append({
                            "page": page_idx + 1,
                            "text": w["text"],
                            "x0": float(w["x0"]),
                            "top": float(w["top"]),
                            "x1": float(w["x1"]),
                            "bottom": float(w["bottom"])
                        })
        except Exception as e:
            # Fallback for plain text extraction if pdfplumber is not available or non-PDF
            pass
        return words_data

    def extract_full_text(self, pdf_path: str) -> str:
        """Extracts complete text across all pages."""
        full_text = ""
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
        except Exception:
            if os.path.exists(pdf_path):
                try:
                    with open(pdf_path, "r", encoding="utf-8", errors="ignore") as f:
                        full_text = f.read()
                except Exception:
                    pass
        return full_text

    def find_bounding_box_for_pattern(self, words: List[Dict[str, Any]], pattern: str) -> Optional[BoundingBox]:
        """Finds spatial bounding box coordinates matching a target regex or substring."""
        regex = re.compile(pattern, re.IGNORECASE)
        for w in words:
            if regex.search(w["text"]):
                return BoundingBox(
                    page=w["page"],
                    x0=w["x0"],
                    top=w["top"],
                    x1=w["x1"],
                    bottom=w["bottom"],
                    text=w["text"]
                )
        return None

    def parse_bill_of_lading(self, pdf_path: str) -> ParsedBillOfLading:
        """Parses Marine/Ocean Bill of Lading adhering to UCP 600 Article 20."""
        text = self.extract_full_text(pdf_path)
        words = self.extract_words_with_boxes(pdf_path)
        bl = ParsedBillOfLading()

        # B/L Number
        bl_match = re.search(r'(?:B/L\s*NO\.?|BILL\s*OF\s*LADING\s*NO\.?|BL\s*NUMBER)[\s:]*([A-Z0-9\-_/]+)', text, re.I)
        if bl_match:
            bl.bl_number = bl_match.group(1).strip()
            box = self.find_bounding_box_for_pattern(words, re.escape(bl.bl_number))
            if box: bl.bounding_boxes.append(box)

        # Carrier Name
        carrier_match = re.search(r'(?:CARRIER|SHIPPING\s*LINE|ISSUED\s*BY)[\s:]*([A-Za-z0-9\s.,]+?)(?:\n|$)', text, re.I)
        if carrier_match:
            bl.carrier_name = carrier_match.group(1).strip()

        # Shipped on Board Date (UCP 600 Art 20(a)(ii))
        board_date_match = re.search(r'(?:SHIPPED\s*ON\s*BOARD(?:\s*DATE)?|ON\s*BOARD\s*DATE)[\s:]*(\d{2,4}[-/\.]\w+[-/\.]\d{2,4}|\w+\s+\d{1,2},?\s+\d{4}|\d{1,2}\s+\w+\s+\d{4})', text, re.I)
        if board_date_match:
            bl.shipped_on_board_date = board_date_match.group(1).strip()
            box = self.find_bounding_box_for_pattern(words, r'SHIPPED|BOARD|\d{4}')
            if box: bl.bounding_boxes.append(box)

        # Port of Loading & Discharge (UCP 600 Art 20(a)(iii))
        pol_match = re.search(r'(?:PORT\s*OF\s*LOADING)[\s:]*([A-Za-z0-9\s,.-]+?)(?:\n|PORT\s*OF|$)', text, re.I)
        if pol_match:
            bl.port_of_loading = pol_match.group(1).strip()

        pod_match = re.search(r'(?:PORT\s*OF\s*DISCHARGE)[\s:]*([A-Za-z0-9\s,.-]+?)(?:\n|PLACE\s*OF|$)', text, re.I)
        if pod_match:
            bl.port_of_discharge = pod_match.group(1).strip()

        # Gross Weight
        weight_match = re.search(r'(?:GROSS\s*WEIGHT|TOTAL\s*WEIGHT)[\s:]*([\d,.]+)\s*(?:KG|KGS|MT)?', text, re.I)
        if weight_match:
            try:
                bl.gross_weight_kg = float(weight_match.group(1).replace(',', ''))
            except ValueError:
                pass

        # Check clean on board
        if re.search(r'(?:DAMAGED|TORN|LEAKING|STAINED|CLAUSED)', text, re.I):
            bl.is_clean = False

        return bl

    def parse_commercial_invoice(self, pdf_path: str) -> ParsedCommercialInvoice:
        """Parses Commercial Invoice adhering to UCP 600 Article 18."""
        text = self.extract_full_text(pdf_path)
        words = self.extract_words_with_boxes(pdf_path)
        inv = ParsedCommercialInvoice()

        inv_match = re.search(r'(?:INVOICE\s*NO\.?|INVOICE\s*NUMBER)[\s:]*([A-Z0-9\-_/]+)', text, re.I)
        if inv_match:
            inv.invoice_number = inv_match.group(1).strip()
            box = self.find_bounding_box_for_pattern(words, re.escape(inv.invoice_number))
            if box: inv.bounding_boxes.append(box)

        # Amount & Currency
        amount_match = re.search(r'(?:TOTAL(?:\s*AMOUNT)?|INVOICE\s*TOTAL)[\s:]*([A-Z]{3})?\s*[\$€¥]?\s*([\d,]+\.?\d*)', text, re.I)
        if amount_match:
            inv.currency = amount_match.group(1) or "USD"
            try:
                inv.total_amount = float(amount_match.group(2).replace(',', ''))
            except ValueError:
                pass
            box = self.find_bounding_box_for_pattern(words, r'TOTAL|\d{3,}')
            if box: inv.bounding_boxes.append(box)

        # Goods Description
        desc_match = re.search(r'(?:DESCRIPTION\s*OF\s*GOODS|COMMODITY|ITEM\s*DESCRIPTION)[\s:]*([^\n\r]+(?:\n[^\n\r]+)?)', text, re.I)
        if desc_match:
            inv.goods_description = desc_match.group(1).strip()

        # Quantity
        qty_match = re.search(r'(?:QUANTITY|TOTAL\s*QTY)[\s:]*([\d,]+)\s*(?:UNITS|PCS|MT)?', text, re.I)
        if qty_match:
            try:
                inv.quantity = float(qty_match.group(1).replace(',', ''))
            except ValueError:
                pass

        return inv

    def parse_packing_list(self, pdf_path: str) -> ParsedPackingList:
        """Parses Packing List for consistency checks under UCP 600 Article 14."""
        text = self.extract_full_text(pdf_path)
        words = self.extract_words_with_boxes(pdf_path)
        pl = ParsedPackingList()

        # Gross Weight
        weight_match = re.search(r'(?:GROSS\s*WEIGHT|TOTAL\s*GROSS\s*WEIGHT)[\s:]*([\d,.]+)\s*(?:KG|KGS)?', text, re.I)
        if weight_match:
            try:
                pl.gross_weight_kg = float(weight_match.group(1).replace(',', ''))
            except ValueError:
                pass
            box = self.find_bounding_box_for_pattern(words, r'GROSS|WEIGHT')
            if box: pl.bounding_boxes.append(box)

        # Packages
        pkg_match = re.search(r'(?:TOTAL\s*PACKAGES|TOTAL\s*CRATES|NUMBER\s*OF\s*PACKAGES)[\s:]*(\d+)', text, re.I)
        if pkg_match:
            try:
                pl.total_packages = int(pkg_match.group(1))
            except ValueError:
                pass

        return pl

    def parse_insurance_certificate(self, pdf_path: str) -> ParsedInsuranceCertificate:
        """Parses Insurance Certificate under UCP 600 Article 28."""
        text = self.extract_full_text(pdf_path)
        words = self.extract_words_with_boxes(pdf_path)
        ins = ParsedInsuranceCertificate()

        # Insured amount
        ins_match = re.search(r'(?:INSURED\s*AMOUNT|SUM\s*INSURED)[\s:]*([A-Z]{3})?\s*[\$€¥]?\s*([\d,]+\.?\d*)', text, re.I)
        if ins_match:
            ins.insured_currency = ins_match.group(1) or "USD"
            try:
                ins.insured_amount = float(ins_match.group(2).replace(',', ''))
            except ValueError:
                pass
            box = self.find_bounding_box_for_pattern(words, r'INSURED|\d{4,}')
            if box: ins.bounding_boxes.append(box)

        return ins
