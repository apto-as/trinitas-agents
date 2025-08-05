#!/usr/bin/env python3
"""
Trinitas Parallel Results Integration
Krukai: "完璧な統合アルゴリズムで、全ての結果を効率的に処理するわ"
Springfield: "各エージェントの貢献を公平に評価し、最適な統合を実現します"
Vector: "……重複と矛盾を検出し、信頼性の高い結果のみを採用……"
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
from collections import defaultdict

# =====================================================
# Configuration
# =====================================================

RESULTS_DIR = Path(os.environ.get('TRINITAS_RESULTS_DIR', 
                                  Path.home() / '.claude' / 'trinitas' / 'parallel_results'))
COMPLETED_DIR = RESULTS_DIR / 'completed'
INTEGRATED_DIR = RESULTS_DIR / 'integrated'

# =====================================================
# Result Integration Logic
# =====================================================

class ParallelResultIntegrator:
    """Integrates results from multiple parallel agent executions"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.session_dir = COMPLETED_DIR / session_id
        self.results = []
        self.integrated_result = {
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'agent_results': {},
            'synthesis': {},
            'metadata': {}
        }
    
    def load_results(self) -> bool:
        """Load all results for the session"""
        if not self.session_dir.exists():
            print(f"[ERROR] Session directory not found: {self.session_dir}")
            return False
        
        result_files = list(self.session_dir.glob('*.json'))
        if not result_files:
            print(f"[WARNING] No result files found in: {self.session_dir}")
            return False
        
        for result_file in result_files:
            try:
                with open(result_file, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                    self.results.append(result)
            except Exception as e:
                print(f"[ERROR] Failed to load {result_file}: {e}")
        
        return len(self.results) > 0
    
    def integrate_results(self):
        """Integrate all results into a unified output"""
        # Group results by agent type
        by_agent = defaultdict(list)
        for result in self.results:
            agent_type = result.get('subagent_type', 'unknown')
            by_agent[agent_type].append(result)
        
        # Process each agent's results
        for agent_type, agent_results in by_agent.items():
            self.integrated_result['agent_results'][agent_type] = {
                'count': len(agent_results),
                'results': self._merge_agent_results(agent_type, agent_results),
                'execution_time_ms': sum(r.get('execution_time_ms', 0) for r in agent_results),
                'status': self._determine_status(agent_results)
            }
        
        # Create synthesis
        self.integrated_result['synthesis'] = self._synthesize_results()
        
        # Add metadata
        self.integrated_result['metadata'] = {
            'total_agents': len(by_agent),
            'total_results': len(self.results),
            'integration_timestamp': datetime.utcnow().isoformat() + 'Z',
            'total_execution_time_ms': sum(r.get('execution_time_ms', 0) for r in self.results)
        }
    
    def _merge_agent_results(self, agent_type: str, results: List[Dict]) -> Dict:
        """Merge multiple results from the same agent type"""
        if len(results) == 1:
            return {
                'content': results[0].get('result', ''),
                'error': results[0].get('error')
            }
        
        # For multiple results, create a structured merge
        merged = {
            'content': [],
            'errors': [],
            'duplicates_removed': 0
        }
        
        seen_hashes = set()
        for result in results:
            content = result.get('result', '')
            if content:
                # Check for duplicates using content hash
                content_hash = hashlib.md5(content.encode()).hexdigest()
                if content_hash not in seen_hashes:
                    seen_hashes.add(content_hash)
                    merged['content'].append(content)
                else:
                    merged['duplicates_removed'] += 1
            
            if result.get('error'):
                merged['errors'].append(result['error'])
        
        # Join content appropriately based on agent type
        if agent_type in ['trinitas-coordinator', 'springfield-strategist']:
            merged['content'] = '\n\n---\n\n'.join(merged['content'])
        else:
            merged['content'] = '\n'.join(merged['content'])
        
        return merged
    
    def _determine_status(self, results: List[Dict]) -> str:
        """Determine overall status from multiple results"""
        statuses = [r.get('status', 'unknown') for r in results]
        if all(s == 'success' for s in statuses):
            return 'success'
        elif any(s == 'error' for s in statuses):
            return 'partial_failure'
        else:
            return 'unknown'
    
    def _synthesize_results(self) -> Dict:
        """Create a synthesis of all agent results"""
        synthesis = {
            'summary': '',
            'key_insights': [],
            'recommendations': [],
            'consensus_level': 'high'
        }
        
        # Extract key information from each agent
        insights = []
        for agent_type, data in self.integrated_result['agent_results'].items():
            content = data['results'].get('content', '')
            if content:
                # Simple extraction - could be enhanced with NLP
                if 'recommendation' in content.lower():
                    synthesis['recommendations'].append(f"[{agent_type}] {content[:200]}...")
                if agent_type == 'vector-auditor' and 'risk' in content.lower():
                    insights.append(f"Security Risk identified by {agent_type}")
                elif agent_type == 'krukai-optimizer' and 'optimize' in content.lower():
                    insights.append(f"Optimization opportunity identified by {agent_type}")
        
        synthesis['key_insights'] = insights[:5]  # Top 5 insights
        synthesis['summary'] = f"Integrated results from {len(self.integrated_result['agent_results'])} agents"
        
        # Determine consensus level
        if len(self.integrated_result['agent_results']) > 1:
            # Simple consensus check - could be more sophisticated
            error_count = sum(1 for a in self.integrated_result['agent_results'].values() 
                            if a['status'] != 'success')
            if error_count == 0:
                synthesis['consensus_level'] = 'high'
            elif error_count == 1:
                synthesis['consensus_level'] = 'medium'
            else:
                synthesis['consensus_level'] = 'low'
        
        return synthesis
    
    def save_integrated_result(self):
        """Save the integrated result to file"""
        INTEGRATED_DIR.mkdir(parents=True, exist_ok=True)
        
        output_file = INTEGRATED_DIR / f"{self.session_id}_integrated.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.integrated_result, f, indent=2, ensure_ascii=False)
        
        print(f"[SUCCESS] Integrated result saved to: {output_file}")
        
        # Also create a summary file for easy reading
        summary_file = INTEGRATED_DIR / f"{self.session_id}_summary.md"
        self._create_summary_markdown(summary_file)
    
    def _create_summary_markdown(self, output_file: Path):
        """Create a human-readable markdown summary"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Parallel Execution Summary\n\n")
            f.write(f"**Session ID**: {self.session_id}\n")
            f.write(f"**Timestamp**: {self.integrated_result['timestamp']}\n")
            f.write(f"**Total Execution Time**: {self.integrated_result['metadata']['total_execution_time_ms']}ms\n\n")
            
            f.write("## Agent Results\n\n")
            for agent, data in self.integrated_result['agent_results'].items():
                f.write(f"### {agent}\n")
                f.write(f"- Status: {data['status']}\n")
                f.write(f"- Execution Time: {data['execution_time_ms']}ms\n")
                f.write(f"- Results: {len(data['results'].get('content', ''))} characters\n\n")
            
            f.write("## Synthesis\n\n")
            synthesis = self.integrated_result['synthesis']
            f.write(f"**Consensus Level**: {synthesis['consensus_level']}\n\n")
            
            if synthesis['key_insights']:
                f.write("### Key Insights\n")
                for insight in synthesis['key_insights']:
                    f.write(f"- {insight}\n")
                f.write("\n")
            
            if synthesis['recommendations']:
                f.write("### Recommendations\n")
                for rec in synthesis['recommendations']:
                    f.write(f"- {rec}\n")

# =====================================================
# Main Execution
# =====================================================

def main():
    """Main entry point for integration"""
    # Get session ID from environment or command line
    session_id = os.environ.get('TRINITAS_INTEGRATION_SESSION')
    if not session_id and len(sys.argv) > 1:
        session_id = sys.argv[1]
    
    if not session_id:
        print("[ERROR] No session ID provided")
        print("Usage: integrate_parallel_results.py <session_id>")
        print("   or: TRINITAS_INTEGRATION_SESSION=<session_id> integrate_parallel_results.py")
        return 1
    
    print(f"[INFO] Starting integration for session: {session_id}")
    
    # Create integrator
    integrator = ParallelResultIntegrator(session_id)
    
    # Load results
    if not integrator.load_results():
        print("[ERROR] Failed to load results")
        return 1
    
    print(f"[INFO] Loaded {len(integrator.results)} results")
    
    # Integrate results
    integrator.integrate_results()
    
    # Save integrated result
    integrator.save_integrated_result()
    
    print("[SUCCESS] Integration completed successfully")
    return 0

if __name__ == '__main__':
    sys.exit(main())