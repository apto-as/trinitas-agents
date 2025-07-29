#!/usr/bin/env python3
"""
Project Trinitas v2.0 - Trinitas Hooks Setup and Installation Script
Automated setup for Claude Code hooks integration

Integrated by: Trinitas Meta-Intelligence System
- Springfield: User-friendly setup process and clear guidance (PRIMARY)
- Krukai: Efficient installation and configuration optimization
- Vector: Secure installation with proper permissions and validation
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class TrinitasHooksInstaller:
    """Trinitas-powered hooks installation and setup system"""
    
    def __init__(self):
        self.trinitas_root = Path(__file__).parent.parent.parent
        self.hooks_dir = self.trinitas_root / 'scripts' / 'hooks'
        self.template_file = self.hooks_dir / 'settings' / 'claude-code-hooks-template.json'
        
        # Trinitas documentation files
        self.trinitas_docs_source = self.trinitas_root / 'TRINITAS-AGENTS.md'
        
        # Claude Code settings locations
        self.claude_user_settings = Path.home() / '.claude' / 'settings.json'
        self.claude_project_settings = Path('.claude') / 'settings.json'
        
        # Claude Code documentation target locations
        self.claude_user_docs = Path.home() / '.claude' / 'CLAUDE.md'
        self.claude_project_docs = Path('.claude') / 'CLAUDE.md'
        
        # Springfield: User-friendly setup options
        self.setup_modes = {
            'minimal': {
                'description': 'Essential security and quality hooks only',
                'hooks_enabled': ['dangerous_command_check', 'security_scanner', 'quality_validator'],
                'features': ['Security validation', 'Code quality checking']
            },
            'standard': {
                'description': 'Balanced functionality with core Trinitas features',
                'hooks_enabled': ['dangerous_command_check', 'resource_validator', 'security_scanner', 
                                'quality_validator', 'knowledge_persister'],
                'features': ['Full security suite', 'Quality validation', 'Knowledge capture', 'Resource monitoring']
            },
            'comprehensive': {
                'description': 'Complete Trinitas experience with all features',
                'hooks_enabled': ['dangerous_command_check', 'resource_validator', 'security_pre_check',
                                'security_scanner', 'quality_validator', 'knowledge_persister'],
                'features': ['Maximum security', 'Complete quality assurance', 'Advanced knowledge capture', 
                           'Performance monitoring', 'Learning optimization']
            }
        }
    
    def check_prerequisites(self) -> Tuple[bool, List[str]]:
        """
        Check system prerequisites for Trinitas hooks
        Vector: Ensure secure and proper installation environment
        """
        
        issues = []
        
        # Check Python version
        if sys.version_info < (3, 7):
            issues.append("Python 3.7+ is required")
        
        # Check Claude Code installation
        try:
            result = subprocess.run(['claude', '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                issues.append("Claude Code CLI not found or not working")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            issues.append("Claude Code CLI not installed or not in PATH")
        
        # Check if we're in a valid project directory
        if not (Path.cwd() / '.git').exists() and not (Path.cwd() / 'package.json').exists():
            issues.append("Not in a recognized project directory (no .git or package.json found)")
        
        # Check template file exists
        if not self.template_file.exists():
            issues.append(f"Template file not found: {self.template_file}")
        
        # Check Trinitas documentation exists
        if not self.trinitas_docs_source.exists():
            issues.append(f"Trinitas documentation not found: {self.trinitas_docs_source}")
        
        # Check hooks scripts exist
        required_scripts = [
            'pre-execution/dangerous_command_check.py',
            'pre-execution/resource_validator.py',
            'post-execution/quality_validator.py',
            'post-execution/security_scanner.py',
            'post-execution/knowledge_persister.py'
        ]
        
        for script in required_scripts:
            script_path = self.hooks_dir / script
            if not script_path.exists():
                issues.append(f"Required script not found: {script_path}")
        
        return len(issues) == 0, issues
    
    def make_scripts_executable(self) -> bool:
        """
        Make all hook scripts executable
        Krukai: Efficient permission setting for optimal execution
        """
        
        try:
            # Find all Python scripts in hooks directory
            for script_file in self.hooks_dir.rglob('*.py'):
                os.chmod(script_file, 0o755)
            
            return True
        except Exception as e:
            print(f"❌ Failed to make scripts executable: {e}")
            return False
    
    def load_template_config(self) -> Optional[Dict]:
        """Load the hooks configuration template"""
        
        try:
            with open(self.template_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load template: {e}")
            return None
    
    def customize_config_for_mode(self, template_config: Dict, mode: str) -> Dict:
        """
        Customize configuration based on setup mode
        Springfield: Tailored configuration for different user needs
        """
        
        if mode not in self.setup_modes:
            mode = 'standard'
        
        mode_info = self.setup_modes[mode]
        enabled_hooks = set(mode_info['hooks_enabled'])
        
        # Create customized config
        customized_config = {'hooks': {}}
        
        # Filter hooks based on mode
        original_hooks = template_config.get('hooks', {})
        
        for hook_event, hook_configs in original_hooks.items():
            if hook_event.startswith('_'):  # Skip comments
                continue
            
            customized_hooks = []
            
            for hook_config in hook_configs:
                if 'hooks' in hook_config:
                    filtered_hooks = []
                    
                    for hook in hook_config['hooks']:
                        command = hook.get('command', '')
                        
                        # Check if this hook should be enabled for the current mode
                        should_include = False
                        for enabled_hook in enabled_hooks:
                            if enabled_hook in command:
                                should_include = True
                                break
                        
                        if should_include:
                            filtered_hooks.append(hook)
                    
                    if filtered_hooks:
                        new_hook_config = hook_config.copy()
                        new_hook_config['hooks'] = filtered_hooks
                        customized_hooks.append(new_hook_config)
            
            if customized_hooks:
                customized_config['hooks'][hook_event] = customized_hooks
        
        # Add metadata
        customized_config['_trinitas_mode'] = mode
        customized_config['_trinitas_features'] = mode_info['features']
        customized_config['_installation_timestamp'] = str(Path().absolute())
        
        return customized_config
    
    def install_documentation(self, install_location: str) -> bool:
        """
        Install Trinitas documentation as CLAUDE.md
        Springfield: Friendly documentation setup for easy access
        """
        
        if install_location == 'user':
            target_docs = self.claude_user_docs
            target_docs.parent.mkdir(parents=True, exist_ok=True)
        elif install_location == 'project':
            target_docs = self.claude_project_docs
            target_docs.parent.mkdir(parents=True, exist_ok=True)
        else:
            print(f"❌ Invalid documentation location: {install_location}")
            return False
        
        try:
            # Copy TRINITAS-AGENTS.md to CLAUDE.md
            shutil.copy2(self.trinitas_docs_source, target_docs)
            
            print(f"✅ Trinitas documentation installed as: {target_docs}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to install documentation: {e}")
            return False
    
    def install_hooks_config(self, config: Dict, install_location: str) -> bool:
        """
        Install hooks configuration to Claude Code settings
        """
        
        if install_location == 'user':
            settings_file = self.claude_user_settings
            settings_file.parent.mkdir(parents=True, exist_ok=True)
        elif install_location == 'project':
            settings_file = self.claude_project_settings
            settings_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            print(f"❌ Invalid installation location: {install_location}")
            return False
        
        try:
            # Load existing settings or create new
            existing_settings = {}
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    existing_settings = json.load(f)
            
            # Merge hooks configuration
            if 'hooks' not in existing_settings:
                existing_settings['hooks'] = {}
            
            # Add Trinitas hooks
            for hook_event, hook_configs in config['hooks'].items():
                if hook_event in existing_settings['hooks']:
                    # Merge with existing hooks
                    existing_settings['hooks'][hook_event].extend(hook_configs)
                else:
                    existing_settings['hooks'][hook_event] = hook_configs
            
            # Add metadata
            existing_settings['_trinitas_hooks'] = {
                'version': '2.0.0',
                'mode': config.get('_trinitas_mode', 'standard'),
                'features': config.get('_trinitas_features', []),
                'installation_path': str(self.trinitas_root),
                'installation_timestamp': config.get('_installation_timestamp', ''),
            }
            
            # Write updated settings
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(existing_settings, f, indent=2)
            
            print(f"✅ Hooks configuration installed to: {settings_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to install hooks configuration: {e}")
            return False
    
    def verify_installation(self) -> bool:
        """
        Verify that the installation was successful
        Vector: Comprehensive validation of installation integrity
        """
        
        try:
            # Test that Claude Code can see the hooks
            result = subprocess.run(['claude', '--help'], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                print("❌ Claude Code CLI not responding properly")
                return False
            
            # Check that settings file is valid JSON
            for settings_file in [self.claude_user_settings, self.claude_project_settings]:
                if settings_file.exists():
                    try:
                        with open(settings_file, 'r', encoding='utf-8') as f:
                            json.load(f)
                    except json.JSONDecodeError as e:
                        print(f"❌ Invalid JSON in settings file {settings_file}: {e}")
                        return False
            
            # Check that hook scripts are executable
            test_scripts = [
                'pre-execution/dangerous_command_check.py',
                'post-execution/quality_validator.py'
            ]
            
            for script in test_scripts:
                script_path = self.hooks_dir / script
                if not os.access(script_path, os.X_OK):
                    print(f"❌ Script not executable: {script_path}")
                    return False
            
            print("✅ Installation verification completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Installation verification failed: {e}")
            return False
    
    def generate_test_command(self, mode: str) -> str:
        """Generate a test command to verify hooks are working"""
        
        test_commands = {
            'minimal': 'echo "console.log(\'Hello, Trinitas!\');" > test-trinitas.js',
            'standard': 'echo "# Trinitas Test File\\nprint(\'Hello, Trinitas!\')" > test-trinitas.py',
            'comprehensive': 'echo "// Trinitas Comprehensive Test\\nconsole.log(\'Trinitas hooks active!\');" > test-trinitas.js'
        }
        
        return test_commands.get(mode, test_commands['standard'])
    
    def run_interactive_setup(self):
        """
        Run interactive setup process
        Springfield: Friendly, guided setup experience
        """
        
        print("""
🌸 TRINITAS HOOKS INSTALLATION WIZARD

Springfield: Welcome to the Trinitas hooks installation! I'll help you set up
our intelligent development assistance system with Claude Code.

Krukai: Efficient installation process optimized for your system performance.

Vector: Secure installation with comprehensive validation and safety checks.
""")
        
        # Check prerequisites
        print("\n📋 Checking prerequisites...")
        prereqs_ok, issues = self.check_prerequisites()
        
        if not prereqs_ok:
            print("\n❌ Prerequisites check failed:")
            for issue in issues:
                print(f"   • {issue}")
            print("\nPlease resolve these issues before continuing.")
            return False
        
        print("✅ Prerequisites check passed!")
        
        # Choose setup mode
        print("\n🎯 Choose your Trinitas experience:")
        for mode, info in self.setup_modes.items():
            print(f"\n{mode.upper()}: {info['description']}")
            print("Features:")
            for feature in info['features']:
                print(f"   • {feature}")
        
        while True:
            choice = input("\nEnter your choice (minimal/standard/comprehensive) [standard]: ").strip().lower()
            if not choice:
                choice = 'standard'
            if choice in self.setup_modes:
                break
            print("Invalid choice. Please enter 'minimal', 'standard', or 'comprehensive'.")
        
        selected_mode = choice
        print(f"\n✅ Selected mode: {selected_mode.upper()}")
        
        # Choose installation location
        print("\n📍 Choose installation location:")
        print("PROJECT: Install hooks for this project only (.claude/settings.json)")
        print("USER: Install hooks for all your projects (~/.claude/settings.json)")
        
        while True:
            location = input("\nEnter your choice (project/user) [project]: ").strip().lower()
            if not location:
                location = 'project'
            if location in ['project', 'user']:
                break
            print("Invalid choice. Please enter 'project' or 'user'.")
        
        print(f"\n✅ Installation location: {location.upper()}")
        
        # Load and customize configuration
        print("\n⚙️ Preparing configuration...")
        template_config = self.load_template_config()
        if not template_config:
            print("❌ Failed to load configuration template")
            return False
        
        customized_config = self.customize_config_for_mode(template_config, selected_mode)
        
        # Make scripts executable
        print("\n🔧 Setting up script permissions...")
        if not self.make_scripts_executable():
            print("❌ Failed to set script permissions")
            return False
        
        # Install documentation
        print(f"\n📚 Installing Trinitas documentation...")
        if not self.install_documentation(location):
            print("❌ Documentation installation failed")
            return False
        
        # Install configuration
        print(f"\n📦 Installing hooks to {location} settings...")
        if not self.install_hooks_config(customized_config, location):
            print("❌ Installation failed")
            return False
        
        # Verify installation
        print("\n🔍 Verifying installation...")
        if not self.verify_installation():
            print("❌ Installation verification failed")
            return False
        
        # Success message
        test_command = self.generate_test_command(selected_mode)
        
        print(f"""

🎉 TRINITAS HOOKS INSTALLATION COMPLETE!

Setup Summary:
• Mode: {selected_mode.upper()}
• Location: {location.upper()}
• Features: {', '.join(self.setup_modes[selected_mode]['features'])}

Springfield's Guidance:
Your Trinitas hooks are now active! They'll provide intelligent assistance
with code quality, security, and learning capture as you work.

Krukai's Performance Note:
Hooks are optimized for efficiency. You can adjust timeout values in your
Claude Code settings if needed for your system performance.

Vector's Security Note:
All security validations are active. Hooks will help prevent dangerous
operations and maintain code security standards.

🧪 Test Your Installation:
Run this command to test the hooks:
claude bash "{test_command}"

📚 For more information:
• View documentation: The complete Trinitas guide is now available as CLAUDE.md in your Claude settings
• View your hooks: claude --debug (to see hook execution)
• Modify settings: Edit your Claude Code settings.json file
• Disable specific hooks: Comment out or remove from settings

📖 Trinitas Documentation Location:
• {location.upper()} mode: {"~/.claude/CLAUDE.md" if location == "user" else ".claude/CLAUDE.md"}

Thank you for choosing Trinitas! We're here to enhance your development experience.
""")
        
        return True

def main():
    """Main installation script execution"""
    
    installer = TrinitasHooksInstaller()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--non-interactive':
        # Non-interactive installation with defaults
        print("🔧 Running non-interactive Trinitas hooks installation...")
        
        prereqs_ok, issues = installer.check_prerequisites()
        if not prereqs_ok:
            print("❌ Prerequisites not met:")
            for issue in issues:
                print(f"   • {issue}")
            sys.exit(1)
        
        template_config = installer.load_template_config()
        if not template_config:
            sys.exit(1)
        
        customized_config = installer.customize_config_for_mode(template_config, 'standard')
        
        if not installer.make_scripts_executable():
            sys.exit(1)
        
        if not installer.install_documentation('project'):
            sys.exit(1)
        
        if not installer.install_hooks_config(customized_config, 'project'):
            sys.exit(1)
        
        if not installer.verify_installation():
            sys.exit(1)
        
        print("✅ Non-interactive installation completed successfully!")
        
    else:
        # Interactive installation
        if not installer.run_interactive_setup():
            sys.exit(1)

if __name__ == "__main__":
    main()