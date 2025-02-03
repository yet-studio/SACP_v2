"""
Rules Manager for custom validation rules and quality thresholds.
"""
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import re
import yaml

class RuleType(Enum):
    CODE = "code"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    ARCHITECTURE = "architecture"
    PERFORMANCE = "performance"
    CUSTOM = "custom"

class BrainType(Enum):
    LLM = "llm"
    CASCADE = "cascade"
    SHARED = "shared"

@dataclass
class Rule:
    name: str
    type: RuleType
    description: str
    validator: Callable
    threshold: Any
    severity: int
    tags: List[str]
    brain: BrainType

class RulesManager:
    def __init__(self, config_path: str = None):
        self.rules: Dict[str, Rule] = {}
        self.config_path = config_path
        self.metrics: Dict[str, Any] = {}
        self._load_default_rules()
        if config_path:
            self._load_custom_rules(config_path)
    
    def _load_default_rules(self):
        """Charge les règles par défaut"""
        # Règles de code
        self.add_rule(
            name="method_length",
            type=RuleType.CODE,
            description="Method length should not exceed threshold",
            validator=lambda x, t: len(x.split('\n')) <= t,
            threshold=20,
            severity=3,
            tags=["code_quality", "maintainability"],
            brain=BrainType.SHARED
        )
        
        self.add_rule(
            name="cyclomatic_complexity",
            type=RuleType.CODE,
            description="Cyclomatic complexity should not exceed threshold",
            validator=self._check_complexity,
            threshold=5,
            severity=4,
            tags=["code_quality", "complexity"],
            brain=BrainType.SHARED
        )
        
        # Règles de documentation
        self.add_rule(
            name="docstring_completeness",
            type=RuleType.DOCUMENTATION,
            description="Docstring must include all required sections",
            validator=self._check_docstring,
            threshold=["description", "parameters", "returns", "examples"],
            severity=3,
            tags=["documentation", "completeness"],
            brain=BrainType.SHARED
        )
        
        # Règles de sécurité
        self.add_rule(
            name="security_patterns",
            type=RuleType.SECURITY,
            description="Code must not contain security anti-patterns",
            validator=self._check_security_patterns,
            threshold={
                "hardcoded_secrets": r'(?i)(password|secret|key|token)\s*=\s*["\'][^"\']+["\']',
                "sql_injection": r'(?i)execute\s*\(\s*["\'].*?\%',
                "shell_injection": r'(?i)(os\.system|subprocess\.call)\s*\('
            },
            severity=5,
            tags=["security", "vulnerabilities"],
            brain=BrainType.SHARED
        )

    def _load_custom_rules(self, path: str):
        """Charge les règles personnalisées depuis le fichier de configuration."""
        try:
            with open(path, 'r') as f:
                config = yaml.safe_load(f)

            # Charger les métriques partagées
            if 'shared' in config and 'metrics' in config['shared']:
                self.metrics = config['shared']['metrics']

            # Charger les règles LLM
            if 'llm' in config and 'validation_rules' in config['llm']:
                for category, rules in config['llm']['validation_rules'].items():
                    for rule in rules:
                        validator = self._get_validator(rule.get('validator', {}))
                        self.add_rule(
                            name=rule['name'],
                            type=RuleType(category.upper()),
                            description=rule['description'],
                            validator=validator,
                            threshold=rule.get('threshold'),
                            severity=rule.get('severity', 3),
                            tags=rule.get('tags', []),
                            brain=BrainType.LLM
                        )

            # Charger les règles Cascade
            if 'cascade' in config and 'execution_rules' in config['cascade']:
                for rule in config['cascade']['execution_rules']:
                    validator = self._get_validator(rule.get('validator', {}))
                    self.add_rule(
                        name=rule['name'],
                        type=self._determine_rule_type(rule.get('tags', [])),
                        description=rule['description'],
                        validator=validator,
                        threshold=rule.get('threshold'),
                        severity=rule.get('severity', 3),
                        tags=rule.get('tags', []),
                        brain=BrainType.CASCADE
                    )

        except Exception as e:
            print(f"Error loading rules: {e}")

    def _determine_rule_type(self, tags: List[str]) -> RuleType:
        """Détermine le type de règle basé sur les tags."""
        type_mapping = {
            'security': RuleType.SECURITY,
            'documentation': RuleType.DOCUMENTATION,
            'code_quality': RuleType.CODE,
            'architecture': RuleType.ARCHITECTURE,
            'performance': RuleType.PERFORMANCE
        }
        
        for tag in tags:
            for key, value in type_mapping.items():
                if key in tag:
                    return value
        return RuleType.CUSTOM

    def add_rule(self, name: str, type: RuleType, description: str,
                validator: Callable, threshold: Any, severity: int,
                tags: List[str], brain: BrainType):
        """Ajoute une nouvelle règle avec son type de cerveau."""
        self.rules[name] = Rule(
            name=name,
            type=type,
            description=description,
            validator=validator,
            threshold=threshold,
            severity=severity,
            tags=tags,
            brain=brain
        )

    def get_rules_by_brain(self, brain: BrainType) -> List[Rule]:
        """Récupère toutes les règles d'un cerveau donné."""
        return [rule for rule in self.rules.values() if rule.brain == brain]

    def get_rules_by_type(self, type: RuleType) -> List[Rule]:
        """Récupère toutes les règles d'un type donné"""
        return [rule for rule in self.rules.values() if rule.type == type]

    def get_rules_by_tag(self, tag: str) -> List[Rule]:
        """Récupère toutes les règles avec un tag donné"""
        return [rule for rule in self.rules.values() if tag in rule.tags]

    def validate(self, content: str, rule_name: str) -> dict:
        """Valide du contenu avec une règle spécifique"""
        if rule_name not in self.rules:
            raise ValueError(f"Rule {rule_name} not found")
        
        rule = self.rules[rule_name]
        try:
            passed = rule.validator(content, rule.threshold)
            return {
                "passed": passed,
                "rule": rule_name,
                "severity": rule.severity,
                "description": rule.description
            }
        except Exception as e:
            return {
                "passed": False,
                "rule": rule_name,
                "severity": rule.severity,
                "description": f"Validation error: {str(e)}"
            }

    def _check_complexity(self, content: str, threshold: int) -> bool:
        """Calcule la complexité cyclomatique"""
        complexity = 1
        complexity += content.count('if ')
        complexity += content.count('while ')
        complexity += content.count('for ')
        complexity += content.count('except')
        complexity += content.count('case')
        return complexity <= threshold

    def _check_docstring(self, content: str, required_sections: List[str]) -> bool:
        """Vérifie la complétude d'une docstring"""
        for section in required_sections:
            if section.lower() not in content.lower():
                return False
        return True

    def _check_security_patterns(self, content: str, patterns: Dict[str, str]) -> bool:
        """Vérifie les patterns de sécurité"""
        for pattern in patterns.values():
            if re.search(pattern, content):
                return False
        return True

    def _get_validator(self, validator_config: dict) -> Callable:
        """Convertit une configuration de validateur en fonction"""
        if validator_config['type'] == 'regex':
            pattern = re.compile(validator_config['pattern'])
            return lambda x, t: bool(pattern.search(x) if validator_config.get('match', True) else not pattern.search(x))
        elif validator_config['type'] == 'length':
            return lambda x, t: len(x) <= t
        elif validator_config['type'] == 'custom':
            # Pour les validateurs personnalisés, vous pouvez implémenter
            # un système de chargement dynamique de code
            raise NotImplementedError("Custom validators not implemented yet")
        else:
            raise ValueError(f"Unknown validator type: {validator_config['type']}")

    def update_threshold(self, rule_name: str, new_threshold: Any):
        """Met à jour le seuil d'une règle"""
        if rule_name not in self.rules:
            raise ValueError(f"Rule {rule_name} not found")
        self.rules[rule_name].threshold = new_threshold

    def export_rules(self, path: str):
        """Exporte les règles vers un fichier YAML"""
        rules_export = {
            'rules': [
                {
                    'name': rule.name,
                    'type': rule.type.value,
                    'description': rule.description,
                    'threshold': rule.threshold,
                    'severity': rule.severity,
                    'tags': rule.tags,
                    'brain': rule.brain.value
                }
                for rule in self.rules.values()
            ]
        }
        with open(path, 'w') as f:
            yaml.safe_dump(rules_export, f)
