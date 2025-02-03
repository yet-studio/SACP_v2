"""
Monitoring system for tracking AI validation and performance metrics.
Implements real-time monitoring, alerting, and metric collection.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import threading
import logging
import json
import os
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class MetricValue:
    value: float
    timestamp: datetime
    labels: Dict[str, str]

@dataclass
class Alert:
    severity: AlertSeverity
    message: str
    timestamp: datetime
    context: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class MetricCollector:
    """Collecteur de métriques avec support pour différents types."""
    
    def __init__(self):
        self.metrics: Dict[str, List[MetricValue]] = {}
        self.metric_types: Dict[str, MetricType] = {}
        self.lock = threading.Lock()

    def register_metric(self, name: str, metric_type: MetricType) -> None:
        """Enregistre une nouvelle métrique."""
        with self.lock:
            if name not in self.metrics:
                self.metrics[name] = []
                self.metric_types[name] = metric_type

    def record(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Enregistre une valeur pour une métrique."""
        with self.lock:
            if name not in self.metrics:
                raise ValueError(f"Metric {name} not registered")
            
            self.metrics[name].append(MetricValue(
                value=value,
                timestamp=datetime.now(),
                labels=labels or {}
            ))

    def get_values(self, name: str, 
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None) -> List[MetricValue]:
        """Récupère les valeurs d'une métrique sur une période."""
        with self.lock:
            if name not in self.metrics:
                return []
            
            values = self.metrics[name]
            if start_time:
                values = [v for v in values if v.timestamp >= start_time]
            if end_time:
                values = [v for v in values if v.timestamp <= end_time]
            
            return values

class AlertManager:
    """Gestionnaire d'alertes avec support pour différentes sévérités."""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.lock = threading.Lock()
        self.handlers: Dict[AlertSeverity, List[callable]] = {
            severity: [] for severity in AlertSeverity
        }

    def add_handler(self, severity: AlertSeverity, handler: callable) -> None:
        """Ajoute un handler pour un niveau de sévérité."""
        with self.lock:
            self.handlers[severity].append(handler)

    def trigger_alert(self, severity: AlertSeverity, message: str, 
                     context: Dict[str, Any] = None) -> None:
        """Déclenche une nouvelle alerte."""
        alert = Alert(
            severity=severity,
            message=message,
            timestamp=datetime.now(),
            context=context or {}
        )
        
        with self.lock:
            self.alerts.append(alert)
            for handler in self.handlers[severity]:
                try:
                    handler(alert)
                except Exception as e:
                    logger.error(f"Error in alert handler: {e}")

    def resolve_alert(self, alert: Alert) -> None:
        """Marque une alerte comme résolue."""
        with self.lock:
            alert.resolved = True
            alert.resolved_at = datetime.now()

    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Récupère les alertes actives."""
        with self.lock:
            alerts = [a for a in self.alerts if not a.resolved]
            if severity:
                alerts = [a for a in alerts if a.severity == severity]
            return alerts

class MonitoringSystem:
    """Système de monitoring principal."""
    
    def __init__(self, export_dir: str = "monitoring"):
        self.metrics = MetricCollector()
        self.alerts = AlertManager()
        self.export_dir = export_dir
        self._setup_default_metrics()
        self._setup_default_handlers()
        
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

    def _setup_default_metrics(self) -> None:
        """Configure les métriques par défaut."""
        # Performance
        self.metrics.register_metric("validation_duration", MetricType.HISTOGRAM)
        self.metrics.register_metric("cache_hit_rate", MetricType.GAUGE)
        self.metrics.register_metric("memory_usage", MetricType.GAUGE)
        
        # Validation
        self.metrics.register_metric("validation_success", MetricType.COUNTER)
        self.metrics.register_metric("validation_failure", MetricType.COUNTER)
        self.metrics.register_metric("pattern_recognition_accuracy", MetricType.GAUGE)
        
        # Sécurité
        self.metrics.register_metric("security_issues", MetricType.COUNTER)
        self.metrics.register_metric("vulnerability_score", MetricType.GAUGE)

    def _setup_default_handlers(self) -> None:
        """Configure les handlers d'alerte par défaut."""
        def log_alert(alert: Alert) -> None:
            logger.log(
                logging.CRITICAL if alert.severity == AlertSeverity.CRITICAL else
                logging.ERROR if alert.severity == AlertSeverity.ERROR else
                logging.WARNING if alert.severity == AlertSeverity.WARNING else
                logging.INFO,
                f"Alert: {alert.message}"
            )

        for severity in AlertSeverity:
            self.alerts.add_handler(severity, log_alert)

    def record_validation(self, duration: float, success: bool, 
                         context: Dict[str, Any]) -> None:
        """Enregistre une validation."""
        self.metrics.record("validation_duration", duration)
        self.metrics.record(
            "validation_success" if success else "validation_failure",
            1,
            context
        )

    def record_security_issue(self, severity: str, issue_type: str,
                            context: Dict[str, Any]) -> None:
        """Enregistre un problème de sécurité."""
        self.metrics.record("security_issues", 1, {
            "severity": severity,
            "type": issue_type
        })
        
        if severity in ["high", "critical"]:
            self.alerts.trigger_alert(
                AlertSeverity.CRITICAL,
                f"Security issue detected: {issue_type}",
                context
            )

    def export_metrics(self) -> None:
        """Exporte les métriques dans un fichier JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metrics_file = os.path.join(self.export_dir, f"metrics_{timestamp}.json")
        
        with open(metrics_file, 'w') as f:
            json.dump({
                name: [asdict(v) for v in values]
                for name, values in self.metrics.metrics.items()
            }, f, indent=2, default=str)

    def get_health_status(self) -> Dict[str, Any]:
        """Récupère le statut de santé du système."""
        active_alerts = self.alerts.get_active_alerts()
        critical_alerts = [a for a in active_alerts 
                         if a.severity == AlertSeverity.CRITICAL]
        
        return {
            "status": "critical" if critical_alerts else
                     "warning" if active_alerts else "healthy",
            "active_alerts": len(active_alerts),
            "critical_alerts": len(critical_alerts),
            "metrics_collected": len(self.metrics.metrics),
            "last_update": datetime.now().isoformat()
        }
