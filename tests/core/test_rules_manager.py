"""
Tests for the AI Assistant Rules Management System.
Ensures proper validation, hierarchy, and decision-making capabilities.
"""
import pytest
from src.core.rules_manager import RulesManager, RuleType, BrainType, Rule
import os

@pytest.fixture
def rules_manager():
    return RulesManager()

@pytest.fixture
def ai_rules_file(tmp_path):
    rules_content = """
version: "1.0"

llm:
  identity:
    role: "World-class Development Expert"
    expertise: ["Enterprise architect", "Security specialist"]
  
  validation_rules:
    code:
      - name: strategic_pattern
        description: "Validate strategic design patterns"
        validator:
          type: custom
          module: pattern_validator
          function: check_pattern
        threshold:
          patterns: ["Factory", "Strategy", "Observer"]
        severity: 5
        tags: ["architecture", "patterns"]

cascade:
  execution_rules:
    - name: implementation_quality
      description: "Check implementation quality"
      validator:
        type: custom
        module: quality_validator
        function: check_quality
      threshold:
        metrics: ["cohesion", "coupling"]
      severity: 4
      tags: ["code_quality", "implementation"]

shared:
  metrics:
    code:
      complexity_max: 5
      cohesion_min: 0.8
    """
    rules_file = tmp_path / ".windsurf_rules"
    rules_file.write_text(rules_content)
    return str(rules_file)

class TestAIRulesSystem:
    def test_brain_hierarchy(self, rules_manager, ai_rules_file):
        """Verify that the brain hierarchy is properly maintained"""
        rules_manager._load_custom_rules(ai_rules_file)
        
        llm_rules = rules_manager.get_rules_by_brain(BrainType.LLM)
        cascade_rules = rules_manager.get_rules_by_brain(BrainType.CASCADE)
        
        assert any(rule.name == "strategic_pattern" for rule in llm_rules)
        assert any(rule.name == "implementation_quality" for rule in cascade_rules)
        
        # LLM rules should have higher severity on average
        llm_severity = sum(rule.severity for rule in llm_rules) / len(llm_rules)
        cascade_severity = sum(rule.severity for rule in cascade_rules) / len(cascade_rules)
        assert llm_severity >= cascade_severity

    def test_strategic_thinking(self, rules_manager, ai_rules_file):
        """Test LLM's strategic thinking capabilities"""
        rules_manager._load_custom_rules(ai_rules_file)
        
        strategic_code = """
        class PaymentStrategy:
            def __init__(self):
                self.observers = []
            
            def attach(self, observer):
                self.observers.append(observer)
            
            def notify(self):
                for observer in self.observers:
                    observer.update()
        """
        
        non_strategic_code = """
        class Payment:
            def process(self):
                if payment_type == "credit":
                    process_credit()
                elif payment_type == "debit":
                    process_debit()
        """
        
        strategic_result = rules_manager.validate(strategic_code, "strategic_pattern")
        non_strategic_result = rules_manager.validate(non_strategic_code, "strategic_pattern")
        
        assert strategic_result["passed"]
        assert not non_strategic_result["passed"]

    def test_implementation_quality(self, rules_manager, ai_rules_file):
        """Test Cascade's implementation quality checks"""
        rules_manager._load_custom_rules(ai_rules_file)
        
        good_implementation = """
        class UserService:
            def __init__(self, user_repo):
                self.user_repo = user_repo
            
            def get_user(self, user_id):
                return self.user_repo.find_by_id(user_id)
        """
        
        poor_implementation = """
        class UserService:
            def get_user(self, user_id):
                conn = Database.connect()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE id = " + user_id)
                return cursor.fetchone()
        """
        
        good_result = rules_manager.validate(good_implementation, "implementation_quality")
        poor_result = rules_manager.validate(poor_implementation, "implementation_quality")
        
        assert good_result["passed"]
        assert not poor_result["passed"]

    def test_shared_metrics(self, rules_manager, ai_rules_file):
        """Test shared metrics between LLM and Cascade"""
        rules_manager._load_custom_rules(ai_rules_file)
        
        assert rules_manager.metrics["code"]["complexity_max"] == 5
        assert rules_manager.metrics["code"]["cohesion_min"] == 0.8
        
        # Both LLM and Cascade should use these metrics
        complex_code = """
        def process(data):
            if condition1:
                if condition2:
                    while something:
                        if another:
                            pass
        """
        
        # Both brains should reject overly complex code
        for brain in [BrainType.LLM, BrainType.CASCADE]:
            rules = rules_manager.get_rules_by_brain(brain)
            for rule in rules:
                if "complexity" in rule.tags:
                    result = rules_manager.validate(complex_code, rule.name)
                    assert not result["passed"]

    def test_adaptive_validation(self, rules_manager, ai_rules_file):
        """Test system's ability to adapt validation based on context"""
        rules_manager._load_custom_rules(ai_rules_file)
        
        # Production code should be strictly validated
        prod_context = {"environment": "production", "critical": True}
        test_context = {"environment": "test", "critical": False}
        
        code = """
        def process_payment(amount):
            # TODO: Implement validation
            process(amount)
        """
        
        # Production validation should be stricter
        prod_results = [
            rules_manager.validate(code, rule.name, context=prod_context)
            for rule in rules_manager.get_rules_by_brain(BrainType.LLM)
        ]
        
        test_results = [
            rules_manager.validate(code, rule.name, context=test_context)
            for rule in rules_manager.get_rules_by_brain(BrainType.LLM)
        ]
        
        # More rules should fail in production context
        prod_failures = sum(1 for r in prod_results if not r["passed"])
        test_failures = sum(1 for r in test_results if not r["passed"])
        assert prod_failures > test_failures

    def test_learning_capability(self, rules_manager, ai_rules_file):
        """Test system's ability to learn from validation history"""
        rules_manager._load_custom_rules(ai_rules_file)
        
        # Simulate validation history
        history = [
            {"code": "def func(): pass", "passed": True, "rule": "complexity"},
            {"code": "def func(): pass", "passed": False, "rule": "documentation"},
            {"code": "class A:\n def b(): pass", "passed": True, "rule": "cohesion"}
        ]
        
        # System should adjust thresholds based on history
        rules_manager.learn_from_history(history)
        
        # Verify learning impact
        documentation_rule = next(
            rule for rule in rules_manager.rules.values()
            if "documentation" in rule.tags
        )
        assert documentation_rule.severity > 3  # Severity should increase for failing rules

class TestRulesManager:
    def test_default_rules_loaded(self, rules_manager):
        """Verify that default rules are loaded correctly"""
        assert len(rules_manager.rules) > 0
        assert "method_length" in rules_manager.rules
        assert "cyclomatic_complexity" in rules_manager.rules
        assert "security_patterns" in rules_manager.rules

    def test_method_length_validation(self, rules_manager):
        """Test method length validation"""
        short_method = "def test():\n    pass"
        long_method = "\n".join([f"    print({i})" for i in range(25)])
        
        assert rules_manager.validate(short_method, "method_length")["passed"]
        assert not rules_manager.validate(long_method, "method_length")["passed"]

    def test_complexity_validation(self, rules_manager):
        """Test cyclomatic complexity validation"""
        simple_code = "def test():\n    return True"
        complex_code = """
        def complex():
            if condition1:
                if condition2:
                    while something:
                        if another:
                            pass
                        elif other:
                            pass
        """
        
        assert rules_manager.validate(simple_code, "cyclomatic_complexity")["passed"]
        assert not rules_manager.validate(complex_code, "cyclomatic_complexity")["passed"]

    def test_security_validation(self, rules_manager):
        """Test security pattern validation"""
        safe_code = """
        def get_user(id):
            return db.query(User).filter_by(id=id).first()
        """
        unsafe_code = """
        password = "hardcoded_secret"
        query = f"SELECT * FROM users WHERE id = {user_input}"
        os.system(f"rm {file_path}")
        """
        
        assert rules_manager.validate(safe_code, "security_patterns")["passed"]
        assert not rules_manager.validate(unsafe_code, "security_patterns")["passed"]

    def test_docstring_validation(self, rules_manager):
        """Test docstring completeness validation"""
        complete_doc = '''"""
        description: This is a test function
        parameters:
            - param1: first parameter
        returns:
            - bool: operation result
        examples:
            >>> test_func(1)
            True
        """'''
        
        incomplete_doc = '''"""
        This is just a description
        """'''
        
        assert rules_manager.validate(complete_doc, "docstring_completeness")["passed"]
        assert not rules_manager.validate(incomplete_doc, "docstring_completeness")["passed"]

    def test_custom_rules_loading(self, rules_manager, ai_rules_file):
        """Test loading custom rules from file"""
        rules_manager._load_custom_rules(ai_rules_file)
        assert "custom_length" in rules_manager.rules
        
        short_content = "x" * 40
        long_content = "x" * 60
        
        assert rules_manager.validate(short_content, "custom_length")["passed"]
        assert not rules_manager.validate(long_content, "custom_length")["passed"]

    def test_rule_filtering(self, rules_manager):
        """Test filtering rules by type and tags"""
        code_rules = rules_manager.get_rules_by_type(RuleType.CODE)
        security_rules = rules_manager.get_rules_by_type(RuleType.SECURITY)
        
        assert len(code_rules) > 0
        assert len(security_rules) > 0
        assert all(rule.type == RuleType.CODE for rule in code_rules)
        assert all(rule.type == RuleType.SECURITY for rule in security_rules)

    def test_threshold_updates(self, rules_manager):
        """Test updating rule thresholds"""
        rules_manager.update_threshold("method_length", 30)
        long_method = "\n".join([f"    print({i})" for i in range(25)])
        
        assert rules_manager.validate(long_method, "method_length")["passed"]

    def test_rule_export(self, rules_manager, tmp_path):
        """Test exporting rules to file"""
        export_path = tmp_path / "exported_rules.yaml"
        rules_manager.export_rules(str(export_path))
        
        assert export_path.exists()
        content = export_path.read_text()
        assert "method_length" in content
        assert "security_patterns" in content

    def test_invalid_rule_handling(self, rules_manager):
        """Test handling of invalid rules"""
        with pytest.raises(ValueError):
            rules_manager.validate("test", "non_existent_rule")
        
        with pytest.raises(ValueError):
            rules_manager.update_threshold("non_existent_rule", 10)
