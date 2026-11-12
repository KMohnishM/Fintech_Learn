import datetime
from typing import List
from app.models.trade_schemas import LetterOfCredit, Discrepancy, DiscrepancySeverity

class SwiftMt734Generator:
    """
    Generates standard SWIFT FIN MT 734 (Advice of Refusal) message
    complying with SWIFT Standards MT and UCP 600 Article 16.
    """

    @staticmethod
    def generate_mt734(
        lc: LetterOfCredit,
        presentation_ref: str,
        discrepancies: List[Discrepancy]
    ) -> str:
        fatal_discrepancies = [d for d in discrepancies if d.severity == DiscrepancySeverity.FATAL]

        if not fatal_discrepancies:
            return ""

        today_swift = datetime.date.today().strftime("%y%m%d")

        discrepancy_lines = []
        for idx, disc in enumerate(fatal_discrepancies, 1):
            line = f"{idx}. {disc.ucp_article.upper()}: {disc.title.upper()} - {disc.legal_rationale.upper()}"
            discrepancy_lines.append(line)

        discrepancies_text = "\n".join(discrepancy_lines)

        mt734_message = f"""{{1:F01{lc.issuing_bank_bic}AXXX0000000000}}{{2:I734{lc.advising_bank_bic}XXXXN}}{{4:
:20:{lc.lc_number}
:21:{presentation_ref}
:32A:{today_swift}{lc.currency}{lc.amount:,.2f}
:77J:DISCREPANCIES NOTED AS FOLLOWS:
{discrepancies_text}
:77B:WE ARE HOLDING DOCUMENTS AT YOUR RISK AND DISPOSAL PENDING INSTRUCTIONS OF THE APPLICANT.
-}}"""
        return mt734_message.strip()
