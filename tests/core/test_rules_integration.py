"""
Tests d'intégration pour le système de règles.
"""
import pytest
from datetime import timedelta
import os
import time
from src.core.rules_manager import RulesManager, RuleType, BrainType
from src.core.cache_manager import ValidationCache
from src.core.monitoring import MonitoringSystem, AlertSeverity

@pytest.fixture
def rules_manager(tmp_path):
    return RulesManager()

class TestRulesIntegration:
    def test_validation_with_cache(self, rules_manager):
        """Test la validation avec mise en cache."""
        content = "def test_function():\n    pass"
        
        # Première validation
        result1 = rules_manager.validate(content, "method_length")
        assert result1["success"] is True
        
        # Deuxième validation (devrait utiliser le cache)
        result2 = rules_manager.validate(content, "method_length")
        assert result2["success"] is True
        
        # Vérifier les métriques de cache
        cache_metrics = rules_manager.get_metrics()["cache"]
        assert cache_metrics["code"]["hits"] >= 1

    def test_validation_with_monitoring(self, rules_manager):
        """Test la validation avec monitoring."""
        content = """def complex_function():
            if condition1:
                if condition2:
                    if condition3:
                        if condition4:
                            if condition5:
                                pass"""
        
        # Validation qui devrait échouer (complexité cyclomatique)
        with pytest.raises(Exception):
            rules_manager.validate(content, "cyclomatic_complexity")
        
        # Vérifier les alertes
        health_status = rules_manager.get_metrics()["validation"]
        assert health_status["active_alerts"] > 0
        assert health_status["status"] in ["warning", "critical"]

    def test_security_validation_alert(self, rules_manager):
        """Test la validation de sécurité avec alertes."""
        content = """
        def unsafe_function():
            password = "hardcoded_secret"
            os.system(user_input)
        """
        
        result = rules_manager.validate(
            content,
            "security_patterns",
            context={"environment": "production"}
        )
        
        assert result["success"] is False
        assert result["severity"] >= 4
        
        # Vérifier les alertes de sécurité
        metrics = rules_manager.get_metrics()
        assert metrics["validation"]["critical_alerts"] > 0

    def test_metrics_export(self, rules_manager, tmp_path):
        """Test l'export des métriques."""
        # Générer quelques données
        content = "def test_function():\n    pass"
        rules_manager.validate(content, "method_length")
        
        # Exporter les métriques
        metrics_dir = tmp_path / "metrics"
        os.makedirs(metrics_dir)
        rules_manager.export_metrics(str(metrics_dir))
        
        # Vérifier les fichiers exportés
        assert os.path.exists(metrics_dir / "metrics_current.json")
        assert os.path.exists(metrics_dir / "cache_metrics.json")

    def test_learning_from_history(self, rules_manager):
        """Test l'apprentissage basé sur l'historique."""
        # Générer un historique de validation
        content_good = "def simple_function():\n    pass"
        content_bad = """def complex_function():
            if condition1:
                if condition2:
                    if condition3:
                        pass"""
        
        rules_manager.validate(content_good, "cyclomatic_complexity")
        try:
            rules_manager.validate(content_bad, "cyclomatic_complexity")
        except:
            pass
        
        # Apprendre de l'historique
        rules_manager.learn_from_history()
        
        # Vérifier les métriques après apprentissage
        metrics = rules_manager.get_metrics()
        assert "rules" in metrics
        assert metrics["rules"]["total"] > 0

    def test_brain_specific_validation(self, rules_manager):
        """Test la validation spécifique à chaque cerveau."""
        content = "def test_function():\n    pass"
        
        # Validation LLM
        llm_recommendations = rules_manager.get_brain_recommendations(
            content,
            BrainType.LLM
        )
        assert isinstance(llm_recommendations, list)
        
        # Validation Cascade
        cascade_recommendations = rules_manager.get_brain_recommendations(
            content,
            BrainType.CASCADE
        )
        assert isinstance(cascade_recommendations, list)
        
        # Vérifier les métriques par cerveau
        metrics = rules_manager.get_metrics()
        assert "by_brain" in metrics["rules"]
        assert "llm" in metrics["rules"]["by_brain"]
        assert "cascade" in metrics["rules"]["by_brain"]
