# Chaos Testing Branch

**Branch**: `chaos-testing`  
**Purpose**: Safe testing environment for Chaos server deployment  
**Base**: Chaos branch  

## Overview

This branch is designed for testing all Chaos optimizations and custom features in a safe environment before deploying to your live server.

## What's Included

### 🚀 Core Chaos Features
- **Multi-level caching system** for database and script optimization
- **Enhanced RO Agent** with architecture-aware management
- **Performance monitoring** and metrics collection  
- **Automated branch synchronization** with upstream rAthena
- **Advanced debugging** and development tools

### 🛠️ Testing Configuration
- Pre-configured for development/testing environment
- Debug logging enabled
- Performance profiling active
- Cache system in test mode
- All safety checks enabled

## Quick Start Testing

### 1. Verify RO Agent
```bash
python "Ragnarok Online Agent/src/cli.py" status
python "Ragnarok Online Agent/src/cli.py" ask "rathena setup"
```

### 2. Test Caching System
```bash
python "Ragnarok Online Agent/src/cli.py" ask "performance guide"
```

### 3. Check Server Configuration
```bash
# Verify configuration files
python "Ragnarok Online Agent/src/cli.py" files organize --type configs
```

## Testing Checklist

### Pre-Deployment Testing
- [ ] **RO Agent Functionality**
  - [ ] CLI commands work properly
  - [ ] Knowledge base responds correctly
  - [ ] Architecture detection works
  - [ ] Performance guides accessible

- [ ] **Caching System**
  - [ ] L1 memory cache functional
  - [ ] L2 database cache operational  
  - [ ] L3 file cache working
  - [ ] Cache statistics accurate
  - [ ] Automatic cleanup functions

- [ ] **Server Components**
  - [ ] Login server compiles and starts
  - [ ] Character server compiles and starts
  - [ ] Map server compiles and starts
  - [ ] Inter-server communication works
  - [ ] Database connectivity confirmed

- [ ] **Performance Monitoring**
  - [ ] Metrics collection active
  - [ ] Performance logs generated
  - [ ] Resource usage monitored
  - [ ] Bottlenecks identified

### Deployment Validation
- [ ] **Custom Features**
  - [ ] All Chaos optimizations active
  - [ ] No performance regression
  - [ ] Memory usage within limits
  - [ ] Custom scripts functional

- [ ] **Integration Testing**
  - [ ] Client connectivity confirmed
  - [ ] Player login/logout works
  - [ ] Game mechanics functional
  - [ ] Custom content accessible

## Performance Benchmarks

### Baseline Targets (Testing Environment)
- **Login Server**: < 10ms response time
- **Character Server**: < 50ms character load time  
- **Map Server**: < 100ms map transition time
- **Database Queries**: < 5ms average (with cache)
- **Memory Usage**: < 2GB total server footprint

### Cache Performance Targets
- **L1 Hit Ratio**: > 80%
- **L2 Hit Ratio**: > 60%  
- **Cache Miss Penalty**: < 2x uncached time
- **Cache Cleanup**: < 1% CPU overhead

## Troubleshooting

### Common Issues
1. **Cache Directory Permissions**
   ```bash
   # Ensure cache directory is writable
   chmod -R 755 "Ragnarok Online Agent/ANALYSIS_CACHE/"
   ```

2. **Python Dependencies**
   ```bash
   # Reinstall if needed
   cd "Ragnarok Online Agent"
   pip install -r requirements.txt
   ```

3. **Database Connection**
   ```bash
   # Test database connectivity
   python "Ragnarok Online Agent/src/cli.py" ask "database setup"
   ```

### Debug Mode
Enable detailed logging by editing `ro_agent_config.yml`:
```yaml
debug:
  enabled: true
  log_level: DEBUG
  performance_logging: true
  cache_debug: true
```

## Performance Monitoring

### Real-time Monitoring
```bash
# Monitor server performance
python "Ragnarok Online Agent/src/cli.py" ask "performance monitoring"

# Check cache statistics
python -c "
from pathlib import Path
import sys
sys.path.append('Ragnarok Online Agent/src')
from cache_manager import CacheManager
cache = CacheManager(Path('Ragnarok Online Agent/ANALYSIS_CACHE'))
print('Cache Stats:', cache.get_stats())
"
```

### Log Analysis
- **Server logs**: `log/` directory
- **Cache performance**: `Ragnarok Online Agent/ANALYSIS_CACHE/performance.log`
- **RO Agent logs**: `Ragnarok Online Agent/ANALYSIS_CACHE/agent.log`

## Branch Management

### Sync with Chaos Branch
```bash
# Get latest Chaos updates
git checkout chaos
git pull origin chaos
git checkout chaos-testing
git merge chaos
```

### Deploy to Production
After successful testing:
```bash
# Create production-ready branch
git checkout chaos
git merge chaos-testing
git tag chaos-v1.0-$(date +%Y%m%d)
git push origin chaos --tags
```

## Safety Features

### Automatic Backups
- Database snapshots before major operations
- Configuration file versioning
- Cache data preservation
- Log rotation and archival

### Rollback Procedures
1. **Quick Rollback**: Switch back to Chaos branch
2. **Config Rollback**: Restore from `conf/backup/`
3. **Database Rollback**: Restore from automated snapshots
4. **Cache Rollback**: Clear cache and regenerate

## Support

### Getting Help
```bash
# RO Agent help system
python "Ragnarok Online Agent/src/cli.py" ask "troubleshooting"

# Architecture information  
python "Ragnarok Online Agent/src/cli.py" ask "architecture"

# Performance tuning
python "Ragnarok Online Agent/src/cli.py" ask "performance optimization"
```

### Documentation
- **Architecture**: `Ragnarok Online Agent/ANALYSIS_CACHE/rathena_architecture.yml`
- **Branch Strategy**: `Ragnarok Online Agent/ANALYSIS_CACHE/branch_strategy.yml`
- **Performance Guide**: Available via RO Agent knowledge base

---

**⚠️ Testing Environment Notice**  
This branch contains experimental optimizations. Always test thoroughly before production deployment.

**✅ Ready for Testing**  
All Chaos features are active and ready for comprehensive testing.