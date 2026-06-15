"""
agents/writer.py — Writer Agent

Produces a final structured report in Markdown format
from the analyst's synthesis. Includes citations.
"""

import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from rich.console import Console

console = Console()

SYSTEM_PROMPT = """You are an expert technical writer. Your job is to produce a clear, well-structured research report in Markdown format.

The report must include:
1. **Executive Summary** — 3-5 sentence overview
2. **Key Findings** — bullet points of the most important insights
3. **Detailed Analysis** — structured prose with headers per theme
4. **Sources** — list of URLs cited
5. **Gaps & Next Steps** — what is still unknown and what to investigate next

Write for a technically sophisticated audience. Be precise, avoid fluff, and cite sources inline where possible.
"""


def writer_node(state: dict) -> dict:
    console.print("[bold blue]✍  Writer:[/bold blue] Producing final report...")

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.4,
    )

    # Collect all source URLs
    all_sources = []
    for item in state["research"]:
        for src in item["sources"]:
            if src["url"]:
                all_sources.append(f"- [{src['title']}]({src['url']})")

    sources_text = "\n".join(all_sources) if all_sources else "No sources available."

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=(
            f"Original query: {state['query']}\n\n"
            f"Research plan:\n" +
            "\n".join(f"- {p}" for p in state["plan"]) +
            f"\n\nAnalyst synthesis:\n{state['analysis']}\n\n"
            f"Available sources:\n{sources_text}"
        ))
    ]

    response = llm.invoke(messages)
    console.print("[dim]  → Report written[/dim]")

    return {**state, "report": response.content}
