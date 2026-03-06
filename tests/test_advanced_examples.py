"""Example usage of Terminal Brain advanced features."""

from pathlib import Path
from terminalbrain.advanced import (
    ErrorAnalyzer,
    CommandPredictor,
    WorkflowDetector,
    CommandExplainer,
    ScriptGenerator,
    AliasSuggester,
    WorkflowRecommender,
    LearningFeedback,
    FeedbackType,
    SafetyChecker,
)


def example_error_analysis():
    """Example: Error Analysis and Fix Suggestions"""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Error Analysis Engine")
    print("=" * 60)

    analyzer = ErrorAnalyzer()

    # Simulate a missing command error
    print("\nScenario: User runs 'pip install numpy' but pip is not installed")
    result = analyzer.analyze(
        command="pip install numpy",
        stderr="bash: pip: command not found",
        exit_code=127,
    )

    print(f"\n✓ Error Detected: {result.message}")
    print(f"  Category: {result.category}")
    print(f"  Confidence: {result.confidence:.0%}")
    print(f"\n  Suggested Fixes:")
    for i, fix in enumerate(result.fixes[:3], 1):
        print(f"    {i}. {fix}")

    # Learn from successful fix
    analyzer.learn_from_fix("missing_pip", "python3 -m ensurepip")
    print(f"\n✓ System learned: python3 -m ensurepip works for missing_pip")


def example_command_prediction():
    """Example: Command Prediction with Markov Chains"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Command Prediction Engine")
    print("=" * 60)

    predictor = CommandPredictor(n=3)

    # Simulate a user's workflow
    workflow = [
        "ls",
        "cd project",
        "git status",
        "git add .",
        "git commit -m feature",
        "git push origin main",
        "cd ..",
        "ls",
        "cd project",
        "git status",
        "git add .",
        "git commit -m bugfix",
        "git push origin main",
        "cd ..",
        "ls",
    ]

    print("\nTraining on workflow:")
    print("  " + " → ".join(workflow[:6]) + " → ...")

    predictor.train(workflow)

    # Predict after "git add ."
    print("\nPredicting next command after 'git add .'")
    result = predictor.predict_next(["git add ."])

    print(f"\n✓ Predictions ({result.based_on}):")
    for cmd, confidence in result.predictions[:3]:
        print(f"  - {cmd}: {confidence:.0%}")

    # Predict entire workflow
    print("\nPredicting workflow starting with 'git add .':")
    workflow_pred = predictor.predict_workflow(["git add ."])
    print(f"  {' → '.join(workflow_pred[:5])} → ...")


def example_workflow_detection():
    """Example: Workflow Detection and Automation"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Workflow Detection Engine")
    print("=" * 60)

    detector = WorkflowDetector(min_frequency=2)

    history = [
        "git add .",
        "git commit -m update",
        "git push origin main",
        "git add .",
        "git commit -m update",
        "git push origin main",
        "docker build -t app .",
        "docker compose up -d",
        "docker build -t app .",
        "docker compose up -d",
    ]

    print("\nAnalyzing command history for patterns...")
    patterns = detector.analyze_history(history)

    print(f"\n✓ Detected {len(patterns)} workflow patterns:")
    for name, pattern in list(patterns.items())[:3]:
        print(f"\n  {name} (frequency: {pattern.frequency})")
        print(f"    {' → '.join(pattern.commands)}")

    # Statistics
    stats = detector.get_workflow_stats()
    print(f"\n✓ Statistics:")
    print(f"  Total workflows detected: {stats['total_workflows']}")
    print(f"  Total sequence occurrences: {stats['total_sequences']}")


def example_command_explanation():
    """Example: Command Explanation Engine"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Command Explanation Engine")
    print("=" * 60)

    explainer = CommandExplainer()

    # Explain a complex command
    command = "tar -czvf archive.tar.gz folder/"
    print(f"\nExplaining command: {command}")

    explanation = explainer.explain_command_parts(command)

    print("\n✓ Command breakdown:")
    for part, desc in explanation.items():
        print(f"  {part:20} → {desc}")


def example_script_generation():
    """Example: Intelligent Script Generation"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Script Generation Engine")
    print("=" * 60)

    generator = ScriptGenerator()

    # Generate backup script
    description = "backup my important files daily"
    print(f"\nGenerating script: '{description}'")

    script = generator.generate(description)

    print(f"\n✓ Generated: {script.name}")
    print(f"  Safety Level: {script.safety_level}")
    print(f"  Requires: {', '.join(script.requires)}")
    print(f"\nScript preview:")
    print("  " + "\n  ".join(script.content.split("\n")[:8]))
    print("  ...")


