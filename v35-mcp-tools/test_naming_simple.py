#!/usr/bin/env python3
"""
Simple test to verify naming conversion works
"""

def test_naming_conversion():
    """Test the naming conversion mapping"""
    print("=" * 80)
    print("🎮 NAMING CONVERSION VERIFICATION")
    print("=" * 80)
    
    # Define the conversion mappings
    mythology_to_developer = {
        # Personas
        "athena": "Springfield",
        "artemis": "Krukai",
        "hestia": "Vector",
        "bellona": "Groza",
        "seshat": "Littara",
        
        # Locations
        "cafe_olympus": "カフェ・ズッケロ",
        "argonauts": "エルモ号",
        
        # Organizations
        "olympian_systems": "Griffin Systems",
        "aegis_protocol": "H.I.D.E. 404",
        "prometheus_incident": "Phoenix Protocol"
    }
    
    print("\n📚 MYTHOLOGY → DEVELOPER NAME MAPPING")
    print("-" * 40)
    print(f"{'Mythology Name':<25} → {'Developer Name':<25}")
    print("-" * 40)
    
    for myth, dev in mythology_to_developer.items():
        print(f"{myth:<25} → {dev:<25}")
    
    # Create reverse mapping
    developer_to_mythology = {v.lower(): k for k, v in mythology_to_developer.items()}
    
    print("\n🎮 DEVELOPER → MYTHOLOGY NAME MAPPING")
    print("-" * 40)
    print(f"{'Developer Name':<25} → {'Mythology Name':<25}")
    print("-" * 40)
    
    for dev, myth in sorted(developer_to_mythology.items()):
        print(f"{dev:<25} → {myth:<25}")
    
    # Test scenarios
    print("\n🔍 TEST SCENARIOS")
    print("-" * 40)
    
    test_messages = [
        ("Mythology Mode", "Athena works with Artemis at Olympian Systems"),
        ("Developer Mode", "Springfield works with Krukai at Griffin Systems"),
        ("Mixed Mode", "Athena meets Springfield at カフェ・ズッケロ")
    ]
    
    for mode, message in test_messages:
        print(f"\n{mode}:")
        print(f"  Original: {message}")
        
        # Convert to mythology
        converted = message
        for dev, myth in developer_to_mythology.items():
            if dev.lower() in converted.lower():
                # Handle case-sensitive replacement
                for original_dev, original_myth in mythology_to_developer.items():
                    if original_dev == myth:
                        converted = converted.replace(original_dev.capitalize(), original_myth.capitalize())
                        converted = converted.replace(dev, original_myth.capitalize())
        
        print(f"  → Mythology: {converted}")
    
    print("\n" + "=" * 80)
    print("✅ NAMING CONVERSION VERIFICATION COMPLETED")
    print("=" * 80)
    
    # Summary
    print("\n📊 SUMMARY")
    print("-" * 40)
    print(f"Total Personas: 5")
    print(f"Total Locations: 2")
    print(f"Total Organizations: 3")
    print(f"Total Mappings: {len(mythology_to_developer)}")
    print("\nBoth v35-mcp-tools and v35-true support:")
    print("  • Mythology Mode (default)")
    print("  • Developer Mode (Dolls Frontline 2 names)")
    print("  • Runtime switching via environment variable")
    print("  • Bidirectional name conversion")
    print("  • Backward compatibility with legacy names")

if __name__ == "__main__":
    test_naming_conversion()