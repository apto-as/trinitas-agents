#!/bin/bash

# Trinitas Backup Manager - 404's Perfect Recovery System
# Provides complete backup and recovery functionality for settings.json

set -euo pipefail

# Source common logging functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRINITAS_ROOT="$(dirname "$SCRIPT_DIR")"

# Source logging functions if available
if [[ -f "$SCRIPT_DIR/../hooks/core/common_lib.sh" ]]; then
    source "$SCRIPT_DIR/../hooks/core/common_lib.sh"
else
    # Fallback logging functions
    log_info() { echo "[INFO] $*" >&2; }
    log_error() { echo "[ERROR] $*" >&2; }
    log_success() { echo "[SUCCESS] $*" >&2; }
    log_warning() { echo "[WARNING] $*" >&2; }
fi

# Global variables
DEFAULT_BACKUP_KEEP=10

show_usage() {
    cat << 'EOF'
Trinitas Backup Manager - 404's Perfect Recovery System

USAGE:
    backup_manager.sh <command> [options]

COMMANDS:
    backup <scope>      - Create backup of settings.json
                         scope: user|project
    
    restore <scope>     - Interactive restore from backup
                         scope: user|project
    
    list <scope>        - List available backups
                         scope: user|project
    
    cleanup <scope>     - Clean up old backups (keep last 10)
                         scope: user|project [keep_count]
    
    verify <scope>      - Verify backup integrity
                         scope: user|project

EXAMPLES:
    backup_manager.sh backup user
    backup_manager.sh restore project
    backup_manager.sh list user
    backup_manager.sh cleanup project 5
    backup_manager.sh verify user

NOTES:
    - User scope: ~/.claude/settings.json
    - Project scope: .claude/settings.json
    - Backups stored in .trinitas_backups/ directory
    - Recovery metadata automatically maintained
EOF
}

# Get paths based on scope
get_paths() {
    local scope="$1"
    local settings_file backup_dir
    
    case "$scope" in
        "user")
            settings_file="$HOME/.claude/settings.json"
            backup_dir="$HOME/.claude/.trinitas_backups"
            ;;
        "project")
            settings_file=".claude/settings.json"
            backup_dir=".claude/.trinitas_backups"
            ;;
        *)
            log_error "Invalid scope '$scope'. Must be 'user' or 'project'"
            return 1
            ;;
    esac
    
    echo "$settings_file|$backup_dir"
}

# Create backup with metadata
create_backup() {
    local scope="$1"
    local reason="${2:-manual}"
    
    local paths settings_file backup_dir
    paths=$(get_paths "$scope")
    settings_file="${paths%|*}"
    backup_dir="${paths#*|}"
    
    if [[ ! -f "$settings_file" ]]; then
        log_error "Settings file not found: $settings_file"
        return 1
    fi
    
    # Verify settings file is valid JSON
    if ! jq empty "$settings_file" >/dev/null 2>&1; then
        log_error "Settings file is not valid JSON: $settings_file"
        return 1
    fi
    
    mkdir -p "$backup_dir"
    
    local timestamp backup_file
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_file="$backup_dir/settings_${timestamp}.json"
    
    # Create backup
    cp "$settings_file" "$backup_file"
    log_info "Created backup: $backup_file"
    
    # Create/update recovery metadata
    cat > "$backup_dir/recovery_info.json" << EOF
{
  "last_backup": "$backup_file",
  "backup_timestamp": "$(date -Iseconds)",
  "scope": "$scope",
  "reason": "$reason",
  "original_file": "$settings_file"
}
EOF
    
    log_success "Backup completed successfully"
    return 0
}