def example_alias_suggestions():
    """Example: Intelligent Alias Suggestions"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Alias Suggester")
    print("=" * 60)

    suggester = AliasSuggester(min_frequency=2)

    # Simulate user's frequent commands
    history = [
        "ls -la",
        "ls -la",
        "ls -la",
        "git add .",
        "git add .",
        "git commit -m message",
        "docker ps",
        "docker ps",
    ]

    print("\nAnalyzing command history for aliasing opportunities...")
    suggestions = suggester.analyze_history(history)

    print(f"\n✓ Alias suggestions:")
    for suggestion in suggestions[:5]:
        savings = int(suggestion.time_saved_per_use * suggestion.frequency)
        print(
            f"  alias {suggestion.alias}='{suggestion.command}' "
            f"(saves ~{savings} chars total)"
        )


def example_workflow_recommendations():
    """Example: Smart Workflow Recommendations"""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Workflow Recommender")
    print("=" * 60)

    recommender = WorkflowRecommender()

    # Get recommendations for various tasks
    tasks = [
        "find large files",
        "backup system",
        "monitor cpu usage",
        "search in codebase",
    ]

    print("\nRecommendations for common tasks:\n")

    for task in tasks:
        rec = recommender.recommend(task)
        if rec:
            print(f"Task: {task}")
            print(f"  Pipeline: {rec.pipeline[:60]}...")
            print(f"  Time: {rec.estimated_time}")
            print()


def example_learning_feedback():
    """Example: Learning Feedback Loop"""
    print("\n" + "=" * 60)
    print("EXAMPLE 8: Learning Feedback Loop")
    print("=" * 60)

    feedback = LearningFeedback()

    # Simulate user feedback
    print("\nRecording user feedback:")

    print("  1. User accepts 'git add .' suggestion")
    feedback.record_feedback(
        "git add .",
        FeedbackType.ACCEPTED,
        confidence_before=0.85,
    )

    print("  2. User rejects 'rm -rf' suggestion")
    feedback.record_feedback(
        "rm -rf", FeedbackType.REJECTED, confidence_before=0.70
    )

    print("  3. User modifies 'git commit' suggestion")
    feedback.record_feedback(
        "git commit",
        FeedbackType.MODIFIED,
        user_modification="git commit -m 'fix: issue'",
        confidence_before=0.60,
    )

    print("  4. User marks 'docker ps' as helpful")
    feedback.record_feedback("docker ps", FeedbackType.HELPFUL)

    # Get statistics
    stats = feedback.get_statistics()
    print(f"\n✓ Learning Statistics:")
    print(f"  Total feedback entries: {stats['total_feedback']}")
    print(f"  Acceptance rate: {stats['acceptance_rate']:.0%}")
    print(f"  Rejection rate: {stats['rejection_rate']:.0%}")

    # Get best suggestions
    best = feedback.get_best_suggestions(top_k=3)
    print(f"\n✓ Best-performing suggestions:")
    for cmd, score in best:
        print(f"  - {cmd}: {score:.2f}")


def example_safety_checker():
    """Example: Safety Checking for Dangerous Commands"""
    print("\n" + "=" * 60)
    print("EXAMPLE 9: Safety Checker")
    print("=" * 60)

    checker = SafetyChecker()

    # Check various command risks
    commands = [
        ("ls -la", "Safe command"),
        ("git push", "Version control"),
        ("chmod 777 /tmp", "Permission change"),
        ("rm -rf /home", "High-risk deletion"),
        ("dd if=/dev/sda", "Critical disk operation"),
    ]

    print("\nCommand Safety Analysis:\n")

    for command, description in commands:
        risk = checker.check(command)
        score = checker.get_safety_score(command)

        print(f"Command: {command:30} ({description})")
        print(f"  Risk Level: {risk.risk_level.value.upper()}")
        print(f"  Safety Score: {score:.0%}")

        if risk.suggested_alternative:
            print(f"  Alternative: {risk.suggested_alternative}")
        print()


def example_integrated_workflow():
    """Example: Integrated Advanced Features Workflow"""
    print("\n" + "=" * 60)
    print("EXAMPLE 10: Integrated Advanced Features")
    print("=" * 60)

    print("\nScenario: Complete Terminal Brain workflow for a developer\n")

    # 1. Safety check
    checker = SafetyChecker()
    user_command = "find . -name '*.tmp' -exec rm {} \\;"

    risk = checker.check(user_command)
    print(f"1. Safety Check: {user_command}")
    print(f"   → Risk: {risk.risk_level.value}")
    print(f"   → Confirmed: Yes\n")

    # 2. Execute and capture error
    analyzer = ErrorAnalyzer()
    stderr = ""  # Command succeeds

    # 3. Predict next command
    predictor = CommandPredictor()
    history = [user_command, "git add .", "git commit -m cleanup"]
    predictor.train(history)

    result = predictor.predict_next([user_command])
    print(f"2. Command Prediction:")
    if result.predictions:
        print(f"   → Next command: {result.predictions[0][0]}")
        print(f"   → Confidence: {result.predictions[0][1]:.0%}\n")

    # 4. Record feedback
    feedback = LearningFeedback()
    feedback.record_feedback(user_command, FeedbackType.ACCEPTED)
    print(f"3. Learning Feedback:")
    print(f"   → Recorded: User accepted command\n")

    # 5. Suggest aliases
    suggester = AliasSuggester()
    print(f"4. Alias Suggestion:")
    print(f"   → alias clean_tmp='find . -name \"*.tmp\" -exec rm {{}} \\;'\n")

    # 6. Recommend workflow
    recommender = WorkflowRecommender()
    rec = recommender.recommend("cleanup and commit")
    print(f"5. Workflow Recommendation:")
    if rec:
        print(f"   → Task: {rec.task}")
        print(f"   → Pipeline: {rec.pipeline}\n")

    print("✓ Workflow completed with intelligent assistance!")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("TERMINAL BRAIN - ADVANCED FEATURES EXAMPLES")
    print("=" * 60)

    examples = [
        ("Error Analysis", example_error_analysis),
        ("Command Prediction", example_command_prediction),
        ("Workflow Detection", example_workflow_detection),
        ("Command Explanation", example_command_explanation),
        ("Script Generation", example_script_generation),
        ("Alias Suggestions", example_alias_suggestions),
        ("Workflow Recommendations", example_workflow_recommendations),
        ("Learning Feedback", example_learning_feedback),
        ("Safety Checker", example_safety_checker),
        ("Integrated Workflow", example_integrated_workflow),
    ]

    for i, (name, example_func) in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"\n⚠ Error in {name}: {e}")

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
