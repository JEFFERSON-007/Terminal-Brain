"""
Quick start example demonstrating Terminal Brain capabilities
"""

import asyncio
from pathlib import Path

from terminalbrain.ai import RecommendationEngine
from terminalbrain.core import CommandParser, HistoryAnalyzer, ContextAnalyzer
from terminalbrain.monitor import SystemMonitor, ProcessMonitor
from terminalbrain.knowledge import KnowledgeBase


async def example_command_recommendations():
    """Example 1: Get command recommendations"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Command Recommendations")
    print("="*60)

    engine = RecommendationEngine(llm_backend="ollama", model="mistral")
    await engine.initialize()

    # Get recommendations
    queries = [
        "find large files",
        "search for python files",
        "list directory contents with details",
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 40)

        suggestions = await engine.recommend(query, top_n=3)

        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion.command}")
            print(f"   Confidence: {suggestion.confidence:.0%} | Source: {suggestion.source}")
            print()


async def example_command_prediction():
    """Example 2: Predict next command"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Command Prediction")
    print("="*60)

    engine = RecommendationEngine()
    await engine.initialize()

    # Common workflows
    workflows = [
        "cd project",
        "git add .",
        "docker build",
    ]

    for cmd in workflows:
        print(f"\nCurrent: {cmd}")
        print("-" * 40)

        predictions = await engine.predict_next(cmd, top_n=2)

        for pred in predictions:
            print(f"  → {pred.command} ({pred.confidence:.0%})")


def example_command_parsing():
    """Example 3: Parse and analyze commands"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Command Parsing")
    print("="*60)

    parser = CommandParser()

    commands = [
        "find . -name '*.txt' | grep error",
        "git add . && git commit -m 'changes'",
        "tar -czf backup.tar.gz /home/user &",
    ]

    for cmd in commands:
        print(f"\nCommand: {cmd}")
        print("-" * 40)

        parsed = parser.parse(cmd)
        info = parser.get_command_info(cmd)

        print(f"Main command: {parsed.command}")
        print(f"Arguments: {parsed.args}")
        print(f"Flags: {list(parsed.flags.keys())}")
        print(f"Complexity: {info['complexity']}")
        print(f"Has pipes: {info['has_pipes']}")
        print(f"Background: {parsed.background}")


def example_history_analysis():
    """Example 4: Analyze command history"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Command History Analysis")
    print("="*60)

    analyzer = HistoryAnalyzer()
    analyzer.load_history()

    # Get statistics
    stats = analyzer.get_statistics()
    print(f"\nHistory Statistics:")
    print("-" * 40)
    print(f"Total commands: {stats.get('total_commands', 0)}")
    print(f"Unique commands: {stats.get('unique_commands', 0)}")
    print(f"Most used: {stats.get('most_used_command', 'N/A')}")

    # Show top commands
    print(f"\nTop 5 Commands:")
    print("-" * 40)
    for cmd, count in analyzer.get_most_common(5):
        print(f"  {cmd}: {count}")

    # Get alias suggestions
    print(f"\nSuggested Aliases:")
    print("-" * 40)
    aliases = analyzer.suggest_aliases(min_frequency=3)
    for alias, cmd in list(aliases.items())[:5]:
        print(f"  alias {alias}=\"{cmd}\"")


def example_context_analysis():
    """Example 5: Analyze terminal context"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Terminal Context Analysis")
    print("="*60)

    context = ContextAnalyzer.get_context()

    print(f"\nCurrent Context:")
    print("-" * 40)
    print(f"Working directory: {context.cwd}")
    print(f"User: {context.user}")
    print(f"Shell: {context.shell}")
    print(f"Git repository: {context.git_repo}")
    if context.git_branch:
        print(f"Git branch: {context.git_branch}")

    # Analyze directory
    analysis = ContextAnalyzer.analyze_cwd()
    print(f"\nDirectory Analysis:")
    print("-" * 40)
    for key, value in analysis.items():
        print(f"  {key}: {value}")


def example_system_monitoring():
    """Example 6: Monitor system resources"""
    print("\n" + "="*60)
    print("EXAMPLE 6: System Monitoring")
    print("="*60)

    # Get metrics
    metrics = SystemMonitor.get_metrics()

    print(f"\nSystem Metrics:")
    print("-" * 40)
    print(f"CPU Usage: {metrics.cpu_percent:.1f}%")
    print(f"Memory: {metrics.ram_used_gb:.1f} GB / {metrics.ram_total_gb:.1f} GB ({metrics.ram_percent:.1f}%)")
    print(f"Disk: {metrics.disk_used_gb:.1f} GB / {metrics.disk_total_gb:.1f} GB ({metrics.disk_percent:.1f}%)")

    if metrics.battery_percent is not None:
        status = "Charging" if metrics.battery_charging else "Discharging"
        print(f"Battery: {metrics.battery_percent:.0f}% ({status})")

    # Get top processes
    print(f"\nTop 5 Processes (by CPU):")
    print("-" * 40)
    processes = ProcessMonitor.get_top_processes(5, sort_by="cpu")
    for proc in processes:
        print(f"  {proc.name}: {proc.cpu_percent:.1f}% CPU, {proc.memory_mb:.1f} MB RAM")


def example_knowledge_base():
    """Example 7: Browse knowledge base"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Knowledge Base")
    print("="*60)

    kb = KnowledgeBase()

    print(f"\nTotal commands in knowledge base: {len(kb.commands)}")
    print("-" * 40)

    # Show some commands
    for cmd in list(kb.commands.keys())[:5]:
        info = kb.get_command_info(cmd)
        print(f"\n{cmd}:")
        print(f"  Description: {info['description']}")
        print(f"  Syntax: {info['syntax']}")
        if info.get("examples"):
            print(f"  Examples:")
            for ex in info["examples"][:2]:
                print(f"    - {ex}")


async def main():
    """Run all examples"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  TERMINAL BRAIN - Quick Start Examples".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")

    # Run examples
    try:
        await example_command_recommendations()
    except Exception as e:
        print(f"Recommendation example skipped (LLM not available): {e}")

    try:
        await example_command_prediction()
    except Exception as e:
        print(f"Prediction example skipped: {e}")

    example_command_parsing()
    example_history_analysis()
    example_context_analysis()
    example_system_monitoring()
    example_knowledge_base()

    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)
    print("\nNext steps:")
    print("  • Try: tb ask 'find large files'")
    print("  • View: tb dashboard")
    print("  • Analyze: tb analyze")
    print("  • Learn more: tb --help")
    print()


if __name__ == "__main__":
    asyncio.run(main())
