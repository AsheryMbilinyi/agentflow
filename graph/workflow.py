"""
graph/workflow.py — LangGraph state machine

Nodes:
  planner   → breaks query into sub-tasks
  human     → checkpoint for approval (can be skipped with --auto)
  researcher → executes web search per sub-task
  analyst   → synthesizes findings into key insights
  writer    → produces final structured report

Edge logic:
  planner → human → researcher → analyst → writer → END
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from rich.console import Console
from agents.planner import planner_node
from agents.researcher import researcher_node
from agents.analyst import analyst_node
from agents.writer import writer_node

console = Console()


class AgentState(TypedDict):
    query: str
    plan: list[str]
    research: list[dict]
    analysis: str
    report: str
    approved: bool
    messages: list[dict]


def human_approval_node(state: AgentState) -> AgentState:
    """Human-in-the-loop checkpoint after planning."""
    console.print("\n[bold cyan]📋 Planner produced the following research plan:[/bold cyan]")
    for i, step in enumerate(state["plan"], 1):
        console.print(f"  [cyan]{i}.[/cyan] {step}")

    response = console.input(
        "\n[bold]Approve plan and continue? (y/n):[/bold] "
    ).strip().lower()

    if response != "y":
        console.print("[red]Plan rejected. Exiting.[/red]")
        raise SystemExit(0)

    console.print("[green]✓ Plan approved. Proceeding...[/green]\n")
    return {**state, "approved": True}


def should_run_human(state: AgentState) -> str:
    """Route to human approval or skip based on flag."""
    # auto_approve is injected via graph config
    return "human" if not state.get("_auto_approve") else "researcher"


def build_graph(auto_approve: bool = False) -> StateGraph:
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("writer", writer_node)

    if not auto_approve:
        workflow.add_node("human", human_approval_node)
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "human")
        workflow.add_edge("human", "researcher")
    else:
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "researcher")

    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", "writer")
    workflow.add_edge("writer", END)

    return workflow.compile()
