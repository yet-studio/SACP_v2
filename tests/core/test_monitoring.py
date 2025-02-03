"""
Tests for the monitoring system.
"""
import pytest
from datetime import datetime, timedelta
import os
from src.core.monitoring import (
    MonitoringSystem, MetricType, AlertSeverity,
    MetricCollector, AlertManager, Alert
)

@pytest.fixture
def monitoring(tmp_path):
    return MonitoringSystem(export_dir=str(tmp_path))

@pytest.fixture
def metric_collector():
    return MetricCollector()

@pytest.fixture
def alert_manager():
    return AlertManager()

class TestMetricCollector:
    def test_metric_registration(self, metric_collector):
        """Test l'enregistrement des métriques."""
        metric_collector.register_metric("test_metric", MetricType.COUNTER)
        metric_collector.record("test_metric", 1.0)
        
        values = metric_collector.get_values("test_metric")
        assert len(values) == 1
        assert values[0].value == 1.0

    def test_invalid_metric(self, metric_collector):
        """Test la gestion des métriques non enregistrées."""
        with pytest.raises(ValueError):
            metric_collector.record("invalid_metric", 1.0)

    def test_metric_filtering(self, metric_collector):
        """Test le filtrage des métriques par période."""
        metric_collector.register_metric("test_metric", MetricType.COUNTER)
        
        now = datetime.now()
        start_time = now - timedelta(hours=1)
        end_time = now + timedelta(hours=1)
        
        metric_collector.record("test_metric", 1.0)
        values = metric_collector.get_values(
            "test_metric",
            start_time=start_time,
            end_time=end_time
        )
        assert len(values) == 1

class TestAlertManager:
    def test_alert_triggering(self, alert_manager):
        """Test le déclenchement d'alertes."""
        alert_manager.trigger_alert(
            AlertSeverity.WARNING,
            "Test alert"
        )
        
        alerts = alert_manager.get_active_alerts()
        assert len(alerts) == 1
        assert alerts[0].message == "Test alert"
        assert alerts[0].severity == AlertSeverity.WARNING

    def test_alert_resolution(self, alert_manager):
        """Test la résolution d'alertes."""
        alert_manager.trigger_alert(
            AlertSeverity.WARNING,
            "Test alert"
        )
        alert = alert_manager.get_active_alerts()[0]
        
        alert_manager.resolve_alert(alert)
        assert len(alert_manager.get_active_alerts()) == 0
        assert alert.resolved
        assert alert.resolved_at is not None

    def test_alert_handlers(self, alert_manager):
        """Test les handlers d'alerte."""
        handled_alerts = []
        
        def test_handler(alert):
            handled_alerts.append(alert)
        
        alert_manager.add_handler(AlertSeverity.ERROR, test_handler)
        alert_manager.trigger_alert(
            AlertSeverity.ERROR,
            "Test alert"
        )
        
        assert len(handled_alerts) == 1
        assert handled_alerts[0].severity == AlertSeverity.ERROR

class TestMonitoringSystem:
    def test_validation_recording(self, monitoring):
        """Test l'enregistrement des validations."""
        monitoring.record_validation(
            duration=0.5,
            success=True,
            context={"type": "pattern"}
        )
        
        values = monitoring.metrics.get_values("validation_duration")
        assert len(values) == 1
        assert values[0].value == 0.5

    def test_security_issue_recording(self, monitoring):
        """Test l'enregistrement des problèmes de sécurité."""
        monitoring.record_security_issue(
            severity="high",
            issue_type="vulnerability",
            context={"details": "Test vulnerability"}
        )
        
        values = monitoring.metrics.get_values("security_issues")
        assert len(values) == 1
        
        alerts = monitoring.alerts.get_active_alerts(AlertSeverity.CRITICAL)
        assert len(alerts) == 1

    def test_metrics_export(self, monitoring):
        """Test l'export des métriques."""
        monitoring.record_validation(
            duration=0.5,
            success=True,
            context={"type": "pattern"}
        )
        
        monitoring.export_metrics()
        export_files = os.listdir(monitoring.export_dir)
        assert len(export_files) == 1
        assert export_files[0].startswith("metrics_")

    def test_health_status(self, monitoring):
        """Test le statut de santé."""
        status = monitoring.get_health_status()
        assert status["status"] == "healthy"
        assert status["active_alerts"] == 0
        
        monitoring.record_security_issue(
            severity="critical",
            issue_type="vulnerability",
            context={"details": "Critical issue"}
        )
        
        status = monitoring.get_health_status()
        assert status["status"] == "critical"
        assert status["active_alerts"] == 1
        assert status["critical_alerts"] == 1
