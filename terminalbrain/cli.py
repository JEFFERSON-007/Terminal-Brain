"""
Terminal Brain CLI
"""

import asyncio
import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich import print as rprint
from pathlib import Path
import json

from terminalbrain.config import load_config, save_config, get_config_path
from terminalbrain.ai import RecommendationEngine
from terminalbrain.core import CommandParser, HistoryAnalyzer
from terminalbrain.monitor import SystemMonitor, ProcessMonitor
from terminalbrain.knowledge import KnowledgeBase

app = typer.Typer(help="Terminal Brain - Your AI brain inside the terminal")
console = Console()


@app.command()
def ask(
    query: str = typer.Argument(..., help="Natural language query"),
    top_n: int = typer.Option(5, "--top", "-t", help="Number of suggestions"),
    explain: bool = typer.Option(False, "--explain", "-e", help="Get explanations"),
) -> None:
    """Ask Terminal Brain for command suggestions"""

    async def _ask(q: str, n: int, exp: bool):
        engine = RecommendationEngine()
        await engine.initialize()

        with console.status("[bold cyan]Analyzing query..."):
            suggestions = await engine.recommend(q, top_n=n)

        if not suggestions:
            console.print("[red]No suggestions found[/red]")
            return

        # Display suggestions
        table = Table(title="Command Suggestions", show_header=True)
        table.add_column("#", style="cyan")
        table.add_column("Command", style="green")
        table.add_column("Confidence", style="yellow")
        table.add_column("Source", style="blue")

        for i, suggestion in enumerate(suggestions, 1):
            table.add_row(
                str(i),
                suggestion.command,
                f"{suggestion.confidence:.0%}",
                suggestion.source,
            )

        console.print(table)

        # Show explanations if requested
        if exp:
            for i, suggestion in enumerate(suggestions, 1):
                console.print(f"\n[bold]{i}. {suggestion.command}[/bold]")
                console.print(f"   {suggestion.explanation}")

    asyncio.run(_ask(query, top_n, explain))


@app.command()
def predict(
    command: Optional[str] = typer.Argument(None, help="Current command (optional)"),
    top_n: int = typer.Option(3, "--top", "-t", help="Number of predictions"),
) -> None:
    """Predict next command"""

    async def _predict(cmd: Optional[str], n: int):
        engine = RecommendationEngine()
        await engine.initialize()

        # Use last command from history if not provided
        current_cmd = cmd
        if not current_cmd:
            history = HistoryAnalyzer()
            history.load_history()
            if history.commands:
                current_cmd = history.commands[-1]
            else:
                console.print("[red]No command history found[/red]")
                return

        with console.status("[bold cyan]Predicting..."):
            predictions = await engine.predict_next(current_cmd, top_n=n)

        if not predictions:
            console.print("[red]No predictions available[/red]")
            return

        console.print(f"\n[bold]Current command:[/bold] {current_cmd}")
        console.print("[bold]Predicted next commands:[/bold]\n")

        table = Table(show_header=True)
        table.add_column("Command", style="green")
        table.add_column("Probability", style="yellow")

        for suggestion in predictions:
            table.add_row(suggestion.command, f"{suggestion.confidence:.0%}")

        console.print(table)

    asyncio.run(_predict(command, top_n))


