# Trinitas Parallel Agents Deployment Checklist

## 📋 Pre-Deployment Checklist

### System Requirements
- [ ] **Claude CLI** installed and authenticated
- [ ] **Python 3.7+** available
- [ ] **jq** command available (recommended)
- [ ] **100MB+ free disk space**
- [ ] **Backup of existing ~/.claude directory**

### Environment Verification
```bash
# Run these commands to verify environment
claude --version
python3 --version
jq --version
df -h ~
```

## 🚀 Deployment Steps

### 1. Backup Current Configuration
```bash
# Create backup directory
mkdir -p ~/trinitas-backup-$(date +%Y%m%d)

# Backup existing Claude configuration
cp -r ~/.claude ~/trinitas-backup-$(date +%Y%m%d)/

# Verify backup
ls -la ~/trinitas-backup-$(date +%Y%m%d)/
```

### 2. Clone and Prepare Repository
```bash
# Clone repository
git clone https://github.com/apto-as/trinitas-agents.git
cd trinitas-agents

# Make scripts executable
find . -name "*.sh" -exec chmod +x {} \;
find . -name "*.py" -exec chmod +x {} \;
```

### 3. Run Pre-Flight Checks
```bash
# Test basic functionality
./hooks/tests/test_framework.sh

# Check for conflicts
python3 hooks/migration/settings_merger.py ~/.claude/settings.json --dry-run
```

### 4. Execute Safe Deployment
```bash
# Run deployment with safety checks
./deploy/safe_deploy.sh

# Follow prompts carefully
# Note the checkpoint directory for potential rollback
```

### 5. Post-Deployment Verification
```bash
# Run health check
~/.claude/trinitas/hooks/monitoring/health_check.sh

# Test parallel execution
./examples/parallel_analysis_demo.sh

# Monitor active sessions
~/.claude/trinitas/hooks/monitoring/session_monitor.sh status
```

## 🔄 Rollback Procedure

If issues occur:

### Immediate Rollback
```bash
# Use checkpoint from deployment
./deploy/safe_deploy.sh rollback <checkpoint_directory>
```

### Manual Rollback
```bash
# Restore from backup
rm -rf ~/.claude
cp -r ~/trinitas-backup-$(date +%Y%m%d)/.claude ~/

# Verify restoration
ls -la ~/.claude/
```

## ✅ Production Readiness Checklist

### Functionality Tests
- [ ] Protocol injection working (SessionStart/PreCompact)
- [ ] Parallel task preparation triggers correctly
- [ ] Result capture functioning
- [ ] Integration produces unified output
- [ ] Error handling works properly

### Performance Tests
- [ ] Response time acceptable (< 2x single agent)
- [ ] Memory usage stable
- [ ] Disk usage reasonable
- [ ] No resource leaks detected

### Monitoring Setup
- [ ] Health check automated (cron)
- [ ] Session monitoring configured
- [ ] Auto-recovery scheduled
- [ ] Log rotation working

### Documentation
- [ ] Team briefed on new features
- [ ] Support procedures documented
- [ ] Troubleshooting guide available
- [ ] Emergency contacts listed

## 🚨 Emergency Procedures

### High CPU/Memory Usage
```bash
# Kill all Claude processes
pkill -f claude

# Clean up sessions
~/.claude/trinitas/hooks/monitoring/session_monitor.sh cleanup
```

### Disk Space Issues
```bash
# Emergency cleanup
find ~/.claude/trinitas/parallel_results -mtime +1 -delete
python3 ~/.claude/trinitas/hooks/monitoring/auto_recovery.py --auto-fix
```

### Complete System Reset
```bash
# Remove Trinitas completely
rm -rf ~/.claude/trinitas

# Restore vanilla Claude
# Edit ~/.claude/settings.json and remove Trinitas hooks
```

## 📞 Support Contacts

- **GitHub Issues**: https://github.com/apto-as/trinitas-agents/issues
- **Documentation**: /docs directory in repository
- **Emergency Rollback**: Keep backup location noted

## 🎯 Success Criteria

Deployment is successful when:
1. ✅ All health checks pass
2. ✅ Demo execution completes without errors
3. ✅ No performance degradation observed
4. ✅ Monitoring shows healthy status
5. ✅ Team can use parallel agents effectively

---

**Remember**: Always test in a non-production environment first!