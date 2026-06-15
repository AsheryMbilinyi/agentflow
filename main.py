"""
AgentFlow — Multi-Agent Research Assistant
Powered by LangGraph + LangChain
"""

import argparse
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from graph.workflow import build_graph, AgentState

load_dotenv()
console = Console()


def run(query: str, auto_approve: bool = False):
    console.print(Panel.fit(
        f"[bold blue]AgentFlow[/bold blue] — Multi-Agent Research Assistant\n"
        f"[dim]Query:[/dim] {query}",
        border_style="blue"
    ))

    graph = build_graph(auto_approve=auto_approve)

    initial_state: AgentState = {
        "query": query,
        "plan": [],
        "research": [],
        "analysis": "",
        "report": "",
        "approved": False,
        "messages": [],
    }

    console.print("\n[bold yellow]⚙  Running agent pipeline...[/bold yellow]\n")

    final_state = graph.invoke(initial_state)

    console.print("\n[bold green]✅ Report complete![/bold green]\n")
    console.print(Panel(
        Markdown(final_state["report"]),
        title="[bold]Final Report[/bold]",
        border_style="green"
    ))

    # Save output
    with open("examples/sample_output.md", "w") as f:
        f.write(f"# Query\n\n{query}\n\n")
        f.write(f"# Plan\n\n")
        for i, step in enumerate(final_state["plan"], 1):
            f.write(f"{i}. {step}\n")
        f.write(f"\n# Report\n\n{final_state['report']}\n")

    console.print("[dim]Output saved to examples/sample_output.md[/dim]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgentFlow Research Assistant")
    parser.add_argument("--query", type=str, required=True, help="Research query")
    parser.add_argument("--auto", action="store_true", help="Skip human approval step")
    args = parser.parse_args()
    run(args.query, auto_approve=args.auto)
