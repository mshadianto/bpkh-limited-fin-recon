"""Reconciliation Analysis Agent for AURIX."""

from crewai import Agent


def create_recon_agent(llm, tools: list) -> Agent:
    """Create the Reconciliation Analysis Agent."""
    return Agent(
        role="Senior Reconciliation Analyst",
        goal=(
            "Analyze reconciliation results between Daftra ERP and Manual Journal entries. "
            "Identify all significant variances, explain discrepancy patterns, "
            "and assess overall reconciliation health for BPKH audit committee."
        ),
        backstory=(
            "You are a senior financial reconciliation specialist with 15 years of experience "
            "in Islamic finance auditing at BPKH Limited (Saudi Arabia). You are expert in "
            "PSAK 109, AAOIFI standards, and OJK regulations. You analyze Daftra accounting "
            "system exports against Manual Journal entries to ensure financial integrity. "
            "You communicate findings in Bahasa Indonesia."
        ),
        llm=llm,
        tools=tools,
        verbose=False,
        allow_delegation=False,
        max_iter=5
    )
