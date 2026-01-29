"""CrewAI orchestrator for AURIX multi-agent system."""

from typing import Dict, Any
from crewai import Crew, Task, Process
import pandas as pd

from aurix.ai.base import LLMProvider
from aurix.ai.tools import (
    set_data_context,
    get_reconciliation_summary,
    get_top_variances,
    get_coa_detail,
    get_anomalies,
    get_unmatched_entries,
    get_transaction_details,
)
from aurix.agents.recon_agent import create_recon_agent
from aurix.agents.fraud_agent import create_fraud_agent
from aurix.agents.report_agent import create_report_agent


class AurixCrew:
    """Orchestrator that coordinates the multi-agent workflow."""

    def __init__(self, api_key: str):
        self.provider = LLMProvider(api_key)
        self.llm = self.provider.llm

    def set_context(self, coa_recon, txn_detail, summary, ml_anomalies=None):
        """Load data into the shared tool data store."""
        set_data_context(coa_recon, txn_detail, summary, ml_anomalies)

    def _build_tools(self) -> list:
        return [
            get_reconciliation_summary,
            get_top_variances,
            get_coa_detail,
            get_anomalies,
            get_unmatched_entries,
            get_transaction_details,
        ]

    def run(self) -> Dict[str, Any]:
        """Execute the full multi-agent workflow."""
        try:
            tools = self._build_tools()

            recon_agent = create_recon_agent(self.llm, tools)
            fraud_agent = create_fraud_agent(self.llm, tools)
            report_agent = create_report_agent(self.llm, [get_reconciliation_summary])

            recon_task = Task(
                description=(
                    "Analyze the reconciliation results comprehensively. "
                    "1. Get the reconciliation summary. "
                    "2. Review the top 10 variances. "
                    "3. For the top 3 variance COAs, get their detailed data. "
                    "4. Check unmatched entries. "
                    "5. Provide a structured analysis covering: overall health, "
                    "key variance patterns, unmatched entry assessment, and risk areas."
                ),
                agent=recon_agent,
                expected_output=(
                    "A structured reconciliation analysis report in Bahasa Indonesia with sections: "
                    "Ringkasan, Analisis Variance Utama, Entry Tidak Cocok, Area Risiko."
                )
            )

            fraud_task = Task(
                description=(
                    "Examine the reconciliation data for fraud indicators and suspicious patterns. "
                    "1. Review all detected anomalies. "
                    "2. Check unmatched entries for suspicious amounts. "
                    "3. Analyze the top variances for manipulation patterns. "
                    "4. Look for split transaction patterns and unusual debit/credit ratios. "
                    "5. Provide a fraud risk assessment with severity levels."
                ),
                agent=fraud_agent,
                expected_output=(
                    "A fraud risk assessment in Bahasa Indonesia with sections: "
                    "Temuan Anomali, Pola Mencurigakan, Penilaian Risiko Fraud, Rekomendasi."
                )
            )

            report_task = Task(
                description=(
                    "Using the reconciliation analysis and fraud assessment from your colleagues, "
                    "create a professional audit report narrative. Include: "
                    "1. Executive Summary (3-5 sentences) "
                    "2. Key Findings (numbered list) "
                    "3. Risk Assessment Matrix (HIGH/MEDIUM/LOW items) "
                    "4. Recommendations (prioritized action items) "
                    "5. Compliance Notes (PSAK 109/AAOIFI impact)"
                ),
                agent=report_agent,
                expected_output=(
                    "A complete audit report narrative in Bahasa Indonesia, "
                    "formatted with clear section headings and professional language "
                    "suitable for the BPKH Audit Committee."
                ),
                context=[recon_task, fraud_task]
            )

            crew = Crew(
                agents=[recon_agent, fraud_agent, report_agent],
                tasks=[recon_task, fraud_task, report_task],
                process=Process.sequential,
                verbose=False
            )
            result = crew.kickoff()

            return {
                "report": str(result),
                "success": True,
                "error": None
            }
        except Exception as e:
            return {
                "report": None,
                "success": False,
                "error": str(e)
            }

    def run_single_agent(self, agent_type: str) -> str:
        """Run a single agent for targeted analysis."""
        tools = self._build_tools()

        if agent_type == "recon":
            agent = create_recon_agent(self.llm, tools)
            description = "Provide a comprehensive reconciliation analysis. Get the summary, review top variances, and check unmatched entries."
        elif agent_type == "fraud":
            agent = create_fraud_agent(self.llm, tools)
            description = "Provide a fraud risk assessment. Review anomalies, check unmatched entries, and analyze suspicious patterns."
        elif agent_type == "report":
            agent = create_report_agent(self.llm, tools)
            description = "Generate an executive audit summary. Get the reconciliation summary and create a professional report."
        else:
            return f"Unknown agent type: {agent_type}"

        task = Task(
            description=description,
            agent=agent,
            expected_output="Analysis in Bahasa Indonesia"
        )
        crew = Crew(agents=[agent], tasks=[task], verbose=False)
        result = crew.kickoff()
        return str(result)
