#!/usr/bin/env python3
"""
Trinitas v3.5 Mode Switching Demonstration
Interactive demo showcasing the complete mode switching system
"""

import asyncio
import json
from typing import Dict, Any
from trinitas_mcp_tools import TrinitasMCPTools
from trinitas_mode_manager import ExecutionMode

class ModeDemo:
    """Interactive demonstration of mode switching capabilities"""
    
    def __init__(self):
        self.tools = TrinitasMCPTools()
    
    async def run_demo(self):
        """Run the complete demonstration"""
        print("🌸 Trinitas v3.5 Mode Switching System Demonstration")
        print("=" * 80)
        print("カフェ・ズッケロへようこそ、指揮官。")
        print("三位一体統合知性システムのモード切り替え機能をご紹介いたします。\n")
        
        # Initialize system
        await self.tools.ensure_initialized()
        
        # Demo sections
        await self._demo_initial_status()
        await self._demo_mode_switching()
        await self._demo_persona_execution_comparison()
        await self._demo_collaboration()
        await self._demo_fallback_behavior()
        await self._final_status()
    
    async def _demo_initial_status(self):
        """Show initial system status"""
        print("📊 Initial System Status")
        print("-" * 40)
        
        mode_info = self.tools.get_mode_info()
        available_modes = self.tools.get_available_modes()
        
        print(f"Current Mode: {mode_info['mode']}")
        print(f"Description: {mode_info['description']}")
        print(f"Local LLM Available: {mode_info['availability']['local_llm']}")
        print(f"Claude Available: {mode_info['availability']['claude']}")
        
        print("\nPersona Executors:")
        for persona, executor in mode_info['executors'].items():
            print(f"  {persona.capitalize()}: {executor}")
        
        print("\nAvailable Modes:")
        for mode_name, mode_details in available_modes.items():
            status = "✓" if mode_details['available'] else "✗"
            req = " (requires Local LLM)" if mode_details.get('requires_local_llm') else ""
            print(f"  [{status}] {mode_name}: {mode_details['description']}{req}")
        
        await self._pause()
    
    async def _demo_mode_switching(self):
        """Demonstrate mode switching"""
        print("\n🔄 Mode Switching Demonstration")
        print("-" * 40)
        
        modes_to_demo = [
            ExecutionMode.SIMULATION,
            ExecutionMode.CLAUDE_ONLY,
            ExecutionMode.HYBRID,
            ExecutionMode.AUTO
        ]
        
        for mode in modes_to_demo:
            print(f"\n→ Switching to {mode.value.upper()} mode...")
            
            result = await self.tools.set_mode(mode.value)
            
            if result.success:
                mode_info = result.data['mode_info']
                print(f"  ✓ Successfully switched to {mode.value}")
                print(f"  Description: {mode_info['description']}")
                print(f"  Trinity executors: {mode_info['executors']['springfield']}, "
                      f"{mode_info['executors']['krukai']}, {mode_info['executors']['vector']}")
                print(f"  Extended team: {mode_info['executors']['groza']}, "
                      f"{mode_info['executors']['littara']}")
            else:
                print(f"  ✗ Failed to switch to {mode.value}: {result.error}")
            
            await asyncio.sleep(0.5)  # Brief pause for readability
        
        await self._pause()
    
    async def _demo_persona_execution_comparison(self):
        """Compare persona execution across different modes"""
        print("\n👥 Persona Execution Comparison")
        print("-" * 40)
        
        test_task = "Analyze the security implications of implementing a microservices architecture"
        personas_to_test = ["springfield", "groza", "littara"]
        modes_to_compare = [ExecutionMode.SIMULATION, ExecutionMode.CLAUDE_ONLY]
        
        execution_results = {}
        
        for mode in modes_to_compare:
            print(f"\n🔧 Testing in {mode.value.upper()} mode:")
            await self.tools.set_mode(mode.value)
            execution_results[mode.value] = {}
            
            for persona in personas_to_test:
                print(f"  {persona.capitalize()}: ", end="", flush=True)
                
                try:
                    result = await self.tools.persona_execute(persona, test_task)
                    
                    if result.success:
                        print("✓")
                        execution_results[mode.value][persona] = {
                            "success": True,
                            "executor": result.metadata.get("executor", "unknown"),
                            "response_preview": str(result.data)[:100] + "..." if len(str(result.data)) > 100 else str(result.data)
                        }
                    else:
                        print(f"✗ {result.error}")
                        execution_results[mode.value][persona] = {
                            "success": False,
                            "error": result.error
                        }
                        
                except Exception as e:
                    print(f"✗ Exception: {e}")
                    execution_results[mode.value][persona] = {
                        "success": False,
                        "error": str(e)
                    }
        
        # Show detailed comparison
        print("\n📋 Detailed Execution Results:")
        for mode, mode_results in execution_results.items():
            print(f"\n{mode.upper()} Mode Results:")
            for persona, result in mode_results.items():
                if result["success"]:
                    print(f"  {persona.capitalize()} [{result['executor']}]: {result['response_preview']}")
                else:
                    print(f"  {persona.capitalize()}: Failed - {result['error']}")
        
        await self._pause()
    
    async def _demo_collaboration(self):
        """Demonstrate collaboration in different modes"""
        print("\n🤝 Collaboration Demonstration")
        print("-" * 40)
        
        # Test Trinity collaboration
        print("\nTesting Trinity Core collaboration...")
        await self.tools.set_mode("claude_only")  # Use Claude for best results
        
        collab_result = await self.tools.collaborate_personas(
            ["springfield", "krukai", "vector"],
            "Design a secure authentication system for a distributed application",
            "sequential"
        )
        
        if collab_result.success:
            print("✓ Trinity collaboration successful!")
            results = collab_result.data.get("results", [])
            for i, result_item in enumerate(results):
                persona = result_item["persona"]
                response = result_item["result"]
                preview = response[:80] + "..." if len(response) > 80 else response
                print(f"  {i+1}. {persona.capitalize()}: {preview}")
        else:
            print(f"✗ Trinity collaboration failed: {collab_result.error}")
        
        await self._pause()
    
    async def _demo_fallback_behavior(self):
        """Demonstrate fallback behavior"""
        print("\n🛡️ Fallback Behavior Demonstration")
        print("-" * 40)
        
        print("Testing fallback behavior when Local LLM is unavailable...")
        
        # Force AUTO mode to test fallback
        await self.tools.set_mode("auto")
        
        # Test Groza execution (should fallback gracefully)
        print("\nTesting Groza execution with fallback:")
        result = await self.tools.persona_execute(
            "groza",
            "Provide tactical assessment of system deployment",
            {"test_scenario": "fallback_demonstration"}
        )
        
        if result.success:
            executor_used = result.metadata.get("executor", "unknown")
            print(f"✓ Groza execution successful using: {executor_used}")
            print(f"  Response: {str(result.data)[:100]}...")
            
            if executor_used == "simulation":
                print("  📝 Note: Fallback to simulation mode activated (Local LLM unavailable)")
            elif executor_used == "local_llm":
                print("  📝 Note: Local LLM successfully used")
        else:
            print(f"✗ Groza execution failed: {result.error}")
        
        await self._pause()
    
    async def _final_status(self):
        """Show final system status"""
        print("\n📈 Final System Status & Statistics")
        print("-" * 40)
        
        stats = self.tools.get_execution_stats()
        mode_info = self.tools.get_mode_info()
        
        print(f"Current Mode: {mode_info['mode']}")
        print(f"Total Executions: {stats['total_executions']}")
        print(f"Success Rate: {stats['success_rate']:.1%}")
        print(f"Personas Used: {', '.join(stats['personas_used'])}")
        
        if stats['recent_executions']:
            print("\nRecent Executions:")
            for i, execution in enumerate(stats['recent_executions'][-3:]):  # Last 3
                status = "✓" if execution['success'] else "✗"
                print(f"  {i+1}. [{status}] {execution['persona']}: {execution['task'][:50]}...")
        
        print(f"\nSystem Health: Local LLM: {stats['local_llm_available']}, Mode: {mode_info['mode']}")
        
        # Trinity farewell
        print("\n" + "=" * 80)
        print("🌸 Springfield: 「デモンストレーションは完了です。いかがでしたでしょうか？」")
        print("⚡ Krukai: 「フン、システムは完璧に動作したわね。404の誇りよ。」") 
        print("🛡️ Vector: 「……全テスト完了……システム正常稼働確認……」")
        print("\n指揮官、Trinitas-Core統合知性システムをご活用ください。")
        print("カフェ・ズッケロはいつでもお待ちしております。")
        print("=" * 80)
    
    async def _pause(self):
        """Brief pause for readability"""
        print("\n" + "·" * 40)
        await asyncio.sleep(1.5)

async def interactive_demo():
    """Run interactive demonstration"""
    demo = ModeDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(interactive_demo())