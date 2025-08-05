#!/bin/bash
# Trinitas Session Monitor - Real-time Parallel Execution Tracking
# Vector: "……全てのセッションを監視し、異常を即座に検出……"

# Configuration
RESULTS_DIR="${TRINITAS_RESULTS_DIR:-$HOME/.claude/trinitas/parallel_results}"
LOG_DIR="$HOME/.claude/trinitas/logs"
MONITOR_LOG="$LOG_DIR/session_monitor.log"
ALERT_THRESHOLD=300000  # 5 minutes in milliseconds

# =====================================================
# Monitoring Functions
# =====================================================

log_monitor() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$MONITOR_LOG"
}

check_active_sessions() {
    echo "=== Active Sessions ==="
    
    local active_count=0
    local stale_count=0
    
    # Check temp directory for active sessions
    if [[ -d "$RESULTS_DIR/temp" ]]; then
        for result_file in "$RESULTS_DIR/temp"/*.json; do
            [[ ! -f "$result_file" ]] && continue
            
            local session_id=$(basename "$result_file" | cut -d'_' -f1)
            local file_age_seconds=$(( $(date +%s) - $(stat -f %m "$result_file" 2>/dev/null || stat -c %Y "$result_file" 2>/dev/null) ))
            
            if [[ $file_age_seconds -gt 300 ]]; then
                echo "⚠️  Stale session: $session_id (age: ${file_age_seconds}s)"
                ((stale_count++))
                log_monitor "WARNING" "Stale session detected: $session_id"
            else
                echo "✅ Active session: $session_id (age: ${file_age_seconds}s)"
                ((active_count++))
            fi
        done
    fi
    
    echo ""
    echo "Active sessions: $active_count"
    echo "Stale sessions: $stale_count"
    
    return $stale_count
}

check_session_health() {
    local session_id=$1
    echo "=== Session Health: $session_id ==="
    
    # Count results for this session
    local result_count=$(find "$RESULTS_DIR/temp" -name "${session_id}_*.json" 2>/dev/null | wc -l)
    
    # Check expected count
    local expected_count=0
    if [[ -f "$RESULTS_DIR/temp/${session_id}_metadata.json" ]]; then
        expected_count=$(jq -r '.expected_count // 0' "$RESULTS_DIR/temp/${session_id}_metadata.json" 2>/dev/null || echo 0)
    fi
    
    echo "Results collected: $result_count"
    if [[ $expected_count -gt 0 ]]; then
        echo "Expected results: $expected_count"
        
        if [[ $result_count -lt $expected_count ]]; then
            echo "⚠️  Incomplete session (missing $((expected_count - result_count)) results)"
            log_monitor "WARNING" "Incomplete session $session_id: $result_count/$expected_count"
        else
            echo "✅ Session complete"
        fi
    fi
    
    # Check for errors
    local error_count=0
    for result_file in "$RESULTS_DIR/temp/${session_id}_"*.json; do
        [[ ! -f "$result_file" ]] && continue
        
        local status=$(jq -r '.status // "unknown"' "$result_file" 2>/dev/null)
        if [[ "$status" != "success" ]]; then
            ((error_count++))
            echo "❌ Error in $(basename "$result_file"): $status"
        fi
    done
    
    if [[ $error_count -gt 0 ]]; then
        echo "⚠️  Session has $error_count errors"
        log_monitor "ERROR" "Session $session_id has $error_count errors"
    fi
}

cleanup_stale_sessions() {
    echo "=== Cleanup Stale Sessions ==="
    
    local cleaned=0
    
    # Clean stale temp files older than 2 hours
    for result_file in "$RESULTS_DIR/temp"/*.json; do
        [[ ! -f "$result_file" ]] && continue
        
        local file_age_minutes=$(( ($(date +%s) - $(stat -f %m "$result_file" 2>/dev/null || stat -c %Y "$result_file" 2>/dev/null)) / 60 ))
        
        if [[ $file_age_minutes -gt 120 ]]; then
            local session_id=$(basename "$result_file" | cut -d'_' -f1)
            echo "Cleaning stale session: $session_id (${file_age_minutes}m old)"
            
            # Move to failed directory for analysis
            mkdir -p "$RESULTS_DIR/failed/$session_id"
            mv "$RESULTS_DIR/temp/${session_id}_"* "$RESULTS_DIR/failed/$session_id/" 2>/dev/null
            ((cleaned++))
            
            log_monitor "INFO" "Cleaned stale session $session_id"
        fi
    done
    
    echo "Cleaned $cleaned stale sessions"
}

monitor_performance() {
    echo "=== Performance Metrics ==="
    
    # Calculate average execution times
    local total_time=0
    local count=0
    
    for result_file in "$RESULTS_DIR/completed"/*/*.json; do
        [[ ! -f "$result_file" ]] && continue
        
        local exec_time=$(jq -r '.execution_time_ms // 0' "$result_file" 2>/dev/null)
        if [[ $exec_time -gt 0 ]]; then
            total_time=$((total_time + exec_time))
            ((count++))
        fi
    done
    
    if [[ $count -gt 0 ]]; then
        local avg_time=$((total_time / count))
        echo "Average execution time: ${avg_time}ms"
        
        if [[ $avg_time -gt $ALERT_THRESHOLD ]]; then
            echo "⚠️  Performance degradation detected!"
            log_monitor "WARNING" "High average execution time: ${avg_time}ms"
        fi
    fi
    
    # Check disk usage
    local disk_usage=$(du -sm "$RESULTS_DIR" 2>/dev/null | cut -f1)
    echo "Results directory size: ${disk_usage}MB"
    
    if [[ $disk_usage -gt 1000 ]]; then
        echo "⚠️  High disk usage! Consider cleanup."
        log_monitor "WARNING" "High disk usage: ${disk_usage}MB"
    fi
}

# =====================================================
# Main Monitor Loop
# =====================================================

monitor_mode() {
    echo "🔍 Trinitas Session Monitor - Real-time Mode"
    echo "Press Ctrl+C to exit"
    echo ""
    
    while true; do
        clear
        echo "Monitoring at $(date)"
        echo "================================"
        
        check_active_sessions
        monitor_performance
        
        # Auto-cleanup if needed
        local stale_count=$?
        if [[ $stale_count -gt 5 ]]; then
            echo ""
            cleanup_stale_sessions
        fi
        
        sleep 10
    done
}

# =====================================================
# Command Line Interface
# =====================================================

case "${1:-status}" in
    status)
        check_active_sessions
        ;;
    health)
        if [[ -n "${2:-}" ]]; then
            check_session_health "$2"
        else
            echo "Usage: $0 health <session_id>"
            exit 1
        fi
        ;;
    cleanup)
        cleanup_stale_sessions
        ;;
    monitor)
        monitor_mode
        ;;
    performance)
        monitor_performance
        ;;
    *)
        echo "Usage: $0 [status|health|cleanup|monitor|performance]"
        echo ""
        echo "Commands:"
        echo "  status      - Show active and stale sessions"
        echo "  health ID   - Check health of specific session"
        echo "  cleanup     - Clean up stale sessions"
        echo "  monitor     - Real-time monitoring mode"
        echo "  performance - Show performance metrics"
        exit 1
        ;;
esac