@app.command()
def dashboard() -> None:
    """Show real-time system dashboard"""

    try:
        from textual.app import ComposeResult, RenderableType
        from textual.widgets import Widget
        from textual.containers import Container
        import time

        # Simple dashboard without full Textual UI for now
        config = load_config()

        while True:
            console.clear()
            metrics = SystemMonitor.get_metrics()

            rprint("[bold cyan]Terminal Brain Dashboard[/bold cyan]\n")

            # Create metrics table
            table = Table(show_header=False, box=None)
            table.add_row("[bold]CPU Usage[/bold]", f"[cyan]{metrics.cpu_percent:.1f}%[/cyan]")
            table.add_row("[bold]Memory[/bold]", f"[cyan]{metrics.ram_used_gb:.1f}GB / {metrics.ram_total_gb:.1f}GB ({metrics.ram_percent:.1f}%)[/cyan]")
            table.add_row("[bold]Disk[/bold]", f"[cyan]{metrics.disk_used_gb:.1f}GB / {metrics.disk_total_gb:.1f}GB ({metrics.disk_percent:.1f}%)[/cyan]")

            if config.ui.show_battery and metrics.battery_percent:
                status = "⚡ Charging" if metrics.battery_charging else "🔋 Discharging"
                table.add_row("[bold]Battery[/bold]", f"[cyan]{metrics.battery_percent:.0f}% {status}[/cyan]")

            console.print(table)

            # Show top processes
            if config.ui.show_processes:
                console.print("\n[bold]Top Processes (CPU)[/bold]")
                processes = ProcessMonitor.get_top_processes(5, sort_by="cpu")

                proc_table = Table(show_header=True)
                proc_table.add_column("PID", style="cyan")
                proc_table.add_column("Name", style="green")
                proc_table.add_column("CPU %", style="yellow")
                proc_table.add_column("Memory MB", style="yellow")

                for proc in processes:
                    proc_table.add_row(
                        str(proc.pid),
                        proc.name,
                        f"{proc.cpu_percent:.1f}",
                        f"{proc.memory_mb:.1f}",
                    )

                console.print(proc_table)

            console.print("\n[dim]Press Ctrl+C to exit, refreshing in 2 seconds...[/dim]")
            time.sleep(2)

    except KeyboardInterrupt:
        console.print("\n[yellow]Dashboard closed[/yellow]")


@app.command()
def generate(
    description: str = typer.Argument(..., help="Script description"),
    save: bool = typer.Option(False, "--save", "-s", help="Save to file"),
    filename: Optional[str] = typer.Option(None, "--output", "-o", help="Output filename"),
) -> None:
    """Generate a shell script"""

    async def _generate(desc: str, should_save: bool, fname: Optional[str]):
        engine = RecommendationEngine()

        with console.status("[bold cyan]Generating script..."):
            script = await engine.generate_script(desc)

        if not script:
            console.print("[red]Could not generate script[/red]")
            return

        # Display script
        syntax = Syntax(script, "bash", theme="monokai", line_numbers=True)
        console.print(syntax)

        # Save if requested
        if should_save:
            output_file = Path(fname or "script.sh")
            output_file.write_text(script)
            output_file.chmod(0o755)
            console.print(f"\n[green]Script saved to {output_file}[/green]")

    asyncio.run(_generate(description, save, filename))


@app.command()
def config(
    action: str = typer.Argument("show", help="Action: show, edit, reset"),
) -> None:
    """Manage configuration"""

    config_path = get_config_path()

    if action == "show":
        if config_path.exists():
            with open(config_path, "r") as f:
                content = f.read()
            syntax = Syntax(content, "toml", theme="monokai")
            console.print(syntax)
        else:
            console.print("[yellow]Config file not found, using defaults[/yellow]")

    elif action == "edit":
        import subprocess

        editor = os.getenv("EDITOR", "nano")
        subprocess.run([editor, str(config_path)])

    elif action == "reset":
        config = load_config()
        save_config(config)
        console.print("[green]Config reset to defaults[/green]")

    else:
        console.print("[red]Unknown action[/red]")


