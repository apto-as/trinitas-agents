#!/usr/bin/env python3
"""
Trinitas v3.5 - Display Name Resolver
Handles switching between mythology names and developer mode (Dolls Frontline 2) names
References unified persona definitions from TRINITAS_PERSONA_DEFINITIONS.yaml
"""

import os
import yaml
from enum import Enum
from typing import Dict, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class NamingMode(str, Enum):
    """Naming mode options"""
    MYTHOLOGY = "mythology"    # Default: Greek/Roman/Egyptian mythology names
    DEVELOPER = "developer"     # Developer mode: Dolls Frontline 2 names
    AUTO = "auto"              # Automatically determine based on context

class DisplayNameResolver:
    """Resolves display names based on current naming mode"""
    
    def __init__(self, mode: Optional[NamingMode] = None):
        """
        Initialize the display name resolver
        
        Args:
            mode: Naming mode to use. If None, reads from env/config
        """
        self.mode = mode or self._get_mode_from_config()
        self._load_persona_definitions()
        
        # Complete bidirectional mapping (augmented by persona definitions)
        self.mythology_to_developer = {
            # Personas
            "athena": "Springfield",
            "artemis": "Krukai",
            "hestia": "Vector",
            "bellona": "Groza",
            "seshat": "Littara",
            
            # Locations
            "cafe_olympus": "カフェ・ズッケロ",
            "cafe olympus": "カフェ・ズッケロ",
            "argonauts": "エルモ号",
            
            # Organizations
            "olympian_systems": "Griffin Systems",
            "olympian systems": "Griffin Systems",
            "aegis_protocol": "H.I.D.E. 404",
            "aegis protocol": "H.I.D.E. 404",
            "prometheus_incident": "Phoenix Protocol",
            "prometheus incident": "Phoenix Protocol",
            
            # Additional mappings for variations
            "olympian": "Griffin",
            "aegis": "H.I.D.E.",
            "prometheus": "Phoenix"
        }
        
        # Create reverse mapping
        self.developer_to_mythology = {
            v.lower(): k for k, v in self.mythology_to_developer.items()
        }
        
        # Add lowercase variations for case-insensitive matching
        self.developer_to_mythology.update({
            "springfield": "athena",
            "krukai": "artemis",
            "vector": "hestia",
            "groza": "bellona",
            "littara": "seshat",
            "griffin systems": "olympian_systems",
            "griffin": "olympian",
            "h.i.d.e. 404": "aegis_protocol",
            "h.i.d.e.": "aegis",
            "hide 404": "aegis_protocol",
            "phoenix protocol": "prometheus_incident",
            "phoenix": "prometheus"
        })
        
        logger.info(f"DisplayNameResolver initialized with mode: {self.mode}")
    
    def _load_persona_definitions(self):
        """Load persona definitions from unified YAML file"""
        # Try to find the unified definitions file
        possible_paths = [
            Path(__file__).parent.parent.parent.parent / "TRINITAS_PERSONA_DEFINITIONS.yaml",
            Path(os.getenv("PERSONA_DEFINITIONS", "./TRINITAS_PERSONA_DEFINITIONS.yaml")),
            Path("./TRINITAS_PERSONA_DEFINITIONS.yaml")
        ]
        
        for path in possible_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        self.persona_definitions = yaml.safe_load(f)
                        logger.info(f"Loaded persona definitions from {path}")
                        return
                except Exception as e:
                    logger.warning(f"Could not load persona definitions from {path}: {e}")
        
        logger.warning("Could not find TRINITAS_PERSONA_DEFINITIONS.yaml, using built-in mappings")
    
    def _get_mode_from_config(self) -> NamingMode:
        """Get naming mode from environment or config file"""
        # First check environment variable
        env_mode = os.getenv("TRINITAS_NAMING_MODE", "").lower()
        if env_mode in ["developer", "dev"]:
            logger.info("Developer mode activated via environment variable")
            return NamingMode.DEVELOPER
        elif env_mode in ["mythology", "myth"]:
            return NamingMode.MYTHOLOGY
        
        # Then check config file
        config_path = Path(__file__).parent.parent.parent / "config" / "naming_mode.yaml"
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    mode_str = config.get("naming", {}).get("default_mode", "mythology")
                    return NamingMode(mode_str)
            except Exception as e:
                logger.warning(f"Could not load naming config: {e}")
        
        # Default to mythology mode
        return NamingMode.MYTHOLOGY
    
    def get_display_name(self, internal_name: str) -> str:
        """
        Get display name based on current mode
        
        Args:
            internal_name: Internal name (always uses mythology names internally)
            
        Returns:
            Display name appropriate for current mode
        """
        if not internal_name:
            return internal_name
        
        name_lower = internal_name.lower()
        
        if self.mode == NamingMode.DEVELOPER:
            # Convert mythology -> developer
            if name_lower in self.mythology_to_developer:
                return self.mythology_to_developer[name_lower]
            # If not found, check if it's already a developer name
            if name_lower in self.developer_to_mythology:
                # Already in developer format, return with proper casing
                for myth, dev in self.mythology_to_developer.items():
                    if dev.lower() == name_lower:
                        return dev
        
        # For mythology mode or if no mapping found, return as-is
        # But capitalize properly
        if name_lower in ["athena", "artemis", "hestia", "bellona", "seshat"]:
            return internal_name.capitalize()
        
        return internal_name
    
    def get_internal_name(self, display_name: str) -> str:
        """
        Get internal name from display name
        
        Args:
            display_name: Display name (could be either mythology or developer)
            
        Returns:
            Internal name (always mythology format)
        """
        if not display_name:
            return display_name
        
        name_lower = display_name.lower()
        
        # Check if it's a developer name that needs conversion
        if name_lower in self.developer_to_mythology:
            return self.developer_to_mythology[name_lower]
        
        # Check if it's already a mythology name
        if name_lower in self.mythology_to_developer:
            return name_lower
        
        # Return as-is if no mapping found
        return display_name
    
    def format_message(self, message: str) -> str:
        """
        Format a message by replacing all known names with appropriate display names
        
        Args:
            message: Message containing names to replace
            
        Returns:
            Formatted message with names replaced based on current mode
        """
        result = message
        
        if self.mode == NamingMode.DEVELOPER:
            # Replace mythology names with developer names
            replacements = {
                "Athena": "Springfield",
                "Artemis": "Krukai", 
                "Hestia": "Vector",
                "Bellona": "Groza",
                "Seshat": "Littara",
                "Cafe Olympus": "カフェ・ズッケロ",
                "Argonauts": "エルモ号",
                "Olympian Systems": "Griffin Systems",
                "Aegis Protocol": "H.I.D.E. 404",
                "Prometheus Incident": "Phoenix Protocol",
                # Lowercase versions
                "athena": "Springfield",
                "artemis": "Krukai",
                "hestia": "Vector",
                "bellona": "Groza",
                "seshat": "Littara"
            }
        else:
            # Replace developer names with mythology names
            replacements = {
                "Springfield": "Athena",
                "Krukai": "Artemis",
                "Vector": "Hestia",
                "Groza": "Bellona",
                "Littara": "Seshat",
                "カフェ・ズッケロ": "Cafe Olympus",
                "エルモ号": "Argonauts",
                "Griffin Systems": "Olympian Systems",
                "H.I.D.E. 404": "Aegis Protocol",
                "Phoenix Protocol": "Prometheus Incident",
                # Lowercase versions
                "springfield": "Athena",
                "krukai": "Artemis",
                "vector": "Hestia",
                "groza": "Bellona",
                "littara": "Seshat"
            }
        
        for old_name, new_name in replacements.items():
            result = result.replace(old_name, new_name)
        
        return result
    
    def set_mode(self, mode: NamingMode):
        """
        Change the naming mode at runtime
        
        Args:
            mode: New naming mode to use
        """
        old_mode = self.mode
        self.mode = mode
        logger.info(f"Naming mode changed from {old_mode} to {mode}")
    
    def get_mode(self) -> NamingMode:
        """Get current naming mode"""
        return self.mode
    
    def get_persona_title(self, internal_name: str) -> str:
        """
        Get full title for a persona
        
        Args:
            internal_name: Internal persona name
            
        Returns:
            Full title with appropriate name
        """
        titles = {
            "athena": "Strategic Architect",
            "artemis": "Technical Perfectionist",
            "hestia": "Paranoid Guardian",
            "bellona": "Tactical Coordinator",
            "seshat": "Implementation Specialist"
        }
        
        display_name = self.get_display_name(internal_name)
        title = titles.get(internal_name.lower(), "")
        
        if title:
            return f"{display_name} - {title}"
        return display_name
    
    def get_location_description(self, internal_name: str) -> str:
        """
        Get full description for a location
        
        Args:
            internal_name: Internal location name
            
        Returns:
            Full description with appropriate name
        """
        descriptions = {
            "cafe_olympus": "Central development hub",
            "argonauts": "Mobile command center"
        }
        
        display_name = self.get_display_name(internal_name)
        desc = descriptions.get(internal_name.lower(), "")
        
        if desc:
            return f"{display_name} ({desc})"
        return display_name


# Global instance
display_resolver = DisplayNameResolver()


def get_display_name(internal_name: str) -> str:
    """Convenience function to get display name"""
    return display_resolver.get_display_name(internal_name)


def get_internal_name(display_name: str) -> str:
    """Convenience function to get internal name"""
    return display_resolver.get_internal_name(display_name)


def format_message(message: str) -> str:
    """Convenience function to format message"""
    return display_resolver.format_message(message)


def set_developer_mode(enabled: bool = True):
    """Enable or disable developer mode"""
    mode = NamingMode.DEVELOPER if enabled else NamingMode.MYTHOLOGY
    display_resolver.set_mode(mode)
    

def is_developer_mode() -> bool:
    """Check if currently in developer mode"""
    return display_resolver.get_mode() == NamingMode.DEVELOPER


if __name__ == "__main__":
    # Test the resolver
    print("Testing Display Name Resolver")
    print("=" * 60)
    
    # Test mythology mode
    resolver = DisplayNameResolver(NamingMode.MYTHOLOGY)
    print("\n🏛️ MYTHOLOGY MODE:")
    print(f"athena -> {resolver.get_display_name('athena')}")
    print(f"cafe_olympus -> {resolver.get_display_name('cafe_olympus')}")
    print(f"olympian_systems -> {resolver.get_display_name('olympian_systems')}")
    
    # Test developer mode
    resolver.set_mode(NamingMode.DEVELOPER)
    print("\n🎮 DEVELOPER MODE:")
    print(f"athena -> {resolver.get_display_name('athena')}")
    print(f"cafe_olympus -> {resolver.get_display_name('cafe_olympus')}")
    print(f"olympian_systems -> {resolver.get_display_name('olympian_systems')}")
    
    # Test reverse conversion
    print("\n🔄 REVERSE CONVERSION:")
    print(f"Springfield -> {resolver.get_internal_name('Springfield')}")
    print(f"カフェ・ズッケロ -> {resolver.get_internal_name('カフェ・ズッケロ')}")
    print(f"Griffin Systems -> {resolver.get_internal_name('Griffin Systems')}")
    
    # Test message formatting
    print("\n📝 MESSAGE FORMATTING:")
    test_message = "Athena is working at Cafe Olympus for Olympian Systems"
    
    resolver.set_mode(NamingMode.MYTHOLOGY)
    print(f"Mythology: {resolver.format_message(test_message)}")
    
    resolver.set_mode(NamingMode.DEVELOPER)
    print(f"Developer: {resolver.format_message(test_message)}")