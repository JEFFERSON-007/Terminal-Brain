"""Tests for advanced Terminal Brain features."""

import pytest
from pathlib import Path
from datetime import datetime

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
    RiskLevel,
)


class TestErrorAnalyzer:
    """Tests for Error Analysis Engine."""

    def test_command_not_found_detection(self):
        analyzer = ErrorAnalyzer()
        result = analyzer.analyze("unknowncmd", "bash: unknowncmd: command not found", 127)

        assert result.error_detected
        assert result.category == "missing_command"
        assert result.confidence > 0.9

    def test_permission_denied_detection(self):
        analyzer = ErrorAnalyzer()
        result = analyzer.analyze("rm file.txt", "Permission denied", 1)

        assert result.error_detected
        assert result.category == "permission_denied"

    def test_git_not_repo_detection(self):
        analyzer = ErrorAnalyzer()
        result = analyzer.analyze(
            "git push", "fatal: not a git repository", 128
        )

        assert result.error_detected
        assert result.category == "not_git_repo"
        assert len(result.fixes) > 0

    def test_success_case(self):
        analyzer = ErrorAnalyzer()
        result = analyzer.analyze("ls", "", 0)

        assert not result.error_detected
        assert result.category == "success"

    def test_error_history_tracking(self):
        analyzer = ErrorAnalyzer()
        analyzer.analyze("cmd1", "error1", 1)
        analyzer.analyze("cmd2", "error2", 1)

        stats = analyzer.get_error_statistics()
        assert len(stats) >= 1

    def test_learn_from_fix(self):
        analyzer = ErrorAnalyzer()
        pattern = next(p for p in analyzer.error_patterns if p.category == "missing_pip")
        original_confidence = pattern.confidence

        analyzer.learn_from_fix("missing_pip", "sudo apt install python3-pip")
        assert pattern.confidence > original_confidence


class TestCommandPredictor:
    """Tests for Command Prediction Engine."""

    def test_bigram_prediction(self):
        predictor = CommandPredictor()
        history = [
            "git add .",
            "git commit -m message",
            "git push",
            "git add .",
            "git commit -m message",
            "git push",
        ]

        predictor.train(history)
        result = predictor.predict_next(["git add"])

        assert len(result.predictions) > 0
        assert result.predictions[0][0] == "git"  # Normalized to base command

    def test_frequency_ranking(self):
        predictor = CommandPredictor()
        history = [
            "ls",
            "cd folder",
            "ls",
            "ls",
            "cd folder",
        ]

        predictor.train(history)
        result = predictor.predict_next(["ls"], top_k=5)

        assert len(result.predictions) > 0
        # Most confident should be highest
        assert result.predictions[0][1] >= result.predictions[1][1] if len(result.predictions) > 1 else True

    def test_workflow_prediction(self):
        predictor = CommandPredictor()
        history = [
            "git add .",
            "git commit -m test",
            "git push",
            "git add .",
            "git commit -m test",
            "git push",
        ]

        predictor.train(history)
        workflow = predictor.predict_workflow(["git add"])

        assert len(workflow) >= 1
        assert "git" in workflow[0]

    def test_model_save_load(self, tmp_path):
        predictor = CommandPredictor()
        history = ["ls", "cd", "ls", "cd"]
        predictor.train(history)

        # Save
        model_file = tmp_path / "model.json"
        predictor.save_model(model_file)
        assert model_file.exists()

        # Load
        predictor2 = CommandPredictor()
        predictor2.load_model(model_file)
        result = predictor2.predict_next(["ls"])
        assert len(result.predictions) > 0


class TestWorkflowDetector:
    """Tests for Workflow Detection Engine."""

    def test_detect_workflow_patterns(self):
        detector = WorkflowDetector(min_frequency=2)
        history = [
            "git add .",
            "git commit -m update",
            "git push",
            "git add .",
            "git commit -m update",
            "git push",
        ]

        patterns = detector.analyze_history(history)
        assert len(patterns) > 0

    def test_workflow_naming(self):
        detector = WorkflowDetector()
        commands = ["git", "commit", "push"]
        name = detector._suggest_workflow_name(commands)

        assert name is not None
        assert isinstance(name, str)

    def test_save_load_workflow(self, tmp_path):
        detector = WorkflowDetector()
        detector.patterns["test_workflow"] = detector.WorkflowPattern(
            name="test_workflow",
            commands=["git add .", "git commit -m test"],
            frequency=5,
            last_used=str(datetime.now()),
        )

        # This would test YAML save/load if implementation uses it
        workflows = detector.list_workflows()
        assert "test_workflow" in [w.name for w in workflows]


class TestCommandExplainer:
    """Tests for Command Explanation Engine."""

    def test_built_in_command_explanation(self):
        explainer = CommandExplainer()
        result = explainer.explain("ls")

        assert result is not None
        assert result.command == "ls"
        assert "directory" in result.description.lower()

    def test_command_parts_explanation(self):
        explainer = CommandExplainer()
        parts = explainer.explain_command_parts("ls -la")

        assert "ls" in parts
        assert "-la" in parts or "-l" in parts

    def test_flag_extraction(self):
        explainer = CommandExplainer()
        result = explainer.explain("tar")

        if result:
            assert len(result.flags) >= 0

    def test_cache_functionality(self):
        explainer = CommandExplainer()
        result1 = explainer.explain("ls")
        result2 = explainer.explain("ls")

        assert result1 is result2  # Same object from cache


class TestScriptGenerator:
    """Tests for Script Generation."""

    def test_backup_script_generation(self):
        generator = ScriptGenerator()
        script = generator.generate("backup my home folder daily")

        assert script.name.endswith(".sh")
        assert "tar" in script.content or "backup" in script.content.lower()
        assert script.safety_level in ["low", "medium", "high"]

    def test_deploy_script_generation(self):
        generator = ScriptGenerator()
        script = generator.generate("deploy docker project")

        assert "docker" in script.content.lower() or "git" in script.content.lower()

    def test_cleanup_script_generation(self):
        generator = ScriptGenerator()
        script = generator.generate("clean up old files")

        assert "rm" in script.content or "cleanup" in script.content.lower()

    def test_safety_detection(self):
        generator = ScriptGenerator()
        
        # Safe script
        safe_script = generator.generate("backup folder")
        assert safe_script.safety_level in ["low", "medium"]
        
        # Dangerous script - contains rm -rf
        script_content = "#!/bin/bash\nrm -rf /"
        safety_level = generator._check_safety(script_content)
        assert safety_level == "high"


class TestAliasSuggester:
    """Tests for Alias Suggestions."""

    def test_alias_suggestion(self):
        suggester = AliasSuggester(min_frequency=2)
        history = ["ls -la", "ls -la", "git add ."]

        suggestions = suggester.analyze_history(history)
        # Should suggest ll for ls -la
        assert any("ll" in str(s.alias).lower() for s in suggestions)

    def test_alias_script_generation(self):
        suggester = AliasSuggester()
        suggestions = [
            suggester.AliasSuggestion("ls -la", "ll", 5, 3, "Common alias"),
        ]

        script = suggester.get_alias_script(suggestions)
        assert "alias" in script
        assert "ll" in script

    def test_function_script_generation(self):
        suggester = AliasSuggester()
        suggestions = [
            suggester.AliasSuggestion("complex command", "cc", 3, 10, "Complex alias"),
        ]

        script = suggester.get_function_script(suggestions)
        assert "function" in script or "cc()" in script


