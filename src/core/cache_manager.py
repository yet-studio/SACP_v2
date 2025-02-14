"""
Cache Manager for optimizing validation and rule processing.
Implements LRU cache with TTL and monitoring capabilities.
"""
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from collections import OrderedDict
import threading
import json
import logging

logger = logging.getLogger(__name__)

class CacheEntry:
    """Entrée de cache avec TTL et métadonnées."""
    def __init__(self, value: Any, ttl: timedelta):
        self.value = value
        self.created_at = datetime.now()
        self.ttl = ttl
        self.hits = 0
        self.last_accessed = self.created_at

    def is_expired(self) -> bool:
        """Vérifie si l'entrée est expirée."""
        return datetime.now() - self.created_at > self.ttl

    def access(self) -> None:
        """Enregistre un accès à l'entrée."""
        self.hits += 1
        self.last_accessed = datetime.now()

    def to_dict(self) -> Dict:
        """Convertit l'entrée en dictionnaire pour la sérialisation."""
        return {
            'value': self.value,
            'created_at': self.created_at.isoformat(),
            'ttl': self.ttl.total_seconds(),
            'hits': self.hits,
            'last_accessed': self.last_accessed.isoformat()
        }

class ValidationCache:
    """Cache LRU avec TTL pour les résultats de validation."""
    
    def __init__(self, maxsize: int = 1000, ttl: timedelta = timedelta(minutes=30)):
        self.maxsize = maxsize
        self.default_ttl = ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.Lock()
        self.metrics = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'size': 0
        }
        self._start_cleanup_thread()

    def _start_cleanup_thread(self) -> None:
        """Démarre le thread de nettoyage périodique."""
        def cleanup():
            while True:
                self._cleanup_expired()
                threading.Event().wait(300)  # Nettoyage toutes les 5 minutes

        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()

    def _cleanup_expired(self) -> None:
        """Nettoie les entrées expirées."""
        with self.lock:
            expired = [k for k, v in self.cache.items() if v.is_expired()]
            for key in expired:
                self.cache.pop(key)
                self.metrics['evictions'] += 1
                self.metrics['size'] = len(self.cache)
                logger.debug(f"Expired cache entry removed: {key}")

    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache."""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                if entry.is_expired():
                    self.cache.pop(key)
                    self.metrics['evictions'] += 1
                    self.metrics['size'] = len(self.cache)
                    self.metrics['misses'] += 1
                    return None
                
                entry.access()
                self.cache.move_to_end(key)
                self.metrics['hits'] += 1
                return entry.value
            
            self.metrics['misses'] += 1
            return None

    def set(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> None:
        """Ajoute ou met à jour une valeur dans le cache."""
        with self.lock:
            if len(self.cache) >= self.maxsize:
                _, _ = self.cache.popitem(last=False)
                self.metrics['evictions'] += 1

            self.cache[key] = CacheEntry(value, ttl or self.default_ttl)
            self.cache.move_to_end(key)
            self.metrics['size'] = len(self.cache)

    def clear(self) -> None:
        """Vide le cache."""
        with self.lock:
            self.cache.clear()
            self.metrics['size'] = 0
            self.metrics['evictions'] += 1

    def get_metrics(self) -> Dict:
        """Récupère les métriques du cache."""
        with self.lock:
            total_requests = self.metrics['hits'] + self.metrics['misses']
            hit_rate = (self.metrics['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self.metrics,
                'hit_rate': hit_rate,
                'entries': [
                    {
                        'key': key,
                        **entry.to_dict()
                    }
                    for key, entry in self.cache.items()
                ]
            }

class ValidationCacheManager:
    """Gestionnaire de cache pour différents types de validation."""
    
    def __init__(self):
        # Optimisation des TTL par type de validation :
        
        # Code : Cache court car le code change fréquemment
        # Taille moyenne car beaucoup de validations de code
        self.caches = {
            'code': ValidationCache(
                maxsize=1000,
                ttl=timedelta(minutes=15)
            ),
            
            # Architecture : Cache long car les patterns changent peu
            # Petite taille car moins de validations
            'architecture': ValidationCache(
                maxsize=200,
                ttl=timedelta(hours=4)
            ),
            
            # Documentation : Cache moyen car la doc est mise à jour périodiquement
            # Taille moyenne
            'documentation': ValidationCache(
                maxsize=500,
                ttl=timedelta(hours=1)
            ),
            
            # Sécurité : Cache court car critique
            # Grande taille car beaucoup de patterns à vérifier
            'security': ValidationCache(
                maxsize=2000,
                ttl=timedelta(minutes=30)
            ),
            
            # Performance : Cache moyen car les métriques sont relativement stables
            # Taille moyenne
            'performance': ValidationCache(
                maxsize=500,
                ttl=timedelta(hours=1)
            )
        }
        
        # Métriques d'efficacité du cache
        self.efficiency_thresholds = {
            'hit_rate_min': 0.7,  # 70% minimum de hit rate
            'eviction_rate_max': 0.1,  # 10% maximum d'évictions
            'size_threshold': 0.8  # Alerte à 80% de remplissage
        }

    def optimize_cache_size(self, cache_type: str) -> None:
        """Optimise la taille du cache basé sur les métriques."""
        cache = self.caches[cache_type]
        metrics = cache.get_metrics()
        
        current_size = metrics['size']
        max_size = cache.maxsize
        hit_rate = metrics['hit_rate']
        eviction_rate = metrics['evictions'] / (metrics['hits'] + metrics['misses'])
        
        # Ajuster la taille si nécessaire
        if hit_rate < self.efficiency_thresholds['hit_rate_min']:
            # Augmenter la taille si trop de miss
            new_size = int(max_size * 1.2)  # +20%
            cache.maxsize = min(new_size, max_size * 2)
        
        elif eviction_rate > self.efficiency_thresholds['eviction_rate_max']:
            # Augmenter la taille si trop d'évictions
            new_size = int(max_size * 1.5)  # +50%
            cache.maxsize = min(new_size, max_size * 2)
        
        elif current_size < max_size * 0.3:
            # Réduire la taille si sous-utilisé
            new_size = int(max_size * 0.8)  # -20%
            cache.maxsize = max(new_size, 100)

    def get_cache(self, cache_type: str) -> ValidationCache:
        """Récupère un cache spécifique."""
        if cache_type not in self.caches:
            raise ValueError(f"Unknown cache type: {cache_type}")
        return self.caches[cache_type]

    def get_all_metrics(self) -> Dict:
        """Récupère les métriques de tous les caches."""
        return {
            cache_type: cache.get_metrics()
            for cache_type, cache in self.caches.items()
        }

    def clear_all(self) -> None:
        """Vide tous les caches."""
        for cache in self.caches.values():
            cache.clear()

    def export_metrics(self, file_path: str) -> None:
        """Exporte les métriques dans un fichier JSON."""
        metrics = self.get_all_metrics()
        with open(file_path, 'w') as f:
            json.dump(metrics, f, indent=2)
