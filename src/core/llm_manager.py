"""
LLM Manager for Claude integration with validation system.
"""
from typing import Dict, List, Optional, Any
import anthropic
from dataclasses import dataclass
from .context_manager import ContextManager

@dataclass
class ValidationResult:
    passed: bool
    issues: List[str]
    suggestions: List[str]

class LLMManager:
    def __init__(self, context_manager: ContextManager, api_key: str):
        self.context = context_manager
        self.client = anthropic.Client(api_key=api_key)
        self.model = "claude-3-sonnet-20240229"
    
    def _prepare_system_prompt(self, context: dict) -> str:
        """Prepare system prompt with context"""
        return f"""You are a world-class development expert with the following characteristics:
Roles: {context['llm']['rules']['core_identity']['role']}
Expertise: {', '.join(context['llm']['rules']['core_identity']['expertise'])}

You MUST follow these standards:
{self._format_standards(context['llm']['rules']['standards'])}

Current Development Context:
- Active File: {context['cascade']['file_context']}
- Recent Changes: {len(context['cascade']['recent_changes'])} modifications
- Active Validations: {', '.join(context['llm']['validations'])}

You MUST follow these protocols:
{self._format_protocols(context['llm']['protocols'])}

Quality Metrics to Enforce:
{self._format_metrics(context['llm']['rules'].get('metrics', {}))}"""

    def _format_standards(self, standards: dict) -> str:
        formatted = []
        for category, items in standards.items():
            formatted.append(f"{category.title()}:")
            formatted.extend([f"- {item}" for item in items])
        return "\n".join(formatted)

    def _format_protocols(self, protocols: dict) -> str:
        formatted = []
        for phase, steps in protocols.items():
            formatted.append(f"{phase.title()}:")
            if isinstance(steps, list):
                formatted.extend([f"- {step}" for step in steps])
            else:
                for sub_phase, sub_steps in steps.items():
                    formatted.append(f"  {sub_phase}:")
                    formatted.extend([f"  - {step}" for step in sub_steps])
        return "\n".join(formatted)

    def _format_metrics(self, metrics: dict) -> str:
        formatted = []
        for category, values in metrics.items():
            formatted.append(f"{category.title()}:")
            for metric, value in values.items():
                formatted.append(f"- {metric}: {value}")
        return "\n".join(formatted)

    async def generate_response(self, user_input: str) -> dict:
        """Generate LLM response with context and validation"""
        context = self.context.prepare_context(user_input)
        system_prompt = self._prepare_system_prompt(context)
        
        # Première passe : génération de réponse
        response = await self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=[{"role": "user", "content": user_input}]
        )
        
        # Validation de la réponse
        validation = await self._validate_response(response.content, context)
        
        if not validation.passed:
            # Deuxième passe si la validation échoue
            corrected_response = await self._correct_response(
                user_input, response.content, validation, context
            )
            response = corrected_response
            validation = await self._validate_response(response.content, context)
        
        return {
            "response": response.content,
            "validation": validation,
            "context_used": context
        }

    async def _validate_response(self, response: str, context: dict) -> ValidationResult:
        """Validate response against rules and context"""
        validation_prompt = f"""Validate this AI response against our standards:

Response to validate:
{response}

Validation criteria:
1. Follows all protocols and standards
2. Meets quality metrics
3. Maintains security standards
4. Uses correct terminology
5. Provides complete solution

Return only a JSON object with:
- passed: boolean
- issues: list of strings
- suggestions: list of strings"""

        validation_response = await self.client.messages.create(
            model=self.model,
            system=self._prepare_system_prompt(context),
            messages=[{"role": "user", "content": validation_prompt}]
        )

        try:
            result = eval(validation_response.content)  # Simple pour l'exemple
            return ValidationResult(
                passed=result['passed'],
                issues=result['issues'],
                suggestions=result['suggestions']
            )
        except:
            return ValidationResult(False, ["Validation parsing failed"], [])

    async def _correct_response(
        self, user_input: str, original_response: str, 
        validation: ValidationResult, context: dict
    ) -> Any:
        """Correct response based on validation feedback"""
        correction_prompt = f"""Original request: {user_input}

Original response: {original_response}

Validation issues:
{chr(10).join(validation.issues)}

Suggestions:
{chr(10).join(validation.suggestions)}

Please provide a corrected response that addresses all validation issues."""

        return await self.client.messages.create(
            model=self.model,
            system=self._prepare_system_prompt(context),
            messages=[{"role": "user", "content": correction_prompt}]
        )
