import argparse
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from src.agent.loop import AgentLoop

def main():
    console = Console()
    parser = argparse.ArgumentParser(description="Gemini-Claw Agent")
    parser.add_argument("--query", type=str, required=True, help="The query to execute.")
    parser.add_argument("--model", type=str, default="gemini-3-flash-preview", help="Model to use.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose debug output.")
    
    args = parser.parse_args()
    
    console.print(Panel(f"[bold blue]Gemini-Claw Agent[/bold blue]\nRequest: [italic]{args.query}[/italic]", title="Initialization"))
    
    loop = AgentLoop(initial_model=args.model, verbose=args.verbose)
    
    result = None
    
    if args.verbose:
        # bypassing progress bar in verbose mode to see print outputs clearly
        console.print("[yellow]Running in VERBOSE mode. Debug logs will be visible.[/yellow]")
        result = loop.execute_with_retry(args.query)
    else:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("[cyan]Initializing agent loop...", total=None)
            progress.update(task, description="[bold cyan]Executing Decompose -> Search -> Fetch -> Synthesize pipeline...[/bold cyan]")
            result = loop.execute_with_retry(args.query)
    
    if "error" in result and len(result) == 1:
        console.print("[bold red]Final Error:[/bold red]")
        console.print(result["error"])
        sys.exit(1)
        
    console.print("\n")
    console.print(Panel(Markdown(result.get("raw_response", "No response text")), title="[bold green]Final Response[/bold green]", expand=True))
    
    urls = result.get("urls", [])
    if urls:
        console.print("\n[bold yellow]Extracted URLs:[/bold yellow]")
        for url in urls:
            console.print(f"- [link={url}]{url}[/link]")
            
    # Show sub-queries transparently
    sub_queries = result.get("sub_queries", [])
    if sub_queries:
        console.print(Panel("\n".join([f"- {q}" for q in sub_queries]), title="[dim]Executed Sub-Queries[/dim]", border_style="dim"))

if __name__ == "__main__":
    main()
