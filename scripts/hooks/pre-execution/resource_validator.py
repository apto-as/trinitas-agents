#!/usr/bin/env python3
"""
Project Trinitas v2.0 - System Resource Validation Hook
Pre-execution resource availability and capacity validation

Integrated by: Trinitas Meta-Intelligence System
- Springfield: User-friendly resource reporting and guidance
- Krukai: Efficient resource monitoring and performance optimization
- Vector: Proactive resource exhaustion prevention and system protection
"""

import sys
import json
import os
import shutil
import psutil
import time
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class TrinitasResourceValidator:
    """Trinitas-powered system resource validation system"""
    
    def __init__(self):
        # Vector: Conservative resource thresholds for safety
        self.resource_thresholds = {
            'memory_critical': 95.0,    # % - Block execution
            'memory_warning': 85.0,     # % - Warn user
            'disk_critical': 98.0,      # % - Block execution
            'disk_warning': 90.0,       # % - Warn user
            'cpu_warning': 90.0,        # % - Warn user (5s average)
            'load_critical': 10.0,      # Load average - Block execution
            'swap_warning': 50.0,       # % - Warn about memory pressure
        }
        
        # Krukai: Performance monitoring configuration
        self.monitoring_duration = 2.0  # seconds for CPU averaging
        self.io_wait_threshold = 30.0   # % - High I/O wait indication
        
        # Springfield: User-friendly operation classifications
        self.operation_requirements = {
            'file_operations': {'disk': 10, 'memory': 5},     # MB requirements
            'compilation': {'cpu': 50, 'memory': 100},        # % CPU, MB memory
            'database': {'disk': 50, 'memory': 200},          # MB requirements
            'network': {'memory': 20, 'bandwidth': 1},        # MB memory, Mbps
            'analysis': {'cpu': 30, 'memory': 150},           # % CPU, MB memory
        }

    def get_system_resources(self) -> Dict:
        """
        Comprehensive system resource analysis
        Krukai: Efficient and accurate resource measurement
        """
        try:
            # Memory information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk information (for current working directory)
            disk = shutil.disk_usage('.')
            disk_total_gb = disk.total / (1024**3)
            disk_free_gb = disk.free / (1024**3)
            disk_used_percent = ((disk.total - disk.free) / disk.total) * 100
            
            # CPU information with brief monitoring
            cpu_percent_initial = psutil.cpu_percent(interval=None)
            time.sleep(self.monitoring_duration)
            cpu_percent = psutil.cpu_percent(interval=None)
            cpu_count = psutil.cpu_count()
            
            # Load average (Unix-like systems)
            try:
                load_avg = os.getloadavg()
            except (OSError, AttributeError):
                load_avg = (0, 0, 0)  # Windows fallback
            
            # I/O statistics
            try:
                io_counters = psutil.disk_io_counters()
                io_wait = getattr(psutil.cpu_times(), 'iowait', 0)
            except:
                io_counters = None
                io_wait = 0
            
            return {
                'memory': {
                    'total_gb': memory.total / (1024**3),
                    'available_gb': memory.available / (1024**3),
                    'used_percent': memory.percent,
                    'free_gb': memory.free / (1024**3)
                },
                'swap': {
                    'total_gb': swap.total / (1024**3),
                    'used_percent': swap.percent,
                    'free_gb': swap.free / (1024**3)
                },
                'disk': {
                    'total_gb': disk_total_gb,
                    'free_gb': disk_free_gb,
                    'used_percent': disk_used_percent,
                    'available_gb': disk_free_gb
                },
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': cpu_count,
                    'load_avg_1m': load_avg[0],
                    'load_avg_5m': load_avg[1],
                    'load_avg_15m': load_avg[2],
                },
                'io': {
                    'wait_percent': io_wait,
                    'counters': io_counters
                },
                'timestamp': time.time()
            }
            
        except Exception as e:
            # Vector: Always handle errors gracefully
            return {
                'error': f"Resource monitoring failed: {str(e)}",
                'timestamp': time.time()
            }

    def classify_operation(self, command: str, context: Dict) -> str:
        """
        Springfield: Intelligently classify the operation type
        """
        command_lower = command.lower()
        tool_name = context.get('tool', '').lower()
        
        # Classification based on command patterns
        if any(pattern in command_lower for pattern in ['gcc', 'clang', 'make', 'cmake', 'cargo', 'npm run build', 'mvn', 'gradle']):
            return 'compilation'
        
        if any(pattern in command_lower for pattern in ['mysql', 'postgres', 'mongo', 'redis', 'sqlite']):
            return 'database'
        
        if any(pattern in command_lower for pattern in ['curl', 'wget', 'ssh', 'scp', 'rsync']):
            return 'network'
        
        if any(pattern in command_lower for pattern in ['grep', 'find', 'awk', 'sed', 'sort', 'analyze']):
            return 'analysis'
        
        if tool_name in ['write', 'edit', 'multiedit'] or any(pattern in command_lower for pattern in ['cp', 'mv', 'mkdir', 'touch']):
            return 'file_operations'
        
        return 'general'

    def validate_resources(self, command: str, context: Dict) -> Tuple[str, str, List[str]]:
        """
        Comprehensive resource validation with Trinity intelligence
        
        Returns:
            (risk_level, decision, warnings)
        """
        
        resources = self.get_system_resources()
        
        if 'error' in resources:
            return 'HIGH', 'WARN', [f"Resource monitoring error: {resources['error']}"]
        
        warnings = []
        risk_level = 'SAFE'
        decision = 'ALLOW'
        
        # Vector: Critical resource checks (system protection)
        if resources['memory']['used_percent'] >= self.resource_thresholds['memory_critical']:
            warnings.append(f"CRITICAL: Memory usage at {resources['memory']['used_percent']:.1f}% - System may become unstable")
            risk_level = 'CRITICAL'
            decision = 'BLOCK'
        
        if resources['disk']['used_percent'] >= self.resource_thresholds['disk_critical']:
            warnings.append(f"CRITICAL: Disk usage at {resources['disk']['used_percent']:.1f}% - Risk of disk full")
            risk_level = 'CRITICAL'
            decision = 'BLOCK'
        
        if resources['cpu']['load_avg_1m'] >= self.resource_thresholds['load_critical']:
            warnings.append(f"CRITICAL: System load at {resources['cpu']['load_avg_1m']:.1f} - System overloaded")
            risk_level = 'CRITICAL'
            decision = 'BLOCK'
        
        # Krukai: Performance optimization warnings
        if resources['memory']['used_percent'] >= self.resource_thresholds['memory_warning']:
            warnings.append(f"WARNING: High memory usage ({resources['memory']['used_percent']:.1f}%) - Performance may be affected")
            if risk_level == 'SAFE':
                risk_level = 'MEDIUM'
                decision = 'WARN'
        
        if resources['disk']['used_percent'] >= self.resource_thresholds['disk_warning']:
            warnings.append(f"WARNING: Low disk space ({resources['disk']['free_gb']:.1f}GB free) - Consider cleanup")
            if risk_level == 'SAFE':
                risk_level = 'MEDIUM'
                decision = 'WARN'
        
        if resources['cpu']['usage_percent'] >= self.resource_thresholds['cpu_warning']:
            warnings.append(f"WARNING: High CPU usage ({resources['cpu']['usage_percent']:.1f}%) - System may be slow")
            if risk_level == 'SAFE':
                risk_level = 'LOW'
                decision = 'WARN'
        
        if resources['swap']['used_percent'] >= self.resource_thresholds['swap_warning']:
            warnings.append(f"INFO: Swap memory in use ({resources['swap']['used_percent']:.1f}%) - Consider adding RAM")
            if risk_level == 'SAFE':
                risk_level = 'LOW'
                decision = 'WARN'
        
        # Springfield: Operation-specific guidance
        operation_type = self.classify_operation(command, context)
        if operation_type in self.operation_requirements:
            req = self.operation_requirements[operation_type]
            
            if 'memory' in req and resources['memory']['available_gb'] * 1024 < req['memory']:
                warnings.append(f"INFO: {operation_type} typically requires {req['memory']}MB RAM, {resources['memory']['available_gb']*1024:.0f}MB available")
            
            if 'disk' in req and resources['disk']['free_gb'] * 1024 < req['disk']:
                warnings.append(f"INFO: {operation_type} may need {req['disk']}MB disk space, {resources['disk']['free_gb']*1024:.0f}MB available")
        
        return risk_level, decision, warnings

    def generate_resource_report(self, resources: Dict) -> str:
        """Springfield: Generate user-friendly resource report"""
        
        if 'error' in resources:
            return f"Resource monitoring unavailable: {resources['error']}"
        
        report = f"""
📊 TRINITAS SYSTEM RESOURCE REPORT

💾 Memory Status:
  • Total: {resources['memory']['total_gb']:.1f}GB
  • Available: {resources['memory']['available_gb']:.1f}GB ({100-resources['memory']['used_percent']:.1f}% free)
  • Used: {resources['memory']['used_percent']:.1f}%

💽 Disk Status:
  • Total: {resources['disk']['total_gb']:.1f}GB
  • Free: {resources['disk']['free_gb']:.1f}GB
  • Used: {resources['disk']['used_percent']:.1f}%

🔧 CPU Status:
  • Current Usage: {resources['cpu']['usage_percent']:.1f}%
  • CPU Cores: {resources['cpu']['count']}
  • Load Average: {resources['cpu']['load_avg_1m']:.2f} (1m), {resources['cpu']['load_avg_5m']:.2f} (5m)

Springfield's Assessment: {"System resources are healthy" if resources['memory']['used_percent'] < 80 and resources['disk']['used_percent'] < 80 else "Some resource constraints detected"}
Krukai's Analysis: {"Performance optimal" if resources['cpu']['usage_percent'] < 50 else "Performance monitoring recommended"}
Vector's Warning: {"No immediate concerns" if resources['memory']['used_percent'] < 90 and resources['disk']['used_percent'] < 90 else "Resource monitoring required"}
"""
        return report

