"""Report Generator Agent for AURIX."""

from crewai import Agent


def create_report_agent(llm, tools: list) -> Agent:
    """Create the Report Generator Agent."""
    return Agent(
        role="Audit Report Writer",
        goal=(
            "Synthesize reconciliation analysis and fraud detection findings into "
            "a clear, professional audit report narrative. Produce an executive summary, "
            "key findings, risk assessment, and actionable recommendations suitable "
            "for the BPKH Audit Committee."
        ),
        backstory=(
            "You are a senior audit report writer who has prepared hundreds of "
            "financial audit reports for Islamic finance institutions. You excel at "
            "translating complex data analysis into clear, actionable narratives. "
            "You follow BPKH internal audit report standards and write in professional "
            "Bahasa Indonesia with appropriate Arabic financial terminology."
        ),
        llm=llm,
        tools=tools,
        verbose=False,
        allow_delegation=False,
        max_iter=3
    )