# List available backups
list_backups() {
    local scope="$1"
    
    local paths settings_file backup_dir
    paths=$(get_paths "$scope")
    settings_file="${paths%|*}"
    backup_dir="${paths#*|}"
    
    if [[ ! -d "$backup_dir" ]]; then
        log_warning "No backup directory found for scope '$scope'"
        log_info "Expected location: $backup_dir"
        return 1
    fi
    
    local backups
    backups=$(find "$backup_dir" -name "settings_*.json" -type f | sort -r)
    
    if [[ -z "$backups" ]]; then
        log_warning "No backups found for scope '$scope'"
        return 1
    fi
    
    echo "Available backups for scope '$scope':"
    echo "Settings file: $settings_file"
    echo "Backup directory: $backup_dir"
    echo
    
    local count=0
    while IFS= read -r backup; do
        count=$((count + 1))
        local timestamp size
        timestamp=$(basename "$backup" .json | sed 's/settings_//')
        size=$(du -h "$backup" 2>/dev/null | cut -f1 || echo "unknown")
        
        # Format timestamp for display
        local display_time
        if command -v date >/dev/null 2>&1; then
            display_time=$(date -d "${timestamp//_/ }" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo "$timestamp")
        else
            display_time="$timestamp"
        fi
        
        # Verify backup integrity
        local status
        if jq empty "$backup" >/dev/null 2>&1; then
            status="✓ Valid"
        else
            status="✗ Corrupted"
        fi
        
        printf "%2d. %s [%s] (%s) - %s\n" "$count" "$display_time" "$size" "$status" "$backup"
    done <<< "$backups"
    
    # Show recovery info if available
    if [[ -f "$backup_dir/recovery_info.json" ]]; then
        echo
        echo "Recovery metadata:"
        jq -r '"Last backup: \(.last_backup // "unknown")
Timestamp: \(.backup_timestamp // "unknown")
Reason: \(.reason // "unknown")"' "$backup_dir/recovery_info.json" 2>/dev/null || echo "  Metadata corrupted"
    fi
}

# Interactive restore function
interactive_restore() {
    local scope="$1"
    
    local paths settings_file backup_dir
    paths=$(get_paths "$scope")
    settings_file="${paths%|*}"
    backup_dir="${paths#*|}"
    
    if [[ ! -d "$backup_dir" ]]; then
        log_error "No backup directory found for scope '$scope'"
        return 1
    fi
    
    local backups
    backups=$(find "$backup_dir" -name "settings_*.json" -type f | sort -r)
    
    if [[ -z "$backups" ]]; then
        log_error "No backups found for scope '$scope'"
        return 1
    fi
    
    echo "Available backups:"
    local -a backup_array=()
    local count=0
    
    while IFS= read -r backup; do
        count=$((count + 1))
        backup_array+=("$backup")
        
        local timestamp size status
        timestamp=$(basename "$backup" .json | sed 's/settings_//')
        size=$(du -h "$backup" 2>/dev/null | cut -f1 || echo "unknown")
        
        if jq empty "$backup" >/dev/null 2>&1; then
            status="✓"
        else
            status="✗"
        fi
        
        local display_time
        display_time=$(date -d "${timestamp//_/ }" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo "$timestamp")
        
        printf "%2d. %s [%s] %s - %s\n" "$count" "$display_time" "$size" "$status" "$backup"
    done <<< "$backups"
    
    echo
    read -p "Select backup to restore (1-$count, or 'q' to quit): " choice
    
    if [[ "$choice" == "q" || "$choice" == "Q" ]]; then
        log_info "Restore cancelled"
        return 0
    fi
    
    if [[ ! "$choice" =~ ^[0-9]+$ ]] || [[ $choice -lt 1 || $choice -gt $count ]]; then
        log_error "Invalid selection: $choice"
        return 1
    fi
    
    local selected_backup="${backup_array[$((choice - 1))]}"
    
    # Verify backup integrity
    if ! jq empty "$selected_backup" >/dev/null 2>&1; then
        log_error "Selected backup is corrupted: $selected_backup"
        return 1
    fi
    
    echo
    log_info "Selected backup: $selected_backup"
    log_info "Will restore to: $settings_file"
    echo
    
    # Show diff if current settings exist
    if [[ -f "$settings_file" ]]; then
        echo "Preview of changes:"
        if command -v diff >/dev/null 2>&1; then
            diff -u "$settings_file" "$selected_backup" 2>/dev/null || true
        else
            log_info "diff command not available - showing backup content:"
            echo "--- Backup content ---"
            head -20 "$selected_backup"
        fi
        echo
    fi
    
    read -p "Proceed with restore? (y/N): " confirm
    
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        # Create backup of current settings before restore
        if [[ -f "$settings_file" ]]; then
            local pre_restore_backup="${settings_file}.pre_restore.$(date +%Y%m%d_%H%M%S)"
            cp "$settings_file" "$pre_restore_backup"
            log_info "Current settings backed up to: $pre_restore_backup"
        fi
        
        # Perform restore
        cp "$selected_backup" "$settings_file"
        
        # Verify restored file
        if jq empty "$settings_file" >/dev/null 2>&1; then
            log_success "Settings restored successfully from: $selected_backup"
            return 0
        else
            log_error "Restored file is corrupted! Attempting emergency recovery..."
            if [[ -f "$pre_restore_backup" ]]; then
                cp "$pre_restore_backup" "$settings_file"
                log_info "Emergency recovery completed"
            fi
            return 1
        fi
    else
        log_info "Restore cancelled"
        return 0
    fi
}

# Cleanup old backups
cleanup_backups() {
    local scope="$1"
    local keep_count="${2:-$DEFAULT_BACKUP_KEEP}"
    
    local paths settings_file backup_dir
    paths=$(get_paths "$scope")
    backup_dir="${paths#*|}"
    
    if [[ ! -d "$backup_dir" ]]; then
        log_warning "No backup directory found for scope '$scope'"
        return 1
    fi
    
    local backup_count
    backup_count=$(find "$backup_dir" -name "settings_*.json" -type f | wc -l)
    
    if [[ $backup_count -le $keep_count ]]; then
        log_info "Only $backup_count backups found (keeping $keep_count) - no cleanup needed"
        return 0
    fi
    
    log_info "Cleaning up old backups (keeping last $keep_count out of $backup_count)..."
    
    local removed_count=0
    find "$backup_dir" -name "settings_*.json" -type f | \
        sort -r | tail -n +$((keep_count + 1)) | while read -r old_backup; do
        rm -f "$old_backup"
        log_info "Removed: $old_backup"
        removed_count=$((removed_count + 1))
    done
    
    log_success "Cleanup completed - kept $keep_count most recent backups"
}

# Verify backup integrity
verify_backups() {
    local scope="$1"
    
    local paths backup_dir
    paths=$(get_paths "$scope")
    backup_dir="${paths#*|}"
    
    if [[ ! -d "$backup_dir" ]]; then
        log_warning "No backup directory found for scope '$scope'"
        return 1
    fi
    
    local backups
    backups=$(find "$backup_dir" -name "settings_*.json" -type f | sort -r)
    
    if [[ -z "$backups" ]]; then
        log_warning "No backups found for scope '$scope'"
        return 1
    fi
    
    echo "Verifying backup integrity for scope '$scope':"
    
    local total_count=0 valid_count=0 corrupted_count=0
    
    while IFS= read -r backup; do
        total_count=$((total_count + 1))
        local timestamp
        timestamp=$(basename "$backup" .json | sed 's/settings_//')
        
        if jq empty "$backup" >/dev/null 2>&1; then
            echo "✓ Valid: $backup"
            valid_count=$((valid_count + 1))
        else
            echo "✗ Corrupted: $backup"
            corrupted_count=$((corrupted_count + 1))
        fi
    done <<< "$backups"
    
    echo
    echo "Verification Summary:"
    echo "  Total backups: $total_count"
    echo "  Valid backups: $valid_count"
    echo "  Corrupted backups: $corrupted_count"
    
    if [[ $corrupted_count -gt 0 ]]; then
        echo
        log_warning "$corrupted_count corrupted backups found!"
        read -p "Remove corrupted backups? (y/N): " remove_corrupted
        
        if [[ "$remove_corrupted" =~ ^[Yy]$ ]]; then
            while IFS= read -r backup; do
                if ! jq empty "$backup" >/dev/null 2>&1; then
                    rm -f "$backup"
                    log_info "Removed corrupted backup: $backup"
                fi
            done <<< "$backups"
            log_success "Corrupted backups cleaned up"
        fi
    else
        log_success "All backups are valid"
    fi
    
    return 0
}

# Main function
main() {
    if [[ $# -lt 2 ]]; then
        show_usage
        return 1
    fi
    
    local command="$1"
    local scope="$2"
    
    # Validate scope
    if [[ "$scope" != "user" && "$scope" != "project" ]]; then
        log_error "Invalid scope '$scope'. Must be 'user' or 'project'"
        return 1
    fi
    
    case "$command" in
        "backup")
            create_backup "$scope" "${3:-manual}"
            ;;
        "restore")
            interactive_restore "$scope"
            ;;
        "list")
            list_backups "$scope"
            ;;
        "cleanup")
            cleanup_backups "$scope" "${3:-$DEFAULT_BACKUP_KEEP}"
            ;;
        "verify")
            verify_backups "$scope"
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            return 1
            ;;
    esac
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi