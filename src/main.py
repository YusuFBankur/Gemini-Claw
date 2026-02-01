import argparse
import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.theme import Theme
from rich import box
from src.agent.loop import AgentLoop

CLAW_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "highlight": "bold magenta",
    "url": "underline blue",
    "stat_val": "bold yellow"
})

def create_header():
    return Panel(
        "[bold cyan]GEMINI-CLAW[/bold cyan] [dim]v1.2 (Speed Optimized)[/dim]\n"
        "[italic white]Autonomous Research & Synthesis Engine[/italic white]",
        box=box.DOUBLE_EDGE,
        border_style="cyan",
        padding=(1, 2)
    )

def main():
    console = Console(theme=CLAW_THEME)
    parser = argparse.ArgumentParser(description="Gemini-Claw Agent")
    parser.add_argument("--query", type=str, required=True, help="The query to execute.")
    parser.add_argument("--model", type=str, default="gemini-3-flash-preview", help="Model to use.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose debug output.")
    
    args = parser.parse_args()
    
    console.print(create_header())
    console.print(Panel(f"[bold white]Query:[/bold white] {args.query}", border_style="dim"))
    
    loop = AgentLoop(initial_model=args.model, verbose=args.verbose)
    
    start_wall_time = time.time()
    result = None
    
    status_label = "[bold cyan]Autonomous Research in progress...[/bold cyan]"
    if args.verbose:
        console.print("[yellow]Benchmarking Mode: Active. Telemetry will sync...[/yellow]\n")
        result = loop.execute_with_retry(args.query)
    else:
        with console.status(status_label, spinner="bouncingBar") as status:
            result = loop.execute_with_retry(args.query)
    
    total_duration = time.time() - start_wall_time

    if not result or (isinstance(result, dict) and "error" in result):
        console.print("\n[bold red]CRITICAL ERROR[/bold red]")
        console.print(Panel(str(result.get("error", "Unknown error occurred")), border_style="red"))
        sys.exit(1)
        
    # Final Result Section
    console.print("\n" + "━" * console.width)
    console.print("[bold green]✨ FINAL RESEARCH REPORT[/bold green]\n")
    
    final_text = result.get("raw_response", "No response text")
    console.print(Markdown(final_text))
    
    console.print("\n" + "━" * console.width)
    
    # Telemetry Dashboard
    telemetry = result.get("telemetry", {})
    
    table = Table(box=box.ROUNDED, border_style="dim", expand=True, title="[bold blue]Performance Telemetry[/bold blue]")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="stat_val")
    
    table.add_row("Total Wall Time", f"{total_duration:.2f}s")
    table.add_row("CLI Processing Time", f"{telemetry.get('cli_latency_ms', 0)/1000:.2f}s")
    table.add_row("Autonomous Tool Calls", str(telemetry.get("tool_calls", 0)))
    table.add_row("Target Model", f"[magenta]{args.model}[/magenta]")
    
    console.print(table)
    
    if args.verbose:
        # Show sub-query/thought trace if present
        sub_queries = result.get("sub_queries", [])
        if sub_queries:
            console.print(Panel("\n".join([f"• {q}" for q in sub_queries]), title="Self-Correction / Thought Trace", border_style="dim"))

    console.print("\n[dim italic text_align_right]Optimized by Gemini-Claw v1.2[/dim italic text_align_right]")

if __name__ == "__main__":
    main()
