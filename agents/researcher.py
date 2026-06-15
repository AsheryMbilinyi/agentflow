"""
agents/researcher.py — Researcher Agent

Uses Tavily web search to gather information for each sub-task
produced by the Planner. Returns structured research results.
"""

import os
from tavily import TavilyClient
from rich.console import Console

console = Console()


def researcher_node(state: dict) -> dict:
    console.print("[bold blue]🔍 Researcher:[/bold blue] Gathering information...")

    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    research_results = []

    for i, sub_task in enumerate(state["plan"], 1):
        console.print(f"  [dim]Searching ({i}/{len(state['plan'])}): {sub_task[:60]}...[/dim]")

        try:
            result = client.search(
                query=sub_task,
                search_depth="basic",
                max_results=3,
                include_answer=True,
            )

            research_results.append({
                "sub_task": sub_task,
                "answer": result.get("answer", ""),
                "sources": [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "content": r.get("content", "")[:500],
                    }
                    for r in result.get("results", [])
                ],
            })

        except Exception as e:
            console.print(f"  [red]Search failed for sub-task {i}: {e}[/red]")
            research_results.append({
                "sub_task": sub_task,
                "answer": "Search failed.",
                "sources": [],
            })

    console.print(f"[dim]  → {len(research_results)} sub-tasks researched[/dim]")
    return {**state, "research": research_results}