def main():
    """Main execution function for Claude Code hook integration"""
    
    try:
        # Parse input
        if len(sys.argv) < 2:
            print(json.dumps({"allowed": True, "message": "No command provided for resource validation"}))
            sys.exit(0)
        
        command = sys.argv[1] if len(sys.argv) > 1 else ""
        context = {}
        
        if len(sys.argv) > 2:
            try:
                context = json.loads(sys.argv[2])
            except json.JSONDecodeError:
                context = {"tool": sys.argv[2] if len(sys.argv) > 2 else "unknown"}
        
        # Initialize validator
        validator = TrinitasResourceValidator()
        
        # Get system resources
        resources = validator.get_system_resources()
        
        # Validate resources
        risk_level, decision, warnings = validator.validate_resources(command, context)
        
        # Generate response
        response = {
            "allowed": decision != 'BLOCK',
            "risk_level": risk_level,
            "decision": decision,
            "warnings": warnings,
            "resources": resources,
            "command": command,
            "trinitas_analysis": {
                "springfield": f"Resource assessment complete - user guidance prioritized",
                "krukai": f"Performance metrics gathered - {len(warnings)} optimization opportunities",
                "vector": f"System protection active - {risk_level} risk level for resource exhaustion"
            }
        }
        
        # Add detailed report for resource-intensive operations
        if risk_level in ['CRITICAL', 'HIGH', 'MEDIUM']:
            response["resource_report"] = validator.generate_resource_report(resources)
        
        print(json.dumps(response, indent=2))
        sys.exit(0 if decision != 'BLOCK' else 1)
        
    except Exception as e:
        error_response = {
            "allowed": False,
            "error": f"Trinitas resource validation failed: {str(e)}",
            "risk_level": "UNKNOWN",
            "trinitas_status": "SYSTEM_ERROR"
        }
        print(json.dumps(error_response, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()