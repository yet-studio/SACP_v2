"""
Validation Manager for automated checks and balances.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
import re

@dataclass
class CodeMetrics:
    complexity: int
    lines: int
    parameters: int
    
@dataclass
class ValidationCheck:
    name: str
    passed: bool
    details: str

class ValidationManager:
    def __init__(self, context_manager):
        self.context = context_manager
        self.metrics = self.context.llm_context.rules.get('metrics', {})
    
    def validate_code_changes(self, file_path: str, changes: List[dict]) -> List[ValidationCheck]:
        """Validate code changes against defined metrics"""
        checks = []
        
        # Complexité cyclomatique
        complexity = self._calculate_complexity(changes)
        checks.append(ValidationCheck(
            name="Complexity",
            passed=complexity <= self.metrics['code']['complexity_max'],
            details=f"Complexity score: {complexity}"
        ))
        
        # Longueur des méthodes
        method_lines = self._calculate_method_lines(changes)
        checks.append(ValidationCheck(
            name="Method Length",
            passed=method_lines <= self.metrics['code']['method_lines_max'],
            details=f"Method lines: {method_lines}"
        ))
        
        # Nombre de paramètres
        params = self._count_parameters(changes)
        checks.append(ValidationCheck(
            name="Parameters",
            passed=params <= self.metrics['code']['parameters_max'],
            details=f"Parameter count: {params}"
        ))
        
        return checks
    
    def validate_documentation(self, content: str) -> List[ValidationCheck]:
        """Validate documentation quality"""
        checks = []
        
        # Vérification de la langue
        english_check = self._check_english_content(content)
        checks.append(ValidationCheck(
            name="English Language",
            passed=english_check['passed'],
            details=english_check['details']
        ))
        
        # Vérification de la complétude
        completeness = self._check_documentation_completeness(content)
        checks.append(ValidationCheck(
            name="Documentation Completeness",
            passed=completeness['passed'],
            details=completeness['details']
        ))
        
        return checks
    
    def validate_security(self, changes: List[dict]) -> List[ValidationCheck]:
        """Validate security considerations"""
        checks = []
        
        # Vérification des pratiques de sécurité
        security_checks = self._perform_security_checks(changes)
        checks.extend(security_checks)
        
        return checks
    
    def _calculate_complexity(self, changes: List[dict]) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        for change in changes:
            content = change.get('content', '')
            # Compte les structures de contrôle
            complexity += content.count('if ') 
            complexity += content.count('while ')
            complexity += content.count('for ')
            complexity += content.count('except')
            complexity += content.count('case')
        return complexity
    
    def _calculate_method_lines(self, changes: List[dict]) -> int:
        """Calculate method lines"""
        max_lines = 0
        current_method_lines = 0
        in_method = False
        
        for change in changes:
            content = change.get('content', '').split('\n')
            for line in content:
                if re.match(r'^\s*def\s+', line):
                    if in_method:
                        max_lines = max(max_lines, current_method_lines)
                    in_method = True
                    current_method_lines = 0
                elif in_method:
                    current_method_lines += 1
        
        if in_method:
            max_lines = max(max_lines, current_method_lines)
        
        return max_lines
    
    def _count_parameters(self, changes: List[dict]) -> int:
        """Count maximum parameters in methods"""
        max_params = 0
        
        for change in changes:
            content = change.get('content', '')
            method_defs = re.finditer(r'def\s+\w+\s*\((.*?)\)', content)
            for match in method_defs:
                params = match.group(1).split(',')
                max_params = max(max_params, len(params))
        
        return max_params
    
    def _check_english_content(self, content: str) -> dict:
        """Verify content is in English"""
        # Simple heuristique pour l'exemple
        non_english = re.findall(r'[àáâãäçèéêëìíîïñòóôõöùúûüýÿ]', content)
        return {
            'passed': len(non_english) == 0,
            'details': f"Found {len(non_english)} non-English characters"
        }
    
    def _check_documentation_completeness(self, content: str) -> dict:
        """Check documentation completeness"""
        required_sections = [
            'purpose', 'usage', 'parameters', 'returns', 'example'
        ]
        
        found_sections = []
        for section in required_sections:
            if re.search(rf'\b{section}\b', content.lower()):
                found_sections.append(section)
        
        return {
            'passed': len(found_sections) == len(required_sections),
            'details': f"Found {len(found_sections)}/{len(required_sections)} required sections"
        }
    
    def _perform_security_checks(self, changes: List[dict]) -> List[ValidationCheck]:
        """Perform security checks on changes"""
        checks = []
        
        # Patterns de sécurité à vérifier
        security_patterns = {
            'hardcoded_secrets': r'(?i)(password|secret|key|token)\s*=\s*["\'][^"\']+["\']',
            'sql_injection': r'(?i)execute\s*\(\s*["\'].*?\%',
            'shell_injection': r'(?i)(os\.system|subprocess\.call)\s*\(',
            'unsafe_deserialization': r'(?i)(pickle\.loads|yaml\.load\()',
        }
        
        for change in changes:
            content = change.get('content', '')
            for check_name, pattern in security_patterns.items():
                matches = re.finditer(pattern, content)
                found = list(matches)
                checks.append(ValidationCheck(
                    name=f"Security: {check_name}",
                    passed=len(found) == 0,
                    details=f"Found {len(found)} potential {check_name} issues"
                ))
        
        return checks
