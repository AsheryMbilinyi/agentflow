"""
agents/planner.py — Planner Agent

Breaks the user query into a list of focused research sub-tasks.
Each sub-task will be independently researched by the Researcher agent.
"""

import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from rich.console import Console

console = Console()

SYSTEM_PROMPT = """You are a research planning expert. Your job is to break down a research query into 3-5 focused, specific sub-tasks that together will comprehensively answer the query.

Each sub-task should:
- Be a specific, searchable question
- Cover a distinct aspect of the main query
- Be answerable with web search

Return ONLY a JSON array of strings. Example:
["What is X?", "How does X compare to Y?", "What are the latest trends in X?"]
"""


def planner_node(state: dict) -> dict:
    console.print("[bold blue]🧠 Planner:[/bold blue] Breaking query into sub-tasks...")

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Query: {state['query']}")
    ]

    response = llm.invoke(messages)

    try:
        # Strip markdown code fences if present
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        plan = json.loads(raw.strip())
    except Exception:
        # Fallback: split by newlines
        plan = [
            line.strip().lstrip("-•123456789. ")
            for line in response.content.split("\n")
            if line.strip()
        ][:5]

    console.print(f"[dim]  → {len(plan)} sub-tasks identified[/dim]")

    return {**state, "plan": plan}
