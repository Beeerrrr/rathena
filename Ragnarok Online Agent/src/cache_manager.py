"""
Advanced Caching System for rAthena Performance Optimization
Implements multi-level caching for database queries, script results, and system data
"""

import json
import pickle
import sqlite3
import hashlib
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from collections import OrderedDict
import yaml

class CacheManager:
    """Multi-level cache manager for rAthena optimization"""
    
    def __init__(self, cache_dir: Path, max_memory_mb: int = 100):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # L1 Cache: In-memory LRU cache
        self.max_memory_entries = (max_memory_mb * 1024 * 1024) // 1024  # Approximate
        self.memory_cache = OrderedDict()
        self.cache_stats = {
            'hits': 0, 'misses': 0, 'evictions': 0,
            'memory_size': 0, 'disk_size': 0
        }
        
        # L2 Cache: Persistent SQLite database
        self.db_path = self.cache_dir / "cache.db"
        self._init_database()
        
        # L3 Cache: File-based cache for large objects
        self.file_cache_dir = self.cache_dir / "files"
        self.file_cache_dir.mkdir(exist_ok=True)
        
        # Cache configuration
        self.config = self._load_cache_config()
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Performance monitoring
        self.performance_log = self.cache_dir / "performance.log"
        
    def _load_cache_config(self) -> Dict:
        """Load cache configuration"""
        config_file = self.cache_dir.parent / "ro_agent_config.yml"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    return config.get('cache', {
                        'ttl_default': 3600,  # 1 hour
                        'ttl_database': 1800,  # 30 minutes
                        'ttl_scripts': 7200,   # 2 hours
                        'ttl_static': 86400,   # 24 hours
                        'auto_cleanup': True,
                        'compression': True
                    })
            except Exception as e:
                print(f"Warning: Could not load cache config: {e}")
        
        return {
            'ttl_default': 3600,
            'ttl_database': 1800,
            'ttl_scripts': 7200,
            'ttl_static': 86400,
            'auto_cleanup': True,
            'compression': True
        }
    
    def _init_database(self):
        """Initialize SQLite cache database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    value BLOB,
                    created_at REAL,
                    expires_at REAL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed REAL,
                    category TEXT,
                    size INTEGER
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_entries(expires_at)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_category ON cache_entries(category)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)
            """)
    
    def _generate_key(self, namespace: str, key: str, *args) -> str:
        """Generate cache key with namespace and arguments"""
        if args:
            key_data = f"{namespace}:{key}:{':'.join(map(str, args))}"
        else:
            key_data = f"{namespace}:{key}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:32]
    
    def get(self, namespace: str, key: str, *args) -> Optional[Any]:
        """Get value from cache (L1 -> L2 -> L3)"""
        cache_key = self._generate_key(namespace, key, *args)
        
        with self._lock:
            # L1: Memory cache
            if cache_key in self.memory_cache:
                value, expires_at = self.memory_cache[cache_key]
                if time.time() < expires_at:
                    # Move to end (LRU)
                    self.memory_cache.move_to_end(cache_key)
                    self.cache_stats['hits'] += 1
                    self._log_performance('L1_HIT', namespace, key)
                    return value
                else:
                    # Expired
                    del self.memory_cache[cache_key]
            
            # L2: Database cache
            db_value = self._get_from_database(cache_key)
            if db_value is not None:
                # Promote to L1
                expires_at = db_value[1]
                self._set_memory_cache(cache_key, db_value[0], expires_at)
                self.cache_stats['hits'] += 1
                self._log_performance('L2_HIT', namespace, key)
                return db_value[0]
            
            # L3: File cache
            file_value = self._get_from_file_cache(cache_key)
            if file_value is not None:
                # Promote to L1 and L2
                expires_at = file_value[1]
                self._set_memory_cache(cache_key, file_value[0], expires_at)
                self._set_database_cache(cache_key, file_value[0], expires_at, namespace)
                self.cache_stats['hits'] += 1
                self._log_performance('L3_HIT', namespace, key)
                return file_value[0]
            
            self.cache_stats['misses'] += 1
            self._log_performance('MISS', namespace, key)
            return None
    
    def set(self, namespace: str, key: str, value: Any, ttl: Optional[int] = None, *args):
        """Set value in cache"""
        if ttl is None:
            ttl = self.config.get(f'ttl_{namespace}', self.config['ttl_default'])
        
        cache_key = self._generate_key(namespace, key, *args)
        expires_at = time.time() + ttl
        
        with self._lock:
            # Determine cache level based on size
            value_size = self._estimate_size(value)
            
            if value_size < 1024:  # < 1KB: L1 (memory)
                self._set_memory_cache(cache_key, value, expires_at)
                self._log_performance('L1_SET', namespace, key, value_size)
                
            elif value_size < 1024 * 1024:  # < 1MB: L2 (database)
                self._set_database_cache(cache_key, value, expires_at, namespace, value_size)
                self._log_performance('L2_SET', namespace, key, value_size)
                
            else:  # >= 1MB: L3 (file)
                self._set_file_cache(cache_key, value, expires_at, namespace)
                self._log_performance('L3_SET', namespace, key, value_size)
    
    def _set_memory_cache(self, key: str, value: Any, expires_at: float):
        """Set value in L1 memory cache"""
        self.memory_cache[key] = (value, expires_at)
        
        # LRU eviction
        while len(self.memory_cache) > self.max_memory_entries:
            oldest_key = next(iter(self.memory_cache))
            del self.memory_cache[oldest_key]
            self.cache_stats['evictions'] += 1
    
    def _set_database_cache(self, key: str, value: Any, expires_at: float, 
                          category: str, size: int = 0):
        """Set value in L2 database cache"""
        try:
            serialized = pickle.dumps(value)
            current_time = time.time()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO cache_entries 
                    (key, value, created_at, expires_at, category, size, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (key, serialized, current_time, expires_at, category, 
                     size or len(serialized), current_time))
        except Exception as e:
            print(f"Database cache error: {e}")
    
    def _set_file_cache(self, key: str, value: Any, expires_at: float, category: str):
        """Set value in L3 file cache"""
        try:
            cache_file = self.file_cache_dir / f"{key}.cache"
            cache_meta = self.file_cache_dir / f"{key}.meta"
            
            # Save data
            if self.config.get('compression', True):
                import gzip
                with gzip.open(cache_file, 'wb') as f:
                    pickle.dump(value, f)
            else:
                with open(cache_file, 'wb') as f:
                    pickle.dump(value, f)
            
            # Save metadata
            metadata = {
                'expires_at': expires_at,
                'created_at': time.time(),
                'category': category,
                'size': cache_file.stat().st_size,
                'compressed': self.config.get('compression', True)
            }
            
            with open(cache_meta, 'w') as f:
                json.dump(metadata, f)
                
        except Exception as e:
            print(f"File cache error: {e}")
    
    def _get_from_database(self, key: str) -> Optional[Tuple[Any, float]]:
        """Get value from L2 database cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT value, expires_at FROM cache_entries 
                    WHERE key = ? AND expires_at > ?
                """, (key, time.time()))
                
                row = cursor.fetchone()
                if row:
                    # Update access stats
                    conn.execute("""
                        UPDATE cache_entries 
                        SET access_count = access_count + 1, last_accessed = ?
                        WHERE key = ?
                    """, (time.time(), key))
                    
                    return pickle.loads(row[0]), row[1]
                    
        except Exception as e:
            print(f"Database cache retrieval error: {e}")
        
        return None
    
    def _get_from_file_cache(self, key: str) -> Optional[Tuple[Any, float]]:
        """Get value from L3 file cache"""
        try:
            cache_file = self.file_cache_dir / f"{key}.cache"
            cache_meta = self.file_cache_dir / f"{key}.meta"
            
            if not cache_file.exists() or not cache_meta.exists():
                return None
            
            # Check metadata
            with open(cache_meta, 'r') as f:
                metadata = json.load(f)
            
            if time.time() > metadata['expires_at']:
                # Expired - clean up
                cache_file.unlink(missing_ok=True)
                cache_meta.unlink(missing_ok=True)
                return None
            
            # Load data
            if metadata.get('compressed', False):
                import gzip
                with gzip.open(cache_file, 'rb') as f:
                    value = pickle.load(f)
            else:
                with open(cache_file, 'rb') as f:
                    value = pickle.load(f)
            
            return value, metadata['expires_at']
            
        except Exception as e:
            print(f"File cache retrieval error: {e}")
        
        return None
    
    def invalidate(self, namespace: str, key: str = None, *args):
        """Invalidate cache entries"""
        with self._lock:
            if key:
                cache_key = self._generate_key(namespace, key, *args)
                
                # L1
                self.memory_cache.pop(cache_key, None)
                
                # L2
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("DELETE FROM cache_entries WHERE key = ?", (cache_key,))
                except Exception as e:
                    print(f"Database invalidation error: {e}")
                
                # L3
                cache_file = self.file_cache_dir / f"{cache_key}.cache"
                cache_meta = self.file_cache_dir / f"{cache_key}.meta"
                cache_file.unlink(missing_ok=True)
                cache_meta.unlink(missing_ok=True)
                
            else:
                # Invalidate entire namespace
                self._invalidate_namespace(namespace)
    
    def _invalidate_namespace(self, namespace: str):
        """Invalidate all entries in a namespace"""
        # L1: Remove by pattern (approximate)
        keys_to_remove = []
        for key in self.memory_cache:
            if key.startswith(namespace):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.memory_cache[key]
        
        # L2: Remove by category
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM cache_entries WHERE category = ?", (namespace,))
        except Exception as e:
            print(f"Database namespace invalidation error: {e}")
        
        # L3: Remove files by metadata
        for meta_file in self.file_cache_dir.glob("*.meta"):
            try:
                with open(meta_file, 'r') as f:
                    metadata = json.load(f)
                
                if metadata.get('category') == namespace:
                    cache_key = meta_file.stem
                    cache_file = self.file_cache_dir / f"{cache_key}.cache"
                    cache_file.unlink(missing_ok=True)
                    meta_file.unlink(missing_ok=True)
                    
            except Exception as e:
                print(f"File cache namespace invalidation error: {e}")
    
    def cleanup_expired(self):
        """Clean up expired cache entries"""
        current_time = time.time()
        
        with self._lock:
            # L1: Memory cache
            expired_keys = []
            for key, (value, expires_at) in self.memory_cache.items():
                if current_time > expires_at:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.memory_cache[key]
            
            # L2: Database cache
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM cache_entries WHERE expires_at < ?", (current_time,))
            except Exception as e:
                print(f"Database cleanup error: {e}")
            
            # L3: File cache
            for meta_file in self.file_cache_dir.glob("*.meta"):
                try:
                    with open(meta_file, 'r') as f:
                        metadata = json.load(f)
                    
                    if current_time > metadata['expires_at']:
                        cache_key = meta_file.stem
                        cache_file = self.file_cache_dir / f"{cache_key}.cache"
                        cache_file.unlink(missing_ok=True)
                        meta_file.unlink(missing_ok=True)
                        
                except Exception as e:
                    print(f"File cache cleanup error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            stats = self.cache_stats.copy()
            
            # Calculate hit ratio
            total_requests = stats['hits'] + stats['misses']
            stats['hit_ratio'] = stats['hits'] / total_requests if total_requests > 0 else 0
            
            # Memory usage
            stats['memory_entries'] = len(self.memory_cache)
            
            # Database stats
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("SELECT COUNT(*), SUM(size) FROM cache_entries")
                    db_count, db_size = cursor.fetchone()
                    stats['database_entries'] = db_count or 0
                    stats['database_size'] = db_size or 0
            except Exception as e:
                stats['database_entries'] = 0
                stats['database_size'] = 0
            
            # File cache stats
            file_count = len(list(self.file_cache_dir.glob("*.cache")))
            file_size = sum(f.stat().st_size for f in self.file_cache_dir.glob("*.cache"))
            stats['file_entries'] = file_count
            stats['file_size'] = file_size
            
            return stats
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate size of value in bytes"""
        try:
            return len(pickle.dumps(value))
        except:
            # Fallback estimation
            import sys
            return sys.getsizeof(value)
    
    def _log_performance(self, operation: str, namespace: str, key: str, size: int = 0):
        """Log cache performance for analysis"""
        if not self.config.get('performance_logging', False):
            return
        
        try:
            timestamp = datetime.now().isoformat()
            log_entry = f"{timestamp},{operation},{namespace},{key},{size}\n"
            
            with open(self.performance_log, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Performance logging error: {e}")

# Convenience functions for common rAthena cache patterns

def cache_database_query(cache_manager: CacheManager, query_hash: str, 
                        result: Any, ttl: int = 1800):
    """Cache database query result"""
    cache_manager.set('database', query_hash, result, ttl)

def get_cached_database_query(cache_manager: CacheManager, query_hash: str) -> Optional[Any]:
    """Get cached database query result"""
    return cache_manager.get('database', query_hash)

def cache_script_result(cache_manager: CacheManager, script_path: str, 
                       result: Any, ttl: int = 7200):
    """Cache NPC script compilation result"""
    cache_manager.set('scripts', script_path, result, ttl)

def get_cached_script_result(cache_manager: CacheManager, script_path: str) -> Optional[Any]:
    """Get cached NPC script compilation result"""
    return cache_manager.get('scripts', script_path)

def cache_item_data(cache_manager: CacheManager, item_id: int, 
                   data: Any, ttl: int = 86400):
    """Cache item database data"""
    cache_manager.set('items', str(item_id), data, ttl)

def get_cached_item_data(cache_manager: CacheManager, item_id: int) -> Optional[Any]:
    """Get cached item database data"""
    return cache_manager.get('items', str(item_id))

def cache_monster_data(cache_manager: CacheManager, monster_id: int, 
                      data: Any, ttl: int = 86400):
    """Cache monster database data"""
    cache_manager.set('monsters', str(monster_id), data, ttl)

def get_cached_monster_data(cache_manager: CacheManager, monster_id: int) -> Optional[Any]:
    """Get cached monster database data"""
    return cache_manager.get('monsters', str(monster_id))