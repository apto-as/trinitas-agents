# Trinitas Monitoring and Recovery Guide

## 🛡️ Overview

The Trinitas Parallel Agents system includes comprehensive monitoring and automatic recovery capabilities to ensure reliable operation in production environments.

### Key Features

- **Real-time Session Monitoring**: Track active parallel executions
- **Automatic Issue Detection**: Identify problems before they impact users
- **Self-Healing Recovery**: Automatically fix common issues
- **Performance Tracking**: Monitor execution times and resource usage

## 📊 Session Monitor

The session monitor provides real-time visibility into parallel agent executions.

### Basic Usage

```bash
# Check current status
./hooks/monitoring/session_monitor.sh status

# Monitor specific session
./hooks/monitoring/session_monitor.sh health <session_id>

# Real-time monitoring mode
./hooks/monitoring/session_monitor.sh monitor

# Check performance metrics
./hooks/monitoring/session_monitor.sh performance

# Clean up stale sessions
./hooks/monitoring/session_monitor.sh cleanup
```

### Status Indicators

- ✅ **Active Session**: Currently executing (< 5 minutes old)
- ⚠️ **Stale Session**: No activity for > 5 minutes
- ❌ **Failed Session**: Contains errors or incomplete results

### Real-time Monitoring

The monitor mode refreshes every 10 seconds and shows:
- Number of active/stale sessions
- Performance metrics
- Automatic cleanup triggers

```bash
# Start real-time monitoring
./hooks/monitoring/session_monitor.sh monitor

# Example output:
# Monitoring at 2024-01-15 10:30:45
# ================================
# === Active Sessions ===
# ✅ Active session: abc123 (age: 45s)
# ✅ Active session: def456 (age: 120s)
# Active sessions: 2
# Stale sessions: 0
```

## 🔧 Auto-Recovery System

The auto-recovery system detects and fixes common issues automatically.

### Running Recovery

```bash
# Diagnose issues only
python3 hooks/monitoring/auto_recovery.py --diagnose-only

# Run recovery with manual confirmation
python3 hooks/monitoring/auto_recovery.py

# Automatic recovery (no confirmation)
python3 hooks/monitoring/auto_recovery.py --auto-fix
```

### Detectable Issues

1. **Incomplete Sessions**
   - Sessions that started but never completed
   - Automatically moved to failed directory for analysis

2. **Corrupted JSON Files**
   - Malformed or truncated JSON results
   - Attempts automatic repair or quarantine

3. **Missing Integrations**
   - Completed sessions without integration
   - Triggers integration process retroactively

4. **Hook Failures**
   - Missing or non-executable hooks
   - Restores from project directory

5. **Low Disk Space**
   - Insufficient space for new results
   - Cleans old results and rotates logs

### Recovery Strategies

#### Incomplete Session Recovery
```python
# Automatically triggered for sessions > 30 minutes old
# Moves to failed/ directory with recovery report
# Preserves data for manual analysis
```

#### JSON Repair
```python
# Attempts to fix:
# - Truncated JSON (finds last valid object)
# - Missing quotes in keys
# - Incomplete arrays/objects
```

#### Disk Space Management
```python
# Removes:
# - Results older than 7 days
# - Rotates logs > 100MB
# - Compresses old logs
```

## 📈 Performance Monitoring

### Metrics Tracked

- **Execution Time**: Average time per agent
- **Success Rate**: Percentage of successful completions
- **Resource Usage**: Disk space and memory
- **Error Frequency**: Rate of failures over time

### Performance Alerts

The system alerts when:
- Average execution time > 5 minutes
- Disk usage > 1GB
- Error rate > 20%
- Stale sessions > 5

### Viewing Metrics

```bash
# Quick performance check
./hooks/monitoring/session_monitor.sh performance

# Detailed metrics from logs
grep "execution_time_ms" ~/.claude/trinitas/parallel_results/completed/*/*.json | \
  jq -s 'map(.execution_time_ms) | add/length'
```

## 🚨 Alerting and Logging

### Log Locations

- **Session Monitor**: `~/.claude/trinitas/logs/session_monitor.log`
- **Recovery Operations**: `~/.claude/trinitas/logs/recovery.log`
- **General Errors**: `~/.claude/trinitas/logs/errors.log`
- **Health Reports**: `~/.claude/trinitas/logs/health_report_*.txt`

### Log Rotation

Logs are automatically rotated when:
- Size exceeds 100MB
- Age exceeds 30 days
- Disk space is low

### Monitoring Best Practices

1. **Regular Health Checks**
   ```bash
   # Add to cron for hourly checks
   0 * * * * /path/to/hooks/monitoring/health_check.sh
   ```

2. **Daily Cleanup**
   ```bash
   # Add to cron for daily cleanup
   0 2 * * * /path/to/hooks/monitoring/session_monitor.sh cleanup
   ```

3. **Weekly Recovery**
   ```bash
   # Add to cron for weekly auto-recovery
   0 3 * * 0 python3 /path/to/hooks/monitoring/auto_recovery.py --auto-fix
   ```

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### High Memory Usage
```bash
# Check for large result files
find ~/.claude/trinitas/parallel_results -name "*.json" -size +10M

# Clean old sessions
find ~/.claude/trinitas/parallel_results/temp -mtime +1 -delete
```

#### Stuck Sessions
```bash
# Identify stuck sessions
./hooks/monitoring/session_monitor.sh status | grep Stale

# Force cleanup
./hooks/monitoring/session_monitor.sh cleanup
```

#### Integration Failures
```bash
# Check for missing integrations
ls ~/.claude/trinitas/parallel_results/completed/*/
ls ~/.claude/trinitas/parallel_results/integrated/

# Manual integration
TRINITAS_SESSION_ID=<session_id> python3 hooks/python/integrate_parallel_results.py
```

## 🔐 Security Considerations

### Access Control
- Logs contain execution details but no sensitive data
- Results are stored with user-only permissions (600)
- Recovery operations require explicit confirmation

### Data Retention
- Active results: Immediate access
- Completed results: 7 days
- Failed results: 30 days
- Logs: 30 days (compressed)

### Audit Trail
All recovery operations are logged with:
- Timestamp
- Action taken
- Success/failure status
- User who initiated

## 📊 Dashboard Integration

For visual monitoring, results can be exported:

```python
# Export metrics to JSON
import json
from pathlib import Path

metrics = {
    'timestamp': datetime.now().isoformat(),
    'active_sessions': count_active_sessions(),
    'success_rate': calculate_success_rate(),
    'avg_execution_time': get_average_execution_time()
}

with open('metrics.json', 'w') as f:
    json.dump(metrics, f)
```

## 🌟 Best Practices Summary

1. **Enable Monitoring**
   - Run health checks regularly
   - Set up automated cleanup
   - Monitor performance trends

2. **Proactive Recovery**
   - Run auto-recovery weekly
   - Address issues promptly
   - Keep logs for analysis

3. **Resource Management**
   - Clean old results regularly
   - Monitor disk usage
   - Rotate logs automatically

4. **Incident Response**
   - Check monitoring logs first
   - Run diagnostic tools
   - Use auto-recovery when safe

---

*The Trinitas monitoring and recovery system ensures your parallel agents remain healthy and performant, providing the reliability needed for production deployments.*