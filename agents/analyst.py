"""
agents/analyst.py — Analyst Agent

Synthesizes raw research results into structured key insights.
Identifies patterns, contradictions, and high-value findings.
"""

import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from rich.console import Console

console = Console()

SYSTEM_PROMPT = """You are a senior research analyst. You receive raw research findings from multiple web searches and your job is to:

1. Identify the most important and reliable insights
2. Spot patterns, trends, and contradictions
3. Highlight surprising or counterintuitive findings
4. Flag any gaps in the research

Be concise but thorough. Structure your analysis clearly with sections.
Focus on insight quality over quantity.
"""


def analyst_node(state: dict) -> dict:
    console.print("[bold blue]📊 Analyst:[/bold blue] Synthesizing findings...")

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
    )

    # Format research for the analyst
    research_text = ""
    for i, item in enumerate(state["research"], 1):
        research_text += f"\n## Sub-task {i}: {item['sub_task']}\n"
        research_text += f"**Answer:** {item['answer']}\n"
        for j, src in enumerate(item["sources"], 1):
            research_text += f"\n**Source {j}:** {src['title']}\n{src['content']}\n"

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=(
            f"Original query: {state['query']}\n\n"
            f"Research findings:\n{research_text}"
        ))
    ]

    response = llm.invoke(messages)
    console.print("[dim]  → Analysis complete[/dim]")

    return {**state, "analysis": response.content}
