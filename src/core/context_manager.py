"""
Core Context Manager for LLM and Cascade integration.
Handles context persistence, sharing, and synchronization.
"""
import os
import yaml
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class CascadeContext:
    current_file: str
    project_tree: dict
    recent_changes: List[dict]
    memory_state: dict

@dataclass
class LLMContext:
    rules: dict
    protocols: List[str]
    conversation_history: List[dict]
    active_validations: List[str]

class ContextManager:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.cascade_context = self._load_cascade_context()
        self.llm_context = self._load_llm_context()
        
    def _load_cascade_context(self) -> CascadeContext:
        """Load Cascade context from .windsurf_rules"""
        rules_path = os.path.join(self.project_root, '.windsurf_rules')
        if os.path.exists(rules_path):
            with open(rules_path, 'r') as f:
                rules = yaml.safe_load(f)
                return CascadeContext(
                    current_file="",
                    project_tree=self._get_project_structure(),
                    recent_changes=[],
                    memory_state=rules
                )
        return None

    def _load_llm_context(self) -> LLMContext:
        """Load LLM context from llm_context.yaml"""
        context_path = os.path.join(self.project_root, 'config', 'llm_context.yaml')
        if os.path.exists(context_path):
            with open(context_path, 'r') as f:
                context = yaml.safe_load(f)
                return LLMContext(
                    rules=context.get('rules', {}),
                    protocols=context.get('protocols', []),
                    conversation_history=[],
                    active_validations=[]
                )
        return None

    def _get_project_structure(self) -> dict:
        """Get current project structure"""
        structure = {}
        for root, dirs, files in os.walk(self.project_root):
            if '.git' in dirs:
                dirs.remove('.git')
            rel_path = os.path.relpath(root, self.project_root)
            if rel_path == '.':
                structure = {'files': files, 'dirs': {}}
            else:
                current = structure
                for part in rel_path.split(os.sep):
                    current = current['dirs'].setdefault(part, {'files': [], 'dirs': {}})
                current['files'] = files
        return structure

    def prepare_context(self, user_input: str) -> dict:
        """Prepare combined context for AI operations"""
        return {
            "cascade": {
                "file_context": self.cascade_context.current_file,
                "project_structure": self.cascade_context.project_tree,
                "recent_changes": self.cascade_context.recent_changes
            },
            "llm": {
                "rules": self.llm_context.rules,
                "protocols": self.llm_context.protocols,
                "history": self.llm_context.conversation_history,
                "validations": self.llm_context.active_validations
            },
            "user_input": user_input
        }

    def update_cascade_context(self, file: str, changes: List[dict]):
        """Update Cascade context with new changes"""
        self.cascade_context.current_file = file
        self.cascade_context.recent_changes.extend(changes)
        self._persist_cascade_context()

    def update_llm_context(self, interaction: dict):
        """Update LLM context with new interaction"""
        self.llm_context.conversation_history.append(interaction)
        self._persist_llm_context()

    def _persist_cascade_context(self):
        """Persist Cascade context to .windsurf_rules"""
        rules_path = os.path.join(self.project_root, '.windsurf_rules')
        with open(rules_path, 'w') as f:
            yaml.safe_dump(self.cascade_context.memory_state, f)

    def _persist_llm_context(self):
        """Persist LLM context to llm_context.yaml"""
        context_path = os.path.join(self.project_root, 'config', 'llm_context.yaml')
        os.makedirs(os.path.dirname(context_path), exist_ok=True)
        with open(context_path, 'w') as f:
            context = {
                'rules': self.llm_context.rules,
                'protocols': self.llm_context.protocols,
                'active_validations': self.llm_context.active_validations
            }
            yaml.safe_dump(context, f)
