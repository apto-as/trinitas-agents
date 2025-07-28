#!/usr/bin/env python3
"""
Project Trinitas v2.0 - Test Utilities
Comprehensive testing and validation utilities for Trinitas installation
"""

import os
import sys
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re

# Add color output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

def log_info(message: str) -> None:
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

def log_success(message: str) -> None:
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def log_warning(message: str) -> None:
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def log_error(message: str) -> None:
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

class TrinitasTestSuite:
    """Comprehensive test suite for Trinitas installation and functionality"""
    
    def __init__(self):
        self.home_dir = Path.home()
        self.claude_dir = self.home_dir / ".claude"
        self.agents_dir = self.claude_dir / "agents"
        self.trinitas_dir = self.agents_dir / "trinitas"
        
        self.required_agents = [
            "trinitas-coordinator.md",
            "springfield-strategist.md", 
            "krukai-optimizer.md",
            "vector-auditor.md",
            "trinitas-workflow.md",
            "trinitas-quality.md"
        ]
        
        self.test_results = []
    
    def run_all_tests(self) -> bool:
        """Run complete test suite"""
        log_info("Starting Trinitas comprehensive test suite...")
        
        tests = [
            ("Environment Setup", self.test_environment_setup),
            ("Agent Files", self.test_agent_files),
            ("Agent Structure", self.test_agent_structure),
            ("Configuration", self.test_configuration),
            ("Claude Integration", self.test_claude_integration),
            ("Auto-Detection", self.test_auto_detection),
            ("Quality Gates", self.test_quality_gates),
            ("Utility Scripts", self.test_utility_scripts)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            log_info(f"Running test: {test_name}")
            try:
                result = test_func()
                if result:
                    log_success(f"✓ {test_name}")
                    passed += 1
                else:
                    log_error(f"✗ {test_name}")
                self.test_results.append((test_name, result))
            except Exception as e:
                log_error(f"✗ {test_name} - Exception: {str(e)}")
                self.test_results.append((test_name, False))
        
        # Summary
        print(f"\n{Colors.WHITE}=== Test Summary ==={Colors.NC}")
        print(f"Passed: {Colors.GREEN}{passed}{Colors.NC}/{total}")
        print(f"Failed: {Colors.RED}{total - passed}{Colors.NC}/{total}")
        
        if passed == total:
            log_success("All tests passed! Trinitas is properly installed.")
            return True
        else:
            log_warning(f"{total - passed} tests failed. Please check the issues above.")
            return False
    
    def test_environment_setup(self) -> bool:
        """Test basic environment setup"""
        checks = [
            (self.claude_dir.exists(), "Claude directory exists"),
            (self.agents_dir.exists(), "Agents directory exists"),
            (self.trinitas_dir.exists(), "Trinitas directory exists")
        ]
        
        all_passed = True
        for check, description in checks:
            if check:
                log_success(f"  ✓ {description}")
            else:
                log_error(f"  ✗ {description}")
                all_passed = False
        
        return all_passed
    
    def test_agent_files(self) -> bool:
        """Test that all required agent files exist"""
        all_passed = True
        
        for agent in self.required_agents:
            agent_path = self.agents_dir / agent
            if agent_path.exists():
                log_success(f"  ✓ {agent}")
            else:
                log_error(f"  ✗ {agent} not found")
                all_passed = False
        
        return all_passed
    
    def test_agent_structure(self) -> bool:
        """Test agent file structure and content"""
        all_passed = True
        
        required_patterns = [
            (r"^name:", "Name field"),
            (r"description:.*MUST BE USED", "MUST BE USED pattern"),
            (r"tools:", "Tools specification"),
            (r"color:", "Color specification")
        ]
        
        for agent in self.required_agents:
            agent_path = self.agents_dir / agent
            if not agent_path.exists():
                continue
                
            try:
                content = agent_path.read_text()
                agent_passed = True
                
                for pattern, description in required_patterns:
                    if re.search(pattern, content, re.MULTILINE):
                        log_success(f"  ✓ {agent}: {description}")
                    else:
                        log_error(f"  ✗ {agent}: Missing {description}")
                        agent_passed = False
                        all_passed = False
                
            except Exception as e:
                log_error(f"  ✗ {agent}: Error reading file - {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_configuration(self) -> bool:
        """Test configuration files"""
        config_path = self.trinitas_dir / "config.yaml"
        
        if not config_path.exists():
            log_warning("  Configuration file not found - using defaults")
            return True
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            required_sections = ['trinitas', 'personalities', 'agent_config']
            all_passed = True
            
            for section in required_sections:
                if section in config:
                    log_success(f"  ✓ Configuration section: {section}")
                else:
                    log_error(f"  ✗ Missing configuration section: {section}")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            log_error(f"  ✗ Configuration file error: {str(e)}")
            return False
    
    def test_claude_integration(self) -> bool:
        """Test Claude Code integration"""
        try:
            # Check if Claude is available
            result = subprocess.run(['claude', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                log_success(f"  ✓ Claude Code available: {result.stdout.strip()}")
            else:
                log_error("  ✗ Claude Code not available")
                return False
            
            # Check agent listing
            result = subprocess.run(['claude', '--list-agents'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                agents_found = 0
                for agent in self.required_agents:
                    agent_name = agent.replace('.md', '')
                    if agent_name in result.stdout:
                        agents_found += 1
                
                if agents_found == len(self.required_agents):
                    log_success(f"  ✓ All {len(self.required_agents)} agents detected by Claude")
                else:
                    log_warning(f"  ! Only {agents_found}/{len(self.required_agents)} agents detected")
                
                return True
            else:
                log_error("  ✗ Failed to list agents")
                return False
                
        except subprocess.TimeoutExpired:
            log_error("  ✗ Claude command timed out")
            return False
        except FileNotFoundError:
            log_error("  ✗ Claude command not found")
            return False
        except Exception as e:
            log_error(f"  ✗ Claude integration error: {str(e)}")
            return False
    
    def test_auto_detection(self) -> bool:
        """Test agent auto-detection patterns"""
        test_cases = [
            ("trinitas-coordinator", ["comprehensive analysis", "three perspectives"]),
            ("springfield-strategist", ["strategic planning", "long-term roadmap"]),
            ("krukai-optimizer", ["performance optimization", "code quality"]),
            ("vector-auditor", ["security audit", "risk assessment"]),
            ("trinitas-workflow", ["development workflow", "automation pipeline"]),
            ("trinitas-quality", ["quality assurance", "testing strategy"])
        ]
        
        all_passed = True
        
        for agent_name, keywords in test_cases:
            agent_path = self.agents_dir / f"{agent_name}.md"
            if not agent_path.exists():
                continue
            
            try:
                content = agent_path.read_text().lower()
                keywords_found = sum(1 for keyword in keywords if keyword.lower() in content)
                
                if keywords_found >= len(keywords) // 2:  # At least half keywords found
                    log_success(f"  ✓ {agent_name}: Auto-detection keywords present")
                else:
                    log_warning(f"  ! {agent_name}: Limited auto-detection keywords")
                    
            except Exception as e:
                log_error(f"  ✗ {agent_name}: Error checking keywords - {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_quality_gates(self) -> bool:
        """Test quality gate specifications"""
        quality_agent = self.agents_dir / "trinitas-quality.md"
        
        if not quality_agent.exists():
            log_error("  ✗ Quality agent not found")
            return False
        
        try:
            content = quality_agent.read_text()
            
            quality_checks = [
                "syntax_validation",
                "type_safety", 
                "code_quality",
                "security_validation",
                "testing_validation",
                "performance_validation"
            ]
            
            found_checks = sum(1 for check in quality_checks if check in content)
            
            if found_checks >= len(quality_checks) * 0.75:  # At least 75% found
                log_success(f"  ✓ Quality gates defined ({found_checks}/{len(quality_checks)})")
                return True
            else:
                log_warning(f"  ! Limited quality gates defined ({found_checks}/{len(quality_checks)})")
                return False
                
        except Exception as e:
            log_error(f"  ✗ Error checking quality gates: {str(e)}")
            return False
    
    def test_utility_scripts(self) -> bool:
        """Test utility scripts presence and basic structure"""
        utils_dir = self.trinitas_dir / "utils"
        
        if not utils_dir.exists():
            log_warning("  ! Utility scripts directory not found - advanced features unavailable")
            return True  # Optional component
        
        script_files = list(utils_dir.glob("*.py"))
        
        if script_files:
            log_success(f"  ✓ {len(script_files)} utility scripts found")
            return True
        else:
            log_warning("  ! No utility scripts found")
            return True  # Optional component

def generate_diagnostic_report() -> str:
    """Generate comprehensive diagnostic report"""
    report = []
    report.append("=== Project Trinitas Diagnostic Report ===")
    report.append(f"Generated: {subprocess.check_output(['date']).decode().strip()}")
    report.append("")
    
    # System information
    report.append("--- System Information ---")
    try:
        report.append(f"OS: {os.uname().sysname} {os.uname().release}")
        report.append(f"Python: {sys.version}")
        report.append(f"Home: {Path.home()}")
    except:
        report.append("System information unavailable")
    
    report.append("")
    
    # Claude information
    report.append("--- Claude Code Information ---")
    try:
        result = subprocess.run(['claude', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            report.append(f"Claude Version: {result.stdout.strip()}")
        else:
            report.append("Claude Code not available")
    except:
        report.append("Claude Code not found")
    
    report.append("")
    
    # Directory structure
    report.append("--- Directory Structure ---")
    claude_dir = Path.home() / ".claude"
    if claude_dir.exists():
        for item in claude_dir.rglob("*"):
            if "trinitas" in str(item).lower():
                report.append(f"  {item}")
    else:
        report.append("  Claude directory not found")
    
    return "\n".join(report)

def main():
    """Main test runner"""
    if len(sys.argv) > 1 and sys.argv[1] == "diagnostic":
        print(generate_diagnostic_report())
        return
    
    test_suite = TrinitasTestSuite()
    success = test_suite.run_all_tests()
    
    if not success:
        print(f"\n{Colors.YELLOW}For additional debugging information, run:{Colors.NC}")
        print(f"  python {__file__} diagnostic")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()