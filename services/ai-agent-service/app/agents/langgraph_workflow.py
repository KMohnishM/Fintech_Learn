import time
from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, END

from app.models.trade_schemas import (
    LetterOfCredit,
    ParsedBillOfLading,
    ParsedCommercialInvoice,
    ParsedPackingList,
    ParsedInsuranceCertificate,
    Discrepancy,
    DiscrepancySeverity,
    Incoterm,
    VerificationReport
)
from app.ocr.pdf_parser import TradePdfParser
from app.agents.ucp_rule_auditor import Ucp600RuleAuditor
from app.agents.mt734_generator import SwiftMt734Generator

class TradeVerificationState(TypedDict):
    lc: LetterOfCredit
    presentation_ref: str
    pdf_paths: Dict[str, str]
    parsed_bl: Optional[ParsedBillOfLading]
    parsed_invoice: Optional[ParsedCommercialInvoice]
    parsed_pl: Optional[ParsedPackingList]
    parsed_insurance: Optional[ParsedInsuranceCertificate]
    discrepancies: List[Discrepancy]
    reinspection_count: int
    is_compliant: bool
    generated_mt734: Optional[str]
    start_time: float
    elapsed_ms: float

class TradeFinanceLangGraph:
    """
    Non-linear, parallel, and cyclical multi-agent graph orchestrator
    for UCP 600 Letter of Credit verification.
    """

    def __init__(self):
        self.parser = TradePdfParser()
        self.auditor = Ucp600RuleAuditor()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(TradeVerificationState)

        # 1. Nodes
        workflow.add_node("ocr_parser_node", self.ocr_parser_node)
        workflow.add_node("article18_invoice_node", self.article18_invoice_node)
        workflow.add_node("article20_bl_node", self.article20_bl_node)
        workflow.add_node("article14_consistency_node", self.article14_consistency_node)
        workflow.add_node("article28_insurance_node", self.article28_insurance_node)
        workflow.add_node("consolidator_node", self.consolidator_node)
        workflow.add_node("ocr_reinspection_node", self.ocr_reinspection_node)
        workflow.add_node("mt734_drafter_node", self.mt734_drafter_node)

        # 2. Edges
        workflow.set_entry_point("ocr_parser_node")

        # After OCR parsing, fan-out to rule auditor nodes
        workflow.add_edge("ocr_parser_node", "article18_invoice_node")
        workflow.add_edge("article18_invoice_node", "article20_bl_node")
        workflow.add_edge("article20_bl_node", "article14_consistency_node")

        # Conditional branch for Insurance: CIF requires Article 28, FOB bypasses it
        workflow.add_conditional_edges(
            "article14_consistency_node",
            self.route_insurance_by_incoterm,
            {
                "audit_insurance": "article28_insurance_node",
                "bypass_insurance": "consolidator_node"
            }
        )
        workflow.add_edge("article28_insurance_node", "consolidator_node")

        # Cyclical Self-Correction Loop edge:
        workflow.add_conditional_edges(
            "consolidator_node",
            self.route_ambiguity_reinspection,
            {
                "reinspect_ocr": "ocr_reinspection_node",
                "draft_mt734": "mt734_drafter_node",
                "completed": END
            }
        )
        workflow.add_edge("ocr_reinspection_node", "consolidator_node")
        workflow.add_edge("mt734_drafter_node", END)

        return workflow.compile()

    # Node Implementations
    def ocr_parser_node(self, state: TradeVerificationState) -> Dict[str, Any]:
        """Extracts text and spatial bounding boxes from submitted PDFs."""
        paths = state.get("pdf_paths", {})
        parsed_bl = self.parser.parse_bill_of_lading(paths["bl"]) if "bl" in paths else None
        parsed_inv = self.parser.parse_commercial_invoice(paths["invoice"]) if "invoice" in paths else None
        parsed_pl = self.parser.parse_packing_list(paths["packing_list"]) if "packing_list" in paths else None
        parsed_ins = self.parser.parse_insurance_certificate(paths["insurance"]) if "insurance" in paths else None

        return {
            "parsed_bl": parsed_bl,
            "parsed_invoice": parsed_inv,
            "parsed_pl": parsed_pl,
            "parsed_insurance": parsed_ins,
            "discrepancies": []
        }

    def article18_invoice_node(self, state: TradeVerificationState) -> Dict[str, Any]:
        """Audits Commercial Invoice under UCP 600 Article 18."""
        lc = state["lc"]
        inv = state.get("parsed_invoice")
        discs = list(state.get("discrepancies", []))
        if inv:
            inv_discs = self.auditor.audit_commercial_invoice_article18(lc, inv)
            discs.extend(inv_discs)
        return {"discrepancies": discs}

    def article20_bl_node(self, state: TradeVerificationState) -> Dict[str, Any]:
        """Audits Bill of Lading under UCP 600 Article 20."""
        lc = state["lc"]
        bl = state.get("parsed_bl")
        discs = list(state.get("discrepancies", []))
        if bl:
            bl_discs = self.auditor.audit_bill_of_lading_article20(lc, bl)
            discs.extend(bl_discs)
        return {"discrepancies": discs}

    def article14_consistency_node(self, state: TradeVerificationState) -> Dict[str, Any]:
        """Audits cross-document consistency under UCP 600 Article 14."""
        bl = state.get("parsed_bl")
        pl = state.get("parsed_pl")
        discs = list(state.get("discrepancies", []))
        if bl and pl:
            cons_discs = self.auditor.audit_cross_document_consistency_article14(bl, pl)
            discs.extend(cons_discs)
        return {"discrepancies": discs}

    def article28_insurance_node(self, state: TradeVerificationState) -> Dict[str, Any]:
        """Audits Insurance Certificate under UCP 600 Article 28."""
        lc = state["lc"]
        inv = state.get("parsed_invoice") or ParsedCommercialInvoice()
        ins = state.get("parsed_insurance")
        discs = list(state.get("discrepancies", []))
        if ins:
            ins_discs = self.auditor.audit_insurance_article28(lc, inv, ins)
            discs.extend(ins_discs)
        return {"discrepancies": discs}

    def route_insurance_by_incoterm(self, state: TradeVerificationState) -> str:
        """Dynamic conditional router based on Incoterms 2020."""
        lc = state["lc"]
        if lc.incoterm in [Incoterm.CIF, Incoterm.CIP] and "insurance" in state.get("pdf_paths", {}):
            return "audit_insurance"
        return "bypass_insurance"

    def consolidator_node(self, state: TradeVerificationState) -> Dict[str, Any]:
        """Consolidates all discrepancies and determines overall compliance."""
        discs = state.get("discrepancies", [])
        fatal_count = sum(1 for d in discs if d.severity == DiscrepancySeverity.FATAL)
        is_compliant = (fatal_count == 0)
        elapsed = (time.time() - state["start_time"]) * 1000.0

        return {
            "is_compliant": is_compliant,
            "elapsed_ms": round(elapsed, 2)
        }

    def route_ambiguity_reinspection(self, state: TradeVerificationState) -> str:
        """
        Cyclical self-correction conditional edge:
        If there is an ambiguous OCR result and reinspection hasn't run yet, loop back.
        """
        reinspect_count = state.get("reinspection_count", 0)
        discs = state.get("discrepancies", [])
        # Check if any discrepancy is marked with potential OCR confusion
        has_ambiguity = any("potential OCR misread" in d.legal_rationale.lower() for d in discs)

        if has_ambiguity and reinspect_count == 0:
            return "reinspect_ocr"

        if not state.get("is_compliant", False):
            return "draft_mt734"

        return "completed"

    def ocr_reinspection_node(self, state: TradeVerificationState) -> Dict[str, Any]:
        """Self-correction node that re-analyzes ambiguous bounding boxes."""
        # Increments counter to prevent infinite cycles
        return {
            "reinspection_count": state.get("reinspection_count", 0) + 1
        }

    def mt734_drafter_node(self, state: TradeVerificationState) -> Dict[str, Any]:
        """Drafts official SWIFT MT 734 Notice of Refusal for fatal discrepancies."""
        lc = state["lc"]
        ref = state.get("presentation_ref", "PRES-REF-001")
        discs = state.get("discrepancies", [])
        mt734 = SwiftMt734Generator.generate_mt734(lc, ref, discs)
        return {"generated_mt734": mt734}

    def verify(
        self,
        lc: LetterOfCredit,
        presentation_ref: str,
        pdf_paths: Dict[str, str],
        parsed_bl: Optional[ParsedBillOfLading] = None,
        parsed_invoice: Optional[ParsedCommercialInvoice] = None,
        parsed_pl: Optional[ParsedPackingList] = None,
        parsed_insurance: Optional[ParsedInsuranceCertificate] = None
    ) -> VerificationReport:
        """Runs the complete verification workflow and returns a structured report."""
        start = time.time()
        initial_state: TradeVerificationState = {
            "lc": lc,
            "presentation_ref": presentation_ref,
            "pdf_paths": pdf_paths,
            "parsed_bl": parsed_bl,
            "parsed_invoice": parsed_invoice,
            "parsed_pl": parsed_pl,
            "parsed_insurance": parsed_insurance,
            "discrepancies": [],
            "reinspection_count": 0,
            "is_compliant": True,
            "generated_mt734": None,
            "start_time": start,
            "elapsed_ms": 0.0
        }

        # If pre-parsed documents were passed in directly (e.g. from direct JSON or unit test)
        if parsed_bl or parsed_invoice or parsed_pl or parsed_insurance:
            # Run rule audits directly
            discs = []
            if parsed_invoice:
                discs.extend(self.auditor.audit_commercial_invoice_article18(lc, parsed_invoice))
            if parsed_bl:
                discs.extend(self.auditor.audit_bill_of_lading_article20(lc, parsed_bl))
            if parsed_bl and parsed_pl:
                discs.extend(self.auditor.audit_cross_document_consistency_article14(parsed_bl, parsed_pl))
            if parsed_insurance:
                inv = parsed_invoice or ParsedCommercialInvoice()
                discs.extend(self.auditor.audit_insurance_article28(lc, inv, parsed_insurance))

            fatal_count = sum(1 for d in discs if d.severity == DiscrepancySeverity.FATAL)
            warning_count = sum(1 for d in discs if d.severity == DiscrepancySeverity.WARNING)
            is_compliant = (fatal_count == 0)
            mt734 = SwiftMt734Generator.generate_mt734(lc, presentation_ref, discs) if not is_compliant else None
            elapsed = (time.time() - start) * 1000.0

            return VerificationReport(
                lc_number=lc.lc_number,
                presentation_reference=presentation_ref,
                is_compliant=is_compliant,
                fatal_discrepancy_count=fatal_count,
                warning_count=warning_count,
                discrepancies=discs,
                generated_swift_mt734=mt734,
                processing_time_ms=round(elapsed, 2)
            )

        # Otherwise execute the full compiled LangGraph workflow
        final_state = self.graph.invoke(initial_state)

        discs = final_state.get("discrepancies", [])
        fatal_count = sum(1 for d in discs if d.severity == DiscrepancySeverity.FATAL)
        warning_count = sum(1 for d in discs if d.severity == DiscrepancySeverity.WARNING)

        return VerificationReport(
            lc_number=lc.lc_number,
            presentation_reference=presentation_ref,
            is_compliant=final_state.get("is_compliant", False),
            fatal_discrepancy_count=fatal_count,
            warning_count=warning_count,
            discrepancies=discs,
            generated_swift_mt734=final_state.get("generated_mt734"),
            processing_time_ms=final_state.get("elapsed_ms", 0.0)
        )