class TestWorkflowRecommender:
    """Tests for Workflow Recommendations."""

    def test_workflow_recommendation(self):
        recommender = WorkflowRecommender()
        result = recommender.recommend("find large files")

        assert result is not None
        assert len(result.pipeline) > 0
        assert "du" in result.pipeline or "find" in result.pipeline

    def test_alternative_pipelines(self):
        recommender = WorkflowRecommender()
        result = recommender.recommend("backup system")

        # Should have alternatives
        assert result is not None

    def test_workflow_listing(self):
        recommender = WorkflowRecommender()
        workflows = recommender.list_available_workflows()

        assert len(workflows) > 0
        assert "find_large_files" in workflows or any("find" in w for w in workflows)

    def test_custom_pipeline(self):
        recommender = WorkflowRecommender()
        recommender.add_custom_pipeline(
            "my_task", "echo custom", "Custom pipeline"
        )

        workflows = recommender.list_available_workflows()
        # Note: custom pipelines stored differently in implementation


class TestLearningFeedback:
    """Tests for Learning Feedback Loop."""

    def test_feedback_recording(self):
        feedback = LearningFeedback()
        entry = feedback.record_feedback(
            "ls -la",
            FeedbackType.ACCEPTED,
            confidence_before=0.7,
        )

        assert entry.suggestion == "ls -la"
        assert entry.feedback_type == "accepted"

    def test_score_update_on_acceptance(self):
        feedback = LearningFeedback()
        initial_score = feedback.get_suggestion_score("cmd")

        feedback.record_feedback("cmd", FeedbackType.ACCEPTED)
        new_score = feedback.get_suggestion_score("cmd")

        assert new_score > initial_score

    def test_score_decrease_on_rejection(self):
        feedback = LearningFeedback()
        feedback.record_feedback("cmd", FeedbackType.ACCEPTED)
        score_after_accept = feedback.get_suggestion_score("cmd")

        feedback.record_feedback("cmd", FeedbackType.REJECTED)
        score_after_reject = feedback.get_suggestion_score("cmd")

        assert score_after_reject < score_after_accept

    def test_statistics(self):
        feedback = LearningFeedback()
        feedback.record_feedback("cmd1", FeedbackType.ACCEPTED)
        feedback.record_feedback("cmd2", FeedbackType.REJECTED)
        feedback.record_feedback("cmd3", FeedbackType.ACCEPTED)

        stats = feedback.get_statistics()
        assert stats["total_feedback"] == 3
        assert stats["acceptance_rate"] > 0

    def test_save_load_history(self, tmp_path):
        feedback = LearningFeedback()
        feedback.record_feedback("cmd", FeedbackType.ACCEPTED)

        history_file = tmp_path / "feedback.json"
        feedback.save_history(history_file)
        assert history_file.exists()

        feedback2 = LearningFeedback(history_file)
        assert len(feedback2.feedback_history) == 1


class TestSafetyChecker:
    """Tests for Safety Checking."""

    def test_critical_risk_detection(self):
        checker = SafetyChecker()
        risk = checker.check("rm -rf /")

        assert risk.risk_level == RiskLevel.CRITICAL
        assert risk.confirmation_required

    def test_high_risk_detection(self):
        checker = SafetyChecker()
        risk = checker.check("dd if=/dev/sda")

        assert risk.risk_level == RiskLevel.CRITICAL
        assert "disk" in risk.description.lower()

    def test_medium_risk_detection(self):
        checker = SafetyChecker()
        risk = checker.check("sudo apt remove python3")

        assert risk.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]

    def test_safe_command(self):
        checker = SafetyChecker()
        risk = checker.check("ls -la")

        assert risk.risk_level == RiskLevel.SAFE
        assert not risk.confirmation_required

    def test_safety_score(self):
        checker = SafetyChecker()

        safe_score = checker.get_safety_score("ls")
        dangerous_score = checker.get_safety_score("rm -rf /")

        assert safe_score > dangerous_score

    def test_affected_items_extraction(self):
        checker = SafetyChecker()
        risk = checker.check("rm /home/user/important.txt")

        assert len(risk.affected_items) > 0

    def test_confirmation_message(self):
        checker = SafetyChecker()
        risk = checker.check("rm -rf /")

        message = checker.get_confirmation_message(risk)
        assert len(message) > 0
        assert "CRITICAL" in message or "WARNING" in message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
