"""
Tests for the cache management system.
"""
import pytest
from datetime import timedelta
import time
from src.core.cache_manager import ValidationCache, ValidationCacheManager, CacheEntry

@pytest.fixture
def cache():
    return ValidationCache(maxsize=3, ttl=timedelta(seconds=1))

@pytest.fixture
def cache_manager():
    return ValidationCacheManager()

class TestValidationCache:
    def test_basic_operations(self, cache):
        """Test les opérations basiques du cache."""
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None

    def test_lru_eviction(self, cache):
        """Test l'éviction LRU."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        cache.set("key4", "value4")  # Devrait évincer key1
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_ttl_expiration(self, cache):
        """Test l'expiration TTL."""
        cache.set("key1", "value1")
        time.sleep(1.1)  # Attendre l'expiration
        assert cache.get("key1") is None

    def test_metrics(self, cache):
        """Test la collecte de métriques."""
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        
        metrics = cache.get_metrics()
        assert metrics["hits"] == 1
        assert metrics["misses"] == 1
        assert metrics["size"] == 1

class TestValidationCacheManager:
    def test_cache_types(self, cache_manager):
        """Test les différents types de cache."""
        pattern_cache = cache_manager.get_cache("pattern")
        security_cache = cache_manager.get_cache("security")
        
        pattern_cache.set("key1", "value1")
        security_cache.set("key1", "value2")
        
        assert pattern_cache.get("key1") == "value1"
        assert security_cache.get("key1") == "value2"

    def test_clear_all(self, cache_manager):
        """Test le nettoyage de tous les caches."""
        for cache_type in ["pattern", "security", "documentation"]:
            cache = cache_manager.get_cache(cache_type)
            cache.set("key1", "value1")
        
        cache_manager.clear_all()
        
        for cache_type in ["pattern", "security", "documentation"]:
            cache = cache_manager.get_cache(cache_type)
            assert cache.get("key1") is None

    def test_metrics_export(self, cache_manager, tmp_path):
        """Test l'export des métriques."""
        pattern_cache = cache_manager.get_cache("pattern")
        pattern_cache.set("key1", "value1")
        pattern_cache.get("key1")
        
        metrics_file = tmp_path / "metrics.json"
        cache_manager.export_metrics(str(metrics_file))
        
        assert metrics_file.exists()
        
    def test_invalid_cache_type(self, cache_manager):
        """Test la gestion des types de cache invalides."""
        with pytest.raises(ValueError):
            cache_manager.get_cache("invalid_type")
