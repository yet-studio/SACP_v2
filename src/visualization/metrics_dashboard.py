"""
Dashboard interactif pour visualiser les métriques du système.
Utilise Plotly pour des graphiques interactifs et exportables.
"""
from typing import Dict, List, Any
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import json
import os

class MetricsDashboard:
    def __init__(self, export_dir: str = "metrics_viz"):
        self.export_dir = export_dir
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

    def _create_cache_performance_plot(self, cache_metrics: Dict) -> go.Figure:
        """Crée un graphique de performance du cache."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Hit Rate par Type",
                "Taille des Caches",
                "Évictions",
                "Durée Moyenne d'Accès"
            )
        )

        # Données pour les graphiques
        types = list(cache_metrics.keys())
        hit_rates = [metrics["hit_rate"] for metrics in cache_metrics.values()]
        sizes = [metrics["size"] for metrics in cache_metrics.values()]
        evictions = [metrics["evictions"] for metrics in cache_metrics.values()]
        
        # Hit Rate
        fig.add_trace(
            go.Bar(
                x=types,
                y=hit_rates,
                name="Hit Rate",
                marker_color='rgb(55, 83, 109)'
            ),
            row=1, col=1
        )
        
        # Taille
        fig.add_trace(
            go.Bar(
                x=types,
                y=sizes,
                name="Taille",
                marker_color='rgb(26, 118, 255)'
            ),
            row=1, col=2
        )
        
        # Évictions
        fig.add_trace(
            go.Bar(
                x=types,
                y=evictions,
                name="Évictions",
                marker_color='rgb(158, 202, 225)'
            ),
            row=2, col=1
        )
        
        # Durée moyenne
        durations = []
        for metrics in cache_metrics.values():
            entries = metrics.get("entries", [])
            if entries:
                avg_duration = sum(1 for e in entries if e.get("hits", 0) > 0) / len(entries)
                durations.append(avg_duration)
            else:
                durations.append(0)
        
        fig.add_trace(
            go.Bar(
                x=types,
                y=durations,
                name="Durée Moyenne",
                marker_color='rgb(98, 182, 149)'
            ),
            row=2, col=2
        )

        fig.update_layout(
            height=800,
            title_text="Performance du Cache par Type",
            showlegend=False
        )

        return fig

    def _create_validation_performance_plot(self, monitoring_metrics: Dict) -> go.Figure:
        """Crée un graphique de performance des validations."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Taux de Succès par Type",
                "Durée Moyenne de Validation",
                "Alertes Actives",
                "Distribution des Sévérités"
            )
        )

        # Extraire les données
        validation_data = monitoring_metrics.get("validation", {})
        alerts = validation_data.get("active_alerts", 0)
        critical_alerts = validation_data.get("critical_alerts", 0)
        
        # Taux de succès (exemple de données)
        success_rates = {
            "code": 0.85,
            "security": 0.95,
            "documentation": 0.90,
            "architecture": 0.88,
            "performance": 0.92
        }
        
        fig.add_trace(
            go.Bar(
                x=list(success_rates.keys()),
                y=list(success_rates.values()),
                name="Taux de Succès",
                marker_color='rgb(67, 147, 195)'
            ),
            row=1, col=1
        )
        
        # Durée moyenne
        durations = {
            "code": 0.15,
            "security": 0.25,
            "documentation": 0.10,
            "architecture": 0.20,
            "performance": 0.18
        }
        
        fig.add_trace(
            go.Bar(
                x=list(durations.keys()),
                y=list(durations.values()),
                name="Durée (s)",
                marker_color='rgb(214, 39, 40)'
            ),
            row=1, col=2
        )
        
        # Alertes
        fig.add_trace(
            go.Pie(
                labels=["Critiques", "Autres", "Pas d'Alerte"],
                values=[critical_alerts, alerts - critical_alerts, 100 - alerts],
                name="Alertes",
                marker_colors=['rgb(255, 65, 54)', 'rgb(255, 144, 14)', 'rgb(44, 160, 44)']
            ),
            row=2, col=1
        )
        
        # Distribution des sévérités
        severities = {
            "1 (Info)": 45,
            "2 (Low)": 30,
            "3 (Medium)": 15,
            "4 (High)": 8,
            "5 (Critical)": 2
        }
        
        fig.add_trace(
            go.Bar(
                x=list(severities.keys()),
                y=list(severities.values()),
                name="Sévérités",
                marker_color='rgb(148, 103, 189)'
            ),
            row=2, col=2
        )

        fig.update_layout(
            height=800,
            title_text="Performance des Validations",
            showlegend=False
        )

        return fig

    def _create_rules_analysis_plot(self, rules_metrics: Dict) -> go.Figure:
        """Crée un graphique d'analyse des règles."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Règles par Type",
                "Règles par Cerveau",
                "Ajustements des Seuils",
                "Distribution des Tags"
            )
        )

        # Règles par type
        types = rules_metrics.get("by_type", {})
        fig.add_trace(
            go.Bar(
                x=list(types.keys()),
                y=list(types.values()),
                name="Par Type",
                marker_color='rgb(31, 119, 180)'
            ),
            row=1, col=1
        )

        # Règles par cerveau
        brains = rules_metrics.get("by_brain", {})
        fig.add_trace(
            go.Pie(
                labels=list(brains.keys()),
                values=list(brains.values()),
                name="Par Cerveau",
                marker_colors=['rgb(255, 127, 14)', 'rgb(44, 160, 44)', 'rgb(214, 39, 40)']
            ),
            row=1, col=2
        )

        # Ajustements des seuils (exemple)
        thresholds = {
            "Augmentés": 15,
            "Diminués": 8,
            "Stables": 77
        }
        
        fig.add_trace(
            go.Pie(
                labels=list(thresholds.keys()),
                values=list(thresholds.values()),
                name="Ajustements",
                marker_colors=['rgb(148, 103, 189)', 'rgb(140, 86, 75)', 'rgb(227, 119, 194)']
            ),
            row=2, col=1
        )

        # Tags les plus communs (exemple)
        tags = {
            "security": 25,
            "performance": 20,
            "code_quality": 18,
            "documentation": 15,
            "architecture": 12
        }
        
        fig.add_trace(
            go.Bar(
                x=list(tags.keys()),
                y=list(tags.values()),
                name="Tags",
                marker_color='rgb(127, 127, 127)'
            ),
            row=2, col=2
        )

        fig.update_layout(
            height=800,
            title_text="Analyse des Règles",
            showlegend=False
        )

        return fig

    def generate_dashboard(self, metrics: Dict[str, Any]) -> None:
        """Génère un dashboard complet avec tous les graphiques."""
        # Créer les graphiques
        cache_fig = self._create_cache_performance_plot(metrics.get("cache", {}))
        validation_fig = self._create_validation_performance_plot(metrics)
        rules_fig = self._create_rules_analysis_plot(metrics.get("rules", {}))
        
        # Créer le HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Métriques de Validation - {timestamp}</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .plot {{ margin-bottom: 30px; }}
                h1 {{ color: #2c3e50; }}
                .summary {{ 
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .metric {{ 
                    display: inline-block;
                    margin-right: 20px;
                    padding: 10px;
                    background-color: #ffffff;
                    border: 1px solid #dee2e6;
                    border-radius: 3px;
                }}
            </style>
        </head>
        <body>
            <h1>Dashboard des Métriques de Validation</h1>
            
            <div class="summary">
                <h2>Résumé</h2>
                <div class="metric">
                    <strong>Status:</strong> {metrics.get("validation", {}).get("status", "N/A")}
                </div>
                <div class="metric">
                    <strong>Alertes Actives:</strong> {metrics.get("validation", {}).get("active_alerts", 0)}
                </div>
                <div class="metric">
                    <strong>Règles Totales:</strong> {metrics.get("rules", {}).get("total", 0)}
                </div>
            </div>
            
            <div class="plot">
                <div id="cache_performance"></div>
            </div>
            
            <div class="plot">
                <div id="validation_performance"></div>
            </div>
            
            <div class="plot">
                <div id="rules_analysis"></div>
            </div>
            
            <script>
                {cache_fig.to_json()}
                Plotly.newPlot('cache_performance', cache_fig.data, cache_fig.layout);
                
                {validation_fig.to_json()}
                Plotly.newPlot('validation_performance', validation_fig.data, validation_fig.layout);
                
                {rules_fig.to_json()}
                Plotly.newPlot('rules_analysis', rules_fig.data, rules_fig.layout);
            </script>
        </body>
        </html>
        """
        
        # Sauvegarder le dashboard
        output_file = os.path.join(self.export_dir, f"dashboard_{timestamp}.html")
        with open(output_file, "w") as f:
            f.write(html_content)
        
        print(f"Dashboard généré : {output_file}")

    def update_dashboard(self, rules_manager) -> None:
        """Met à jour le dashboard avec les dernières métriques."""
        metrics = rules_manager.get_metrics()
        self.generate_dashboard(metrics)
