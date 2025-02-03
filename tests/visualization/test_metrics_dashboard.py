"""
Tests for the metrics visualization dashboard.
"""
import pytest
import os
import json
from datetime import datetime
from bs4 import BeautifulSoup
from src.visualization.metrics_dashboard import MetricsDashboard
from src.core.rules_manager import RulesManager

@pytest.fixture
def dashboard(tmp_path):
    return MetricsDashboard(export_dir=str(tmp_path))

@pytest.fixture
def sample_metrics():
    return {
        "validation": {
            "status": "healthy",
            "active_alerts": 2,
            "critical_alerts": 0,
            "metrics_collected": 150,
            "last_update": datetime.now().isoformat()
        },
        "cache": {
            "code": {
                "hits": 120,
                "misses": 30,
                "size": 800,
                "evictions": 20,
                "hit_rate": 0.8,
                "entries": [
                    {"hits": 5, "last_accessed": datetime.now().isoformat()}
                ]
            },
            "security": {
                "hits": 90,
                "misses": 10,
                "size": 1500,
                "evictions": 5,
                "hit_rate": 0.9,
                "entries": [
                    {"hits": 3, "last_accessed": datetime.now().isoformat()}
                ]
            }
        },
        "rules": {
            "total": 25,
            "by_type": {
                "code": 10,
                "security": 5,
                "documentation": 5,
                "architecture": 3,
                "performance": 2
            },
            "by_brain": {
                "llm": 8,
                "cascade": 12,
                "shared": 5
            }
        }
    }

class TestMetricsDashboard:
    def test_dashboard_creation(self, dashboard, sample_metrics):
        """Test la création basique du dashboard."""
        dashboard.generate_dashboard(sample_metrics)
        
        # Vérifier que le fichier est créé
        files = os.listdir(dashboard.export_dir)
        assert len(files) == 1
        assert files[0].startswith("dashboard_")
        assert files[0].endswith(".html")

    def test_dashboard_content(self, dashboard, sample_metrics):
        """Test le contenu du dashboard généré."""
        dashboard.generate_dashboard(sample_metrics)
        
        # Lire le fichier généré
        files = os.listdir(dashboard.export_dir)
        dashboard_file = os.path.join(dashboard.export_dir, files[0])
        
        with open(dashboard_file, 'r') as f:
            content = f.read()
        
        # Parser le HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Vérifier les éléments essentiels
        assert soup.title.string.startswith("Métriques de Validation")
        
        # Vérifier les métriques de résumé
        summary = soup.find("div", class_="summary")
        assert summary is not None
        
        metrics = summary.find_all("div", class_="metric")
        assert len(metrics) == 3
        
        # Vérifier les graphiques
        assert soup.find("div", id="cache_performance") is not None
        assert soup.find("div", id="validation_performance") is not None
        assert soup.find("div", id="rules_analysis") is not None

    def test_cache_performance_plot(self, dashboard, sample_metrics):
        """Test la création du graphique de performance du cache."""
        fig = dashboard._create_cache_performance_plot(sample_metrics["cache"])
        
        # Vérifier la structure du graphique
        assert len(fig.data) == 4  # 4 sous-graphiques
        assert fig.layout.height == 800
        assert "Performance du Cache" in fig.layout.title.text

    def test_validation_performance_plot(self, dashboard, sample_metrics):
        """Test la création du graphique de performance des validations."""
        fig = dashboard._create_validation_performance_plot(sample_metrics)
        
        # Vérifier la structure du graphique
        assert len(fig.data) == 4  # 4 sous-graphiques
        assert fig.layout.height == 800
        assert "Performance des Validations" in fig.layout.title.text

    def test_rules_analysis_plot(self, dashboard, sample_metrics):
        """Test la création du graphique d'analyse des règles."""
        fig = dashboard._create_rules_analysis_plot(sample_metrics["rules"])
        
        # Vérifier la structure du graphique
        assert len(fig.data) == 4  # 4 sous-graphiques
        assert fig.layout.height == 800
        assert "Analyse des Règles" in fig.layout.title.text

    def test_dashboard_update(self, dashboard, tmp_path):
        """Test la mise à jour du dashboard avec un RulesManager."""
        # Créer un RulesManager avec quelques données
        rules_manager = RulesManager()
        
        # Valider quelques règles pour générer des métriques
        content = "def test_function():\n    pass"
        rules_manager.validate(content, "method_length")
        
        # Mettre à jour le dashboard
        dashboard.update_dashboard(rules_manager)
        
        # Vérifier que le fichier est créé
        files = os.listdir(dashboard.export_dir)
        assert len(files) == 1
        assert files[0].startswith("dashboard_")

    def test_multiple_updates(self, dashboard, sample_metrics):
        """Test plusieurs mises à jour du dashboard."""
        # Générer plusieurs versions
        for _ in range(3):
            dashboard.generate_dashboard(sample_metrics)
        
        # Vérifier que tous les fichiers sont créés
        files = os.listdir(dashboard.export_dir)
        assert len(files) == 3
        
        # Vérifier que les timestamps sont différents
        timestamps = [f.split("_")[1].split(".")[0] for f in files]
        assert len(set(timestamps)) == 3  # Tous les timestamps sont uniques