@app.command()
def analyze() -> None:
    """Analyze your command history"""

    console.print("[bold cyan]Analyzing command history...[/bold cyan]\n")

    history = HistoryAnalyzer()
    history.load_history()

    stats = history.get_statistics()

    # Display statistics
    table = Table(show_header=False)
    for key, value in stats.items():
        if isinstance(value, float):
            table.add_row(key, f"{value:.2%}")
        else:
            table.add_row(key, str(value))

    console.print(table)

    # Show most common commands
    console.print("\n[bold]Top 10 Commands[/bold]")
    most_common = history.get_most_common(10)

    common_table = Table(show_header=True)
    common_table.add_column("Command", style="green")
    common_table.add_column("Count", style="cyan")

    for cmd, count in most_common:
        common_table.add_row(cmd, str(count))

    console.print(common_table)

    # Show suggested aliases
    console.print("\n[bold]Suggested Aliases[/bold]")
    aliases = history.suggest_aliases(min_frequency=3)

    alias_table = Table(show_header=True)
    alias_table.add_column("Alias", style="yellow")
    alias_table.add_column("Command", style="green")

    for alias, cmd in aliases.items():
        alias_table.add_row(alias, cmd)

    console.print(alias_table)


@app.command()
def knowledge() -> None:
    """Browse knowledge base"""

    kb = KnowledgeBase()

    console.print("[bold cyan]Terminal Brain Knowledge Base[/bold cyan]\n")

    table = Table(show_header=True)
    table.add_column("Command", style="green")
    table.add_column("Description", style="cyan")
    table.add_column("Tags", style="yellow")

    for cmd, info in sorted(kb.commands.items()):
        tags = ", ".join(info.get("tags", []))
        table.add_row(cmd, info["description"], tags)

    console.print(table)


@app.command()
def version() -> None:
    """Show version"""
    from terminalbrain import __version__

    console.print(f"[bold cyan]Terminal Brain[/bold cyan] v{__version__}")


@app.command()
def install(
    module: str = typer.Argument(..., help="Module to install (llm, prediction, knowledgebase, voice, workflows)"),
) -> None:
    """Install optional modules."""
    from terminalbrain.plugins import PluginManager
    
    manager = PluginManager()
    
    console.print(f"[bold cyan]Installing module: {module}[/bold cyan]")
    
    if manager.install_module(module):
        console.print(f"[green]✓ Module '{module}' installed successfully[/green]")
        console.print(f"\nModule '{module}' is now available and enabled.")
        console.print("Configure it in ~/.config/terminalbrain/terminalbrain.toml if needed.")
    else:
        console.print(f"[red]✗ Failed to install module '{module}'[/red]")
        sys.exit(1)


@app.command()
def uninstall(
    module: str = typer.Argument(..., help="Module to uninstall"),
) -> None:
    """Uninstall optional modules."""
    from terminalbrain.plugins import PluginManager
    
    manager = PluginManager()
    
    if manager.uninstall_module(module):
        console.print(f"[green]✓ Module '{module}' uninstalled[/green]")
    else:
        console.print(f"[red]✗ Failed to uninstall module '{module}'[/red]")
        sys.exit(1)


@app.command()
def modules() -> None:
    """List available and installed modules."""
    from terminalbrain.plugins import PluginManager, PluginStatus
    
    manager = PluginManager()
    plugins = manager.list_plugins()
    
    table = Table(title="Terminal Brain Optional Modules", show_header=True)
    table.add_column("Module", style="cyan")
    table.add_column("Status", style="yellow")
    table.add_column("Description", style="green")
    
    descriptions = {
        "llm": "Local LLM support (Ollama, llama.cpp)",
        "prediction": "ML-based command prediction",
        "knowledgebase": "Vector search knowledge base",
        "voice": "Speech-to-text voice commands",
        "workflows": "Advanced workflow automation",
    }
    
    for name, status in plugins.items():
        status_str = status.value.replace("_", " ").title()
        table.add_row(name, status_str, descriptions.get(name, ""))
    
    console.print(table)
    
    console.print("\n[bold]Usage:[/bold]")
    console.print("  terminal-brain install <module>    # Install a module")
    console.print("  terminal-brain uninstall <module>  # Uninstall a module")


def main():
    """Main entry point"""
    import os

    app()


if __name__ == "__main__":
    main()
