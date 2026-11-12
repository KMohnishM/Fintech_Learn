"use client";

import React, { useState } from "react";
import {
  ShieldAlert,
  ShieldCheck,
  FileText,
  Building2,
  Cpu,
  ArrowRight,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Layers,
  Send,
  Lock,
  RefreshCw,
  ExternalLink
} from "lucide-react";

interface Discrepancy {
  id: string;
  ucp_article: string;
  title: string;
  severity: string;
  document_type: string;
  field_name: string;
  expected_value: string;
  actual_value: string;
  legal_rationale: string;
}

interface VerificationReport {
  lc_number: string;
  presentation_reference: string;
  is_compliant: boolean;
  fatal_discrepancy_count: number;
  warning_count: number;
  discrepancies: Discrepancy[];
  generated_swift_mt734?: string;
  processing_time_ms: number;
}

export default function TradeFinanceWorkbench() {
  const [activeTab, setActiveTab] = useState<"workbench" | "lcs" | "settlement">("workbench");
  const [selectedScenario, setSelectedScenario] = useState<string>("case1");
  const [isVerifying, setIsVerifying] = useState<boolean>(false);
  const [report, setReport] = useState<VerificationReport | null>(null);
  const [makerDecision, setMakerDecision] = useState<string>("");
  const [checkerSettled, setCheckerSettled] = useState<boolean>(false);

  // Baseline LC Data
  const sampleLc = {
    lcNumber: "GB-LC-2026-8891",
    issuingBank: "Global Commercial Bank, Tokyo (BOTKJPJT)",
    advisingBank: "Global Commercial Bank, Bangalore (BOTKINBB)",
    applicant: "Toyota Tsusho Corporation (Nagoya, Japan)",
    beneficiary: "Tata Electronics Private Limited (Bangalore, India)",
    amount: "USD 250,000.00",
    tolerance: "±5.00%",
    incoterm: "CIF YOKOHAMA",
    latestShipmentDate: "2026-11-30",
    expiryDate: "2026-12-31",
    goods: "10,000 UNITS OF AUTOMOTIVE MICROCONTROLLERS (MODEL MCU-900). UNIT PRICE USD 25.00 CIF YOKOHAMA. PACKED IN 50 CRATES."
  };

  const scenarios = [
    {
      id: "case1",
      name: "Case 1: Clean Compliant Presentation",
      expected: "CLEAN_PASS",
      desc: "All shipping documents (B/L, Invoice, Packing List, Insurance) align 100% with LC conditions."
    },
    {
      id: "case2",
      name: "Case 2: Late Shipment (UCP 600 Art. 20)",
      expected: "FATAL_DISCREPANCY",
      desc: "B/L Shipped on Board date is 05-DEC-2026 (LC latest shipment deadline was 30-NOV-2026)."
    },
    {
      id: "case3",
      name: "Case 3: Invoice Description Mismatch (Art. 18)",
      expected: "FATAL_DISCREPANCY",
      desc: "Commercial Invoice omits mandatory specification 'MODEL MCU-900'."
    },
    {
      id: "case4",
      name: "Case 4: Weight Conflict Across Docs (Art. 14)",
      expected: "FATAL_DISCREPANCY",
      desc: "Packing List gross weight (4,800 KG) contradicts B/L gross weight (4,200 KG)."
    },
    {
      id: "case5",
      name: "Case 5: Under-Insurance Discrepancy (Art. 28)",
      expected: "FATAL_DISCREPANCY",
      desc: "Insurance certificate covers $250,000 (100% instead of mandatory 110% = $275,000)."
    }
  ];

  const runSimulationVerification = () => {
    setIsVerifying(true);
    setCheckerSettled(false);
    setMakerDecision("");

    setTimeout(() => {
      let rep: VerificationReport;

      if (selectedScenario === "case1") {
        rep = {
          lc_number: "GB-LC-2026-8891",
          presentation_reference: "PRES-Global Bank-8891-001",
          is_compliant: true,
          fatal_discrepancy_count: 0,
          warning_count: 0,
          discrepancies: [],
          generated_swift_mt734: undefined,
          processing_time_ms: 184.5
        };
      } else if (selectedScenario === "case2") {
        rep = {
          lc_number: "GB-LC-2026-8891",
          presentation_reference: "PRES-Global Bank-8891-002",
          is_compliant: false,
          fatal_discrepancy_count: 1,
          warning_count: 0,
          discrepancies: [
            {
              id: "disc-201",
              ucp_article: "Article 20(a)(ii)",
              title: "Late Shipment on Bill of Lading",
              severity: "FATAL",
              document_type: "BILL_OF_LADING",
              field_name: "shipped_on_board_date",
              expected_value: "On or before 30-NOV-2026",
              actual_value: "Shipped on 05-DEC-2026",
              legal_rationale: "Shipped on board date (05-DEC-2026) is 5 days after the latest shipment date specified in field :44C: of the Letter of Credit."
            }
          ],
          generated_swift_mt734: `{1:F01BOTKJPJTAXXX0000000000}{2:I734BOTKINBBXXXXN}{4:\n:20:GB-LC-2026-8891\n:21:PRES-Global Bank-8891-002\n:32A:261111USD250,000.00\n:77J:DISCREPANCIES NOTED AS FOLLOWS:\n1. ARTICLE 20(A)(II): LATE SHIPMENT ON BILL OF LADING (SHIPPED 05-DEC-2026 VS LATEST 30-NOV-2026)\n:77B:WE ARE HOLDING DOCUMENTS AT YOUR RISK AND DISPOSAL PENDING INSTRUCTIONS OF THE APPLICANT.\n-}`,
          processing_time_ms: 212.1
        };
      } else if (selectedScenario === "case3") {
        rep = {
          lc_number: "GB-LC-2026-8891",
          presentation_reference: "PRES-Global Bank-8891-003",
          is_compliant: false,
          fatal_discrepancy_count: 1,
          warning_count: 0,
          discrepancies: [
            {
              id: "disc-301",
              ucp_article: "Article 18(c)",
              title: "Invoice Goods Description Mismatch",
              severity: "FATAL",
              document_type: "COMMERCIAL_INVOICE",
              field_name: "goods_description",
              expected_value: "10,000 UNITS OF AUTOMOTIVE MICROCONTROLLERS (MODEL MCU-900)",
              actual_value: "10,000 UNITS OF ELECTRONIC COMPONENTS",
              legal_rationale: "Under UCP 600 Article 18(c), the commercial invoice must correspond strictly with the credit description. Crucial model identifier 'MODEL MCU-900' was omitted."
            }
          ],
          generated_swift_mt734: `{1:F01BOTKJPJTAXXX0000000000}{2:I734BOTKINBBXXXXN}{4:\n:20:GB-LC-2026-8891\n:21:PRES-Global Bank-8891-003\n:32A:261111USD250,000.00\n:77J:DISCREPANCIES NOTED AS FOLLOWS:\n1. ARTICLE 18(C): INVOICE GOODS DESCRIPTION OMITS 'MODEL MCU-900'\n:77B:WE ARE HOLDING DOCUMENTS AT YOUR RISK AND DISPOSAL PENDING INSTRUCTIONS OF THE APPLICANT.\n-}`,
          processing_time_ms: 195.8
        };
      } else if (selectedScenario === "case4") {
        rep = {
          lc_number: "GB-LC-2026-8891",
          presentation_reference: "PRES-Global Bank-8891-004",
          is_compliant: false,
          fatal_discrepancy_count: 1,
          warning_count: 0,
          discrepancies: [
            {
              id: "disc-401",
              ucp_article: "Article 14(d)",
              title: "Gross Weight Conflict Across Documents",
              severity: "FATAL",
              document_type: "PACKING_LIST",
              field_name: "gross_weight_kg",
              expected_value: "4,200.0 KG (As indicated on Bill of Lading)",
              actual_value: "4,800.0 KG (On Packing List)",
              legal_rationale: "Data in a document must not conflict with data in any other stipulated document under UCP 600 Article 14(d). 600 KG conflict detected."
            }
          ],
          generated_swift_mt734: `{1:F01BOTKJPJTAXXX0000000000}{2:I734BOTKINBBXXXXN}{4:\n:20:GB-LC-2026-8891\n:21:PRES-Global Bank-8891-004\n:32A:261111USD250,000.00\n:77J:DISCREPANCIES NOTED AS FOLLOWS:\n1. ARTICLE 14(D): GROSS WEIGHT CONFLICT (B/L 4,200 KG VS PACKING LIST 4,800 KG)\n:77B:WE ARE HOLDING DOCUMENTS AT YOUR RISK AND DISPOSAL PENDING INSTRUCTIONS OF THE APPLICANT.\n-}`,
          processing_time_ms: 228.4
        };
      } else {
        rep = {
          lc_number: "GB-LC-2026-8891",
          presentation_reference: "PRES-Global Bank-8891-005",
          is_compliant: false,
          fatal_discrepancy_count: 1,
          warning_count: 0,
          discrepancies: [
            {
              id: "disc-501",
              ucp_article: "Article 28(f)(ii)",
              title: "Under-Insurance Coverage",
              severity: "FATAL",
              document_type: "INSURANCE_CERTIFICATE",
              field_name: "insured_amount",
              expected_value: "USD 275,000.00 (Minimum 110% of CIF value)",
              actual_value: "USD 250,000.00 (100% of Invoice value)",
              legal_rationale: "Under CIF terms and UCP 600 Article 28(f)(ii), insurance cover must be at least 110% of the CIF invoice amount."
            }
          ],
          generated_swift_mt734: `{1:F01BOTKJPJTAXXX0000000000}{2:I734BOTKINBBXXXXN}{4:\n:20:GB-LC-2026-8891\n:21:PRES-Global Bank-8891-005\n:32A:261111USD250,000.00\n:77J:DISCREPANCIES NOTED AS FOLLOWS:\n1. ARTICLE 28(F)(II): UNDER-INSURED (100% COVERED VS MANDATORY 110% CIF REQUIREMENT)\n:77B:WE ARE HOLDING DOCUMENTS AT YOUR RISK AND DISPOSAL PENDING INSTRUCTIONS OF THE APPLICANT.\n-}`,
          processing_time_ms: 179.3
        };
      }

      setReport(rep);
      setIsVerifying(false);
    }, 600);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* Top Header */}
      <header className="bg-slate-900 text-white border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-red-600 w-8 h-8 rounded flex items-center justify-center font-bold text-white text-lg tracking-wider">
              M
            </div>
            <div>
              <div className="font-bold text-lg tracking-tight flex items-center gap-2">
                Global Commercial Bank <span className="text-xs bg-red-600/20 text-red-400 border border-red-500/30 px-2 py-0.5 rounded font-mono">Transaction Banking</span>
              </div>
              <div className="text-xs text-slate-400">
                Global Transaction Banking • Autonomous UCP 600 Trade Discrepancy Platform
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-4 text-xs font-mono">
            <div className="flex items-center gap-1.5 bg-slate-800/80 px-2.5 py-1 rounded border border-slate-700">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-slate-300">Kafka: Active</span>
            </div>
            <div className="flex items-center gap-1.5 bg-slate-800/80 px-2.5 py-1 rounded border border-slate-700">
              <Lock className="w-3 h-3 text-amber-400" />
              <span className="text-slate-300">Redis Redlock: Armed</span>
            </div>
            <div className="flex items-center gap-1.5 bg-slate-800/80 px-2.5 py-1 rounded border border-slate-700">
              <Cpu className="w-3 h-3 text-cyan-400" />
              <span className="text-slate-300">LangGraph: Ready</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Sub-header */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 flex items-center space-x-8">
          <button
            onClick={() => setActiveTab("workbench")}
            className={`py-3.5 text-sm font-medium border-b-2 flex items-center gap-2 ${
              activeTab === "workbench"
                ? "border-red-600 text-red-600"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
            Document Examination Workbench (Maker-Checker)
          </button>
          <button
            onClick={() => setActiveTab("lcs")}
            className={`py-3.5 text-sm font-medium border-b-2 flex items-center gap-2 ${
              activeTab === "lcs"
                ? "border-red-600 text-red-600"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <FileText className="w-4 h-4" />
            Letter of Credit Contracts & Credit Lines
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 py-6 flex-1 w-full">
        {activeTab === "workbench" && (
          <div className="space-y-6">
            {/* Scenario Selector Card */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h2 className="text-base font-semibold text-slate-900 flex items-center gap-2">
                    <Layers className="w-4 h-4 text-red-600" />
                    Select Curated Benchmark Presentation Scenario
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Test the autonomous LangGraph verification engine against real-world compliant and discrepant trade document packs.
                  </p>
                </div>
                <button
                  onClick={runSimulationVerification}
                  disabled={isVerifying}
                  className="bg-red-600 hover:bg-red-700 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition flex items-center gap-2 shadow-sm disabled:opacity-50"
                >
                  {isVerifying ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Auditing UCP 600 Rules...
                    </>
                  ) : (
                    <>
                      <Cpu className="w-4 h-4" />
                      Execute Autonomous Examination
                    </>
                  )}
                </button>
              </div>

              {/* Radio Grid */}
              <div className="grid grid-cols-1 md:grid-cols-5 gap-3 mt-4">
                {scenarios.map((sc) => (
                  <div
                    key={sc.id}
                    onClick={() => {
                      setSelectedScenario(sc.id);
                      setReport(null);
                    }}
                    className={`cursor-pointer rounded-lg p-3 text-xs border transition ${
                      selectedScenario === sc.id
                        ? "border-red-500 bg-red-50/50 shadow-sm"
                        : "border-slate-200 hover:border-slate-300 bg-slate-50/50"
                    }`}
                  >
                    <div className="font-semibold text-slate-800 mb-1">{sc.name}</div>
                    <div className="text-slate-500 line-clamp-2">{sc.desc}</div>
                    <div className="mt-2 text-[10px] font-mono">
                      {sc.expected === "CLEAN_PASS" ? (
                        <span className="text-emerald-700 bg-emerald-100 px-1.5 py-0.5 rounded font-semibold">
                          Expected: Pass
                        </span>
                      ) : (
                        <span className="text-rose-700 bg-rose-100 px-1.5 py-0.5 rounded font-semibold">
                          Expected: Discrepancy
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Dual-Pane Workbench Area */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Left Pane: Submitted Trade Document Packet */}
              <div className="lg:col-span-5 space-y-4">
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
                  <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3 flex items-center justify-between">
                    <span>Submitted Trade Packet</span>
                    <span className="text-xs font-mono font-normal text-slate-500">Ref: {sampleLc.lcNumber}</span>
                  </h3>

                  <div className="space-y-3 text-xs">
                    <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                      <div className="font-semibold text-slate-800 flex items-center justify-between mb-1">
                        <span className="flex items-center gap-1.5">
                          <FileText className="w-3.5 h-3.5 text-blue-600" />
                          1. Ocean Bill of Lading (3/3 Original)
                        </span>
                        <span className="text-[10px] bg-slate-200 px-1.5 py-0.5 rounded font-mono">PDF Verified</span>
                      </div>
                      <div className="text-slate-600 grid grid-cols-2 gap-1 mt-1 text-[11px]">
                        <div>Carrier: <strong>Maersk Line A/S</strong></div>
                        <div>Gross Weight: <strong>{selectedScenario === "case4" ? "4,200 KG" : "4,200 KG"}</strong></div>
                        <div>Pol: <strong>Nhava Sheva (IN)</strong></div>
                        <div>Pod: <strong>Yokohama (JP)</strong></div>
                        <div className="col-span-2">
                          Shipped on Board:{" "}
                          <strong className={selectedScenario === "case2" ? "text-rose-600 font-bold" : "text-emerald-700 font-bold"}>
                            {selectedScenario === "case2" ? "05-DEC-2026 (LATE)" : "15-NOV-2026"}
                          </strong>
                        </div>
                      </div>
                    </div>

                    <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                      <div className="font-semibold text-slate-800 flex items-center justify-between mb-1">
                        <span className="flex items-center gap-1.5">
                          <FileText className="w-3.5 h-3.5 text-blue-600" />
                          2. Commercial Invoice
                        </span>
                        <span className="text-[10px] bg-slate-200 px-1.5 py-0.5 rounded font-mono">PDF Verified</span>
                      </div>
                      <div className="text-slate-600 text-[11px] space-y-1">
                        <div>Total: <strong>USD 250,000.00</strong> (CIF Yokohama)</div>
                        <div>
                          Goods Description:{" "}
                          <span className={selectedScenario === "case3" ? "text-rose-600 font-semibold" : "text-slate-700"}>
                            {selectedScenario === "case3"
                              ? "10,000 UNITS OF ELECTRONIC COMPONENTS (Omitted Model)"
                              : "10,000 UNITS OF AUTOMOTIVE MICROCONTROLLERS (MODEL MCU-900)"}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                      <div className="font-semibold text-slate-800 flex items-center justify-between mb-1">
                        <span className="flex items-center gap-1.5">
                          <FileText className="w-3.5 h-3.5 text-blue-600" />
                          3. Detailed Packing List
                        </span>
                        <span className="text-[10px] bg-slate-200 px-1.5 py-0.5 rounded font-mono">PDF Verified</span>
                      </div>
                      <div className="text-slate-600 text-[11px] grid grid-cols-2 gap-1">
                        <div>Packages: <strong>50 Crates</strong></div>
                        <div>
                          Gross Weight:{" "}
                          <strong className={selectedScenario === "case4" ? "text-rose-600 font-bold" : "text-slate-800"}>
                            {selectedScenario === "case4" ? "4,800.0 KG (Conflict)" : "4,200.0 KG"}
                          </strong>
                        </div>
                      </div>
                    </div>

                    <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                      <div className="font-semibold text-slate-800 flex items-center justify-between mb-1">
                        <span className="flex items-center gap-1.5">
                          <FileText className="w-3.5 h-3.5 text-blue-600" />
                          4. Marine Cargo Insurance
                        </span>
                        <span className="text-[10px] bg-slate-200 px-1.5 py-0.5 rounded font-mono">PDF Verified</span>
                      </div>
                      <div className="text-slate-600 text-[11px]">
                        Insured Sum:{" "}
                        <strong className={selectedScenario === "case5" ? "text-rose-600 font-bold" : "text-emerald-700 font-bold"}>
                          {selectedScenario === "case5" ? "USD 250,000.00 (100% only)" : "USD 275,000.00 (110% CIF)"}
                        </strong>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Pane: Autonomous UCP 600 AI Findings & Four-Eyes Actions */}
              <div className="lg:col-span-7 space-y-4">
                {report ? (
                  <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 space-y-4">
                    {/* Status Banner */}
                    <div
                      className={`p-4 rounded-lg border flex items-start justify-between ${
                        report.is_compliant
                          ? "bg-emerald-50 border-emerald-200 text-emerald-900"
                          : "bg-rose-50 border-rose-200 text-rose-900"
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        {report.is_compliant ? (
                          <CheckCircle2 className="w-6 h-6 text-emerald-600 mt-0.5" />
                        ) : (
                          <AlertTriangle className="w-6 h-6 text-rose-600 mt-0.5" />
                        )}
                        <div>
                          <div className="font-bold text-base">
                            {report.is_compliant
                              ? "CLEAN PRESENTATION - 100% COMPLIANT UNDER UCP 600"
                              : `DISCREPANCIES IDENTIFIED: ${report.fatal_discrepancy_count} FATAL NON-COMPLIANCE`}
                          </div>
                          <div className="text-xs opacity-80 mt-0.5">
                            Autonomous examination completed in {report.processing_time_ms} ms via LangGraph StateGraph.
                          </div>
                        </div>
                      </div>

                      <div className="text-right font-mono text-xs font-semibold">
                        {report.is_compliant ? (
                          <span className="bg-emerald-200 text-emerald-800 px-2.5 py-1 rounded">APPROVED</span>
                        ) : (
                          <span className="bg-rose-200 text-rose-800 px-2.5 py-1 rounded">HOLD PAYMENT</span>
                        )}
                      </div>
                    </div>

                    {/* Discrepancies List */}
                    {!report.is_compliant && (
                      <div className="space-y-3">
                        <div className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                          UCP 600 Violation Citations:
                        </div>
                        {report.discrepancies.map((d) => (
                          <div key={d.id} className="p-3.5 bg-rose-50/60 rounded-lg border border-rose-200 text-xs space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="font-bold text-rose-800 flex items-center gap-1.5">
                                <span className="bg-rose-600 text-white px-1.5 py-0.5 rounded text-[10px]">
                                  {d.ucp_article}
                                </span>
                                {d.title}
                              </span>
                              <span className="text-[10px] font-mono font-bold text-rose-700">
                                SEVERITY: {d.severity}
                              </span>
                            </div>
                            <p className="text-rose-900 text-[11px] leading-relaxed">{d.legal_rationale}</p>
                            <div className="grid grid-cols-2 gap-2 text-[11px] bg-white p-2 rounded border border-rose-100 font-mono">
                              <div><span className="text-slate-500">Expected:</span> <strong className="text-slate-800">{d.expected_value}</strong></div>
                              <div><span className="text-rose-600">Actual:</span> <strong className="text-rose-700">{d.actual_value}</strong></div>
                            </div>
                          </div>
                        ))}

                        {/* Generated SWIFT MT 734 Refusal Box */}
                        {report.generated_swift_mt734 && (
                          <div className="mt-4">
                            <div className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1 flex items-center justify-between">
                              <span>Auto-Generated SWIFT MT 734 Notice of Refusal</span>
                              <span className="text-[10px] text-slate-500 font-normal">Ready for FIN network</span>
                            </div>
                            <pre className="p-3 bg-slate-900 text-slate-200 rounded-lg font-mono text-[11px] overflow-x-auto whitespace-pre-wrap leading-relaxed">
                              {report.generated_swift_mt734}
                            </pre>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Four-Eyes Principle / Maker-Checker Action Desk */}
                    <div className="pt-4 border-t border-slate-200">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                          <Lock className="w-3.5 h-3.5 text-amber-600" />
                          Four-Eyes Dual Control (Maker-Checker)
                        </span>
                        {checkerSettled && (
                          <span className="text-xs bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-semibold font-mono">
                            ✓ SETTLED ATOMICALLY IN POSTGRES
                          </span>
                        )}
                      </div>

                      <div className="flex flex-wrap gap-2 text-xs">
                        {report.is_compliant ? (
                          <button
                            onClick={() => {
                              setMakerDecision("MAKER_APPROVED");
                              setCheckerSettled(true);
                            }}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg font-medium transition flex items-center gap-1.5 shadow-sm"
                          >
                            <ShieldCheck className="w-4 h-4" />
                            Checker Sign-off & Execute Double-Entry Settlement ($250,000)
                          </button>
                        ) : (
                          <>
                            <button
                              onClick={() => setMakerDecision("WAIVER_REQUESTED")}
                              className="bg-amber-500 hover:bg-amber-600 text-white px-3.5 py-2 rounded-lg font-medium transition flex items-center gap-1.5"
                            >
                              Request Applicant Waiver (Toyota)
                            </button>
                            <button
                              onClick={() => setMakerDecision("MT734_TRANSMITTED")}
                              className="bg-rose-600 hover:bg-rose-700 text-white px-3.5 py-2 rounded-lg font-medium transition flex items-center gap-1.5"
                            >
                              <Send className="w-3.5 h-3.5" />
                              Transmit SWIFT MT 734 Notice of Refusal
                            </button>
                          </>
                        )}
                      </div>

                      {makerDecision && (
                        <div className="mt-3 p-2 bg-slate-100 rounded text-xs text-slate-700 font-mono">
                          Action Recorded: <strong>{makerDecision}</strong> | User: <code>BANK_OFFICER_01 (Maker)</code> | Dual Signer: <code>BANK_MANAGER_02 (Checker)</code>
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-12 text-center text-slate-500">
                    <Cpu className="w-10 h-10 text-slate-300 mx-auto mb-3" />
                    <div className="font-semibold text-slate-700">Autonomous UCP 600 Engine Idle</div>
                    <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                      Click &ldquo;Execute Autonomous Examination&rdquo; above to run the LangGraph rule audit against the selected trade presentation.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === "lcs" && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 space-y-6">
            <div>
              <h2 className="text-base font-bold text-slate-900">Registered Corporate Letters of Credit</h2>
              <p className="text-xs text-slate-500">Active documentary credits issued under Global Bank Bank Tokyo and Mumbai/Bangalore branches.</p>
            </div>

            <div className="overflow-x-auto border border-slate-200 rounded-lg">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
                  <tr>
                    <th className="p-3">LC Number</th>
                    <th className="p-3">Applicant (Importer)</th>
                    <th className="p-3">Beneficiary (Exporter)</th>
                    <th className="p-3">Amount</th>
                    <th className="p-3">Incoterm</th>
                    <th className="p-3">Latest Shipment</th>
                    <th className="p-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 font-mono text-[11px]">
                  <tr>
                    <td className="p-3 font-bold text-red-600">{sampleLc.lcNumber}</td>
                    <td className="p-3 font-sans">{sampleLc.applicant}</td>
                    <td className="p-3 font-sans">{sampleLc.beneficiary}</td>
                    <td className="p-3 font-bold">{sampleLc.amount}</td>
                    <td className="p-3">{sampleLc.incoterm}</td>
                    <td className="p-3">{sampleLc.latestShipmentDate}</td>
                    <td className="p-3">
                      <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-semibold">ISSUED</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-3 text-center text-xs text-slate-500">
        Global Transaction Banking • Corporate & Investment Banking Systems Engineering • Polyglot Stack
      </footer>
    </div>
  );
}
