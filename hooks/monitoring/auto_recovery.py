#!/usr/bin/env python3
"""
Trinitas Auto-Recovery System - Automatic Error Detection and Recovery
Vector: "……障害を予測し、自動的に回復する……システムの自己修復……"
"""

import json
import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import subprocess
import hashlib

class AutoRecoverySystem:
    """Automatic recovery from common parallel execution failures"""
    
    def __init__(self):
        self.trinitas_dir = Path.home() / '.claude' / 'trinitas'
        self.results_dir = Path(os.environ.get('TRINITAS_RESULTS_DIR', 
                                              self.trinitas_dir / 'parallel_results'))
        self.log_dir = self.trinitas_dir / 'logs'
        self.recovery_log = self.log_dir / 'recovery.log'
        
        # Setup logging
        self.setup_logging()
        
        # Recovery strategies
        self.recovery_strategies = {
            'incomplete_session': self._recover_incomplete_session,
            'corrupted_json': self._recover_corrupted_json,
            'missing_integration': self._recover_missing_integration,
            'hook_failure': self._recover_hook_failure,
            'disk_space': self._recover_disk_space
        }
    
    def setup_logging(self):
        """Configure logging for recovery operations"""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(self.recovery_log),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def diagnose_issues(self) -> List[Dict]:
        """Diagnose current system issues"""
        issues = []
        
        # Check for incomplete sessions
        incomplete = self._find_incomplete_sessions()
        if incomplete:
            issues.append({
                'type': 'incomplete_session',
                'severity': 'medium',
                'sessions': incomplete,
                'description': f'{len(incomplete)} incomplete sessions found'
            })
        
        # Check for corrupted JSON files
        corrupted = self._find_corrupted_json()
        if corrupted:
            issues.append({
                'type': 'corrupted_json',
                'severity': 'high',
                'files': corrupted,
                'description': f'{len(corrupted)} corrupted JSON files found'
            })
        
        # Check for missing integrations
        missing = self._find_missing_integrations()
        if missing:
            issues.append({
                'type': 'missing_integration',
                'severity': 'low',
                'sessions': missing,
                'description': f'{len(missing)} sessions missing integration'
            })
        
        # Check disk space
        disk_issue = self._check_disk_space()
        if disk_issue:
            issues.append(disk_issue)
        
        # Check hook health
        hook_issues = self._check_hook_health()
        if hook_issues:
            issues.extend(hook_issues)
        
        return issues
    
    def _find_incomplete_sessions(self) -> List[str]:
        """Find sessions that started but didn't complete"""
        incomplete = []
        temp_dir = self.results_dir / 'temp'
        
        if not temp_dir.exists():
            return incomplete
        
        # Group files by session
        sessions = {}
        for file in temp_dir.glob('*.json'):
            if file.name == 'metadata.json':
                continue
                
            session_id = file.name.split('_')[0]
            if session_id not in sessions:
                sessions[session_id] = []
            sessions[session_id].append(file)
        
        # Check each session
        for session_id, files in sessions.items():
            # Check if session is stale (older than 30 minutes)
            oldest_file = min(files, key=lambda f: f.stat().st_mtime)
            age = time.time() - oldest_file.stat().st_mtime
            
            if age > 1800:  # 30 minutes
                incomplete.append(session_id)
        
        return incomplete
    
    def _find_corrupted_json(self) -> List[Path]:
        """Find corrupted JSON files"""
        corrupted = []
        
        for results_subdir in ['temp', 'completed', 'integrated']:
            subdir = self.results_dir / results_subdir
            if not subdir.exists():
                continue
                
            for json_file in subdir.rglob('*.json'):
                try:
                    with open(json_file, 'r') as f:
                        json.load(f)
                except (json.JSONDecodeError, IOError):
                    corrupted.append(json_file)
        
        return corrupted
    
    def _find_missing_integrations(self) -> List[str]:
        """Find completed sessions without integration"""
        missing = []
        completed_dir = self.results_dir / 'completed'
        integrated_dir = self.results_dir / 'integrated'
        
        if not completed_dir.exists():
            return missing
        
        for session_dir in completed_dir.iterdir():
            if not session_dir.is_dir():
                continue
                
            session_id = session_dir.name
            
            # Check if integration exists
            integration_files = list(integrated_dir.glob(f'{session_id}_*'))
            if not integration_files:
                missing.append(session_id)
        
        return missing
    
    def _check_disk_space(self) -> Optional[Dict]:
        """Check available disk space"""
        try:
            stat = os.statvfs(self.results_dir)
            free_mb = (stat.f_bavail * stat.f_frsize) / 1024 / 1024
            
            if free_mb < 100:
                return {
                    'type': 'disk_space',
                    'severity': 'critical',
                    'free_mb': free_mb,
                    'description': f'Low disk space: {free_mb:.1f}MB free'
                }
        except OSError:
            pass
        
        return None
    
    def _check_hook_health(self) -> List[Dict]:
        """Check health of hook scripts"""
        issues = []
        hooks_dir = self.trinitas_dir / 'hooks'
        
        critical_hooks = [
            'core/trinitas_protocol_injector.sh',
            'post-execution/capture_subagent_result.sh',
            'python/prepare_parallel_tasks.py',
            'python/integrate_parallel_results.py'
        ]
        
        for hook_path in critical_hooks:
            full_path = hooks_dir / hook_path
            
            if not full_path.exists():
                issues.append({
                    'type': 'hook_failure',
                    'severity': 'critical',
                    'hook': hook_path,
                    'description': f'Missing critical hook: {hook_path}'
                })
            elif not os.access(full_path, os.X_OK):
                issues.append({
                    'type': 'hook_failure',
                    'severity': 'high',
                    'hook': hook_path,
                    'description': f'Hook not executable: {hook_path}'
                })
        
        return issues
    
    # =====================================================
    # Recovery Strategies
    # =====================================================
    
    def _recover_incomplete_session(self, issue: Dict) -> bool:
        """Recover incomplete sessions"""
        self.logger.info(f"Recovering {len(issue['sessions'])} incomplete sessions")
        
        recovered = 0
        for session_id in issue['sessions']:
            try:
                # Move to failed directory for analysis
                failed_dir = self.results_dir / 'failed' / session_id
                failed_dir.mkdir(parents=True, exist_ok=True)
                
                # Move all session files
                temp_dir = self.results_dir / 'temp'
                for file in temp_dir.glob(f'{session_id}_*.json'):
                    file.rename(failed_dir / file.name)
                
                # Create recovery report
                report = {
                    'session_id': session_id,
                    'recovery_time': datetime.now().isoformat(),
                    'reason': 'incomplete_session',
                    'files_recovered': len(list(failed_dir.glob('*.json')))
                }
                
                report_file = failed_dir / 'recovery_report.json'
                with open(report_file, 'w') as f:
                    json.dump(report, f, indent=2)
                
                recovered += 1
                self.logger.info(f"Recovered incomplete session: {session_id}")
                
            except Exception as e:
                self.logger.error(f"Failed to recover session {session_id}: {e}")
        
        return recovered == len(issue['sessions'])
    
    def _recover_corrupted_json(self, issue: Dict) -> bool:
        """Attempt to recover corrupted JSON files"""
        self.logger.info(f"Attempting to recover {len(issue['files'])} corrupted files")
        
        recovered = 0
        for file_path in issue['files']:
            try:
                # Try to read and fix common JSON issues
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Backup corrupted file
                backup_path = file_path.with_suffix('.corrupted')
                file_path.rename(backup_path)
                
                # Attempt repairs
                fixed_content = self._attempt_json_repair(content)
                
                if fixed_content:
                    # Validate repaired JSON
                    json.loads(fixed_content)
                    
                    # Write repaired content
                    with open(file_path, 'w') as f:
                        f.write(fixed_content)
                    
                    recovered += 1
                    self.logger.info(f"Recovered corrupted file: {file_path}")
                else:
                    self.logger.warning(f"Could not repair: {file_path}")
                    
            except Exception as e:
                self.logger.error(f"Failed to recover {file_path}: {e}")
        
        return recovered > 0
    
    def _attempt_json_repair(self, content: str) -> Optional[str]:
        """Attempt to repair common JSON issues"""
        if not content.strip():
            return None
        
        # Try to fix truncated JSON
        if content.rstrip()[-1] not in ['}', ']']:
            # Find last complete object/array
            for i in range(len(content) - 1, -1, -1):
                if content[i] in ['}', ']']:
                    try:
                        json.loads(content[:i+1])
                        return content[:i+1]
                    except:
                        continue
        
        # Try to fix missing quotes
        try:
            # Simple attempt - this is a basic implementation
            import re
            fixed = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', content)
            json.loads(fixed)
            return fixed
        except:
            pass
        
        return None
    
    def _recover_missing_integration(self, issue: Dict) -> bool:
        """Trigger integration for sessions missing it"""
        self.logger.info(f"Integrating {len(issue['sessions'])} sessions")
        
        integrated = 0
        for session_id in issue['sessions']:
            try:
                # Set up environment
                env = os.environ.copy()
                env['TRINITAS_SESSION_ID'] = session_id
                env['TRINITAS_INTEGRATION_SESSION'] = session_id
                
                # Run integration script
                integration_script = self.trinitas_dir / 'hooks' / 'python' / 'integrate_parallel_results.py'
                
                result = subprocess.run(
                    ['python3', str(integration_script)],
                    env=env,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    integrated += 1
                    self.logger.info(f"Successfully integrated session: {session_id}")
                else:
                    self.logger.error(f"Integration failed for {session_id}: {result.stderr}")
                    
            except Exception as e:
                self.logger.error(f"Failed to integrate {session_id}: {e}")
        
        return integrated == len(issue['sessions'])
    
    def _recover_hook_failure(self, issue: Dict) -> bool:
        """Attempt to recover failed hooks"""
        hook_path = issue['hook']
        self.logger.info(f"Attempting to recover hook: {hook_path}")
        
        # Try to restore from project directory
        project_hook = Path(__file__).parent.parent.parent / 'hooks' / hook_path
        target_hook = self.trinitas_dir / 'hooks' / hook_path
        
        try:
            if project_hook.exists():
                target_hook.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy hook
                with open(project_hook, 'r') as src:
                    content = src.read()
                with open(target_hook, 'w') as dst:
                    dst.write(content)
                
                # Make executable
                os.chmod(target_hook, 0o755)
                
                self.logger.info(f"Recovered hook: {hook_path}")
                return True
            else:
                self.logger.error(f"Source hook not found: {project_hook}")
                
        except Exception as e:
            self.logger.error(f"Failed to recover hook {hook_path}: {e}")
        
        return False
    
    def _recover_disk_space(self, issue: Dict) -> bool:
        """Free up disk space"""
        self.logger.info("Attempting to free disk space")
        
        freed_mb = 0
        
        try:
            # Clean old results (older than 7 days)
            cutoff_time = time.time() - (7 * 24 * 60 * 60)
            
            for subdir in ['completed', 'integrated', 'failed']:
                dir_path = self.results_dir / subdir
                if not dir_path.exists():
                    continue
                
                for item in dir_path.iterdir():
                    if item.stat().st_mtime < cutoff_time:
                        size_mb = self._get_dir_size_mb(item)
                        
                        if item.is_dir():
                            import shutil
                            shutil.rmtree(item)
                        else:
                            item.unlink()
                        
                        freed_mb += size_mb
                        self.logger.info(f"Removed old item: {item.name} ({size_mb:.1f}MB)")
            
            # Clean large log files
            for log_file in self.log_dir.glob('*.log'):
                if log_file.stat().st_size > 100 * 1024 * 1024:  # 100MB
                    # Rotate log
                    rotated = log_file.with_suffix('.log.old')
                    log_file.rename(rotated)
                    
                    # Compress old log
                    subprocess.run(['gzip', str(rotated)], capture_output=True)
                    
                    freed_mb += 100
                    self.logger.info(f"Rotated large log: {log_file.name}")
            
            self.logger.info(f"Freed {freed_mb:.1f}MB of disk space")
            return freed_mb > 50  # Success if freed more than 50MB
            
        except Exception as e:
            self.logger.error(f"Failed to free disk space: {e}")
            return False
    
    def _get_dir_size_mb(self, path: Path) -> float:
        """Get directory size in MB"""
        total = 0
        
        if path.is_file():
            return path.stat().st_size / 1024 / 1024
        
        for item in path.rglob('*'):
            if item.is_file():
                total += item.stat().st_size
        
        return total / 1024 / 1024
    
    # =====================================================
    # Main Recovery Process
    # =====================================================
    
    def run_recovery(self, auto_fix: bool = False) -> Dict:
        """Run full recovery process"""
        self.logger.info("Starting Trinitas Auto-Recovery")
        
        # Diagnose issues
        issues = self.diagnose_issues()
        
        if not issues:
            self.logger.info("No issues found - system healthy")
            return {'status': 'healthy', 'issues': 0, 'fixed': 0}
        
        self.logger.warning(f"Found {len(issues)} issues")
        
        # Report issues
        for issue in issues:
            self.logger.warning(f"{issue['severity'].upper()}: {issue['description']}")
        
        fixed = 0
        
        if auto_fix:
            # Attempt recovery for each issue
            for issue in issues:
                issue_type = issue['type']
                
                if issue_type in self.recovery_strategies:
                    self.logger.info(f"Attempting recovery for: {issue_type}")
                    
                    if self.recovery_strategies[issue_type](issue):
                        fixed += 1
                        self.logger.info(f"Successfully recovered: {issue_type}")
                    else:
                        self.logger.error(f"Failed to recover: {issue_type}")
        
        # Final report
        report = {
            'status': 'recovered' if fixed > 0 else 'issues_found',
            'issues': len(issues),
            'fixed': fixed,
            'timestamp': datetime.now().isoformat(),
            'details': issues
        }
        
        # Save report
        report_file = self.log_dir / f'recovery_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Trinitas Auto-Recovery System')
    parser.add_argument(
        '--auto-fix',
        action='store_true',
        help='Automatically attempt to fix issues'
    )
    parser.add_argument(
        '--diagnose-only',
        action='store_true',
        help='Only diagnose issues without fixing'
    )
    
    args = parser.parse_args()
    
    recovery = AutoRecoverySystem()
    
    if args.diagnose_only:
        issues = recovery.diagnose_issues()
        print(f"\nFound {len(issues)} issues:")
        for issue in issues:
            print(f"  [{issue['severity']}] {issue['description']}")
    else:
        report = recovery.run_recovery(auto_fix=args.auto_fix)
        print(f"\nRecovery Report:")
        print(f"  Status: {report['status']}")
        print(f"  Issues found: {report['issues']}")
        print(f"  Issues fixed: {report['fixed']}")

if __name__ == '__main__':
    main()