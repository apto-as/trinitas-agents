#!/usr/bin/env python3
"""
Test Developer Mode - Switch between mythology and Dolls Frontline 2 names
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.display_name_resolver import DisplayNameResolver, NamingMode, set_developer_mode
from core.trinitas_mcp_tools import TrinitasMCPTools

async def test_developer_mode():
    """Test developer mode functionality"""
    print("=" * 80)
    print("🎮 TRINITAS DEVELOPER MODE TEST")
    print("=" * 80)
    
    # Initialize tools
    tools = TrinitasMCPTools()
    await tools.ensure_initialized()
    resolver = DisplayNameResolver()
    
    # Test 1: Mythology Mode (Default)
    print("\n📚 TEST 1: MYTHOLOGY MODE (Default)")
    print("-" * 40)
    resolver.set_mode(NamingMode.MYTHOLOGY)
    
    personas = ["athena", "artemis", "hestia", "bellona", "seshat"]
    for persona in personas:
        display = resolver.get_display_name(persona)
        print(f"  {persona:10} → {display}")
    
    locations = ["cafe_olympus", "argonauts"]
    for location in locations:
        display = resolver.get_display_name(location)
        print(f"  {location:15} → {display}")
    
    orgs = ["olympian_systems", "aegis_protocol", "prometheus_incident"]
    for org in orgs:
        display = resolver.get_display_name(org)
        print(f"  {org:20} → {display}")
    
    # Test 2: Developer Mode
    print("\n🎮 TEST 2: DEVELOPER MODE (Dolls Frontline 2)")
    print("-" * 40)
    resolver.set_mode(NamingMode.DEVELOPER)
    
    for persona in personas:
        display = resolver.get_display_name(persona)
        print(f"  {persona:10} → {display}")
    
    for location in locations:
        display = resolver.get_display_name(location)
        print(f"  {location:15} → {display}")
    
    for org in orgs:
        display = resolver.get_display_name(org)
        print(f"  {org:20} → {display}")
    
    # Test 3: Reverse Conversion
    print("\n🔄 TEST 3: REVERSE CONVERSION (Developer → Internal)")
    print("-" * 40)
    
    dev_names = ["Springfield", "Krukai", "Vector", "Groza", "Littara",
                 "カフェ・ズッケロ", "エルモ号", "Griffin Systems", "H.I.D.E. 404"]
    
    for name in dev_names:
        internal = resolver.get_internal_name(name)
        print(f"  {name:20} → {internal}")
    
    # Test 4: Message Formatting
    print("\n📝 TEST 4: MESSAGE FORMATTING")
    print("-" * 40)
    
    messages = [
        "Athena is working with Artemis at Cafe Olympus",
        "Hestia detected a security issue in Olympian Systems",
        "Bellona and Seshat are deploying from Argonauts",
        "Aegis Protocol initiated after Prometheus Incident"
    ]
    
    print("\nMythology Mode:")
    resolver.set_mode(NamingMode.MYTHOLOGY)
    for msg in messages:
        formatted = resolver.format_message(msg)
        print(f"  → {formatted}")
    
    print("\nDeveloper Mode:")
    resolver.set_mode(NamingMode.DEVELOPER)
    for msg in messages:
        formatted = resolver.format_message(msg)
        print(f"  → {formatted}")
    
    # Test 5: Environment Variable Control
    print("\n🔧 TEST 5: ENVIRONMENT VARIABLE CONTROL")
    print("-" * 40)
    
    # Set environment variable
    os.environ["TRINITAS_NAMING_MODE"] = "developer"
    new_resolver = DisplayNameResolver()
    print(f"  Mode from env: {new_resolver.get_mode()}")
    print(f"  Athena displays as: {new_resolver.get_display_name('athena')}")
    
    # Clear environment variable
    del os.environ["TRINITAS_NAMING_MODE"]
    default_resolver = DisplayNameResolver()
    print(f"  Default mode: {default_resolver.get_mode()}")
    print(f"  Athena displays as: {default_resolver.get_display_name('athena')}")
    
    # Test 6: Persona Execution with Different Modes
    print("\n🚀 TEST 6: PERSONA EXECUTION WITH NAMING MODES")
    print("-" * 40)
    
    # Mythology mode execution
    print("\nMythology Mode Execution:")
    resolver.set_mode(NamingMode.MYTHOLOGY)
    result = await tools.persona_execute("athena", "Test task in mythology mode")
    if result.success:
        print(f"  ✅ Executed as: {result.persona}")
    
    # Developer mode execution - using original name
    print("\nDeveloper Mode Execution (using original name):")
    resolver.set_mode(NamingMode.DEVELOPER)
    set_developer_mode(True)  # Set global developer mode
    result = await tools.persona_execute("springfield", "Test task in developer mode")
    if result.success:
        print(f"  ✅ Executed as: {result.persona}")
    
    # Developer mode execution - using new name (should still work)
    print("\nDeveloper Mode Execution (using mythology name):")
    result = await tools.persona_execute("athena", "Test task with mixed names")
    if result.success:
        print(f"  ✅ Executed as: {result.persona}")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_developer_mode())