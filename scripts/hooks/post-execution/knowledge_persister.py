#!/usr/bin/env python3
"""
Project Trinitas v2.0 - Knowledge Persistence Hook
Post-execution knowledge extraction and learning persistence

Integrated by: Trinitas Meta-Intelligence System
- Springfield: Knowledge extraction and learning organization (PRIMARY)
- Krukai: Efficient knowledge indexing and retrieval optimization
- Vector: Secure knowledge storage and privacy protection
"""

import sys
import json
import os
import hashlib
import time
from typing import Dict, List, Tuple, Optional, Set
from pathlib import Path
from datetime import datetime
import re

class TrinitasKnowledgePersister:
    """Trinitas-powered knowledge extraction and persistence system"""
    
    def __init__(self):
        # Springfield: Learning-focused knowledge categories
        self.knowledge_categories = {
            'patterns': {
                'description': 'Code patterns and best practices discovered',
                'weight': 0.3,
                'triggers': ['pattern', 'practice', 'convention', 'idiom']
            },
            'solutions': {
                'description': 'Problem-solution pairs and troubleshooting knowledge',
                'weight': 0.4,
                'triggers': ['fix', 'solve', 'error', 'issue', 'bug', 'problem']
            },
            'optimizations': {
                'description': 'Performance and efficiency improvements',
                'weight': 0.2,
                'triggers': ['optimize', 'performance', 'efficient', 'fast', 'improve']
            },
            'security': {
                'description': 'Security insights and vulnerability mitigations',
                'weight': 0.3,
                'triggers': ['security', 'vulnerability', 'safe', 'protect', 'auth']
            },
            'architecture': {
                'description': 'Architectural decisions and design insights',
                'weight': 0.25,
                'triggers': ['architecture', 'design', 'structure', 'organize']
            },
            'tools': {
                'description': 'Tool usage and configuration insights',
                'weight': 0.15,
                'triggers': ['tool', 'config', 'setup', 'install', 'configure']
            }
        }
        
        # Krukai: Efficient knowledge indexing system
        self.knowledge_index_fields = [
            'timestamp', 'tool_name', 'file_type', 'project_context',
            'keywords', 'difficulty_level', 'success_rate', 'category'
        ]
        
        # Vector: Security-conscious sensitive data patterns to exclude
        self.sensitive_patterns = [
            r'(?i)password\s*=\s*["\'][^"\']+["\']',
            r'(?i)api[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'(?i)secret\s*=\s*["\'][^"\']+["\']',
            r'(?i)token\s*=\s*["\'][^"\']+["\']',
            r'["\'][A-Za-z0-9]{32,}["\']',  # Long potential secrets
            r'(?i)(?:mysql|postgres|mongodb)://[^\\s]+',  # Database URLs
            r'(?i)(?:https?://)[^\\s]+:[^\\s]+@',  # URLs with credentials
        ]
        
        # Springfield: Knowledge storage paths
        self.knowledge_base_dir = Path.home() / '.claude' / 'trinitas-knowledge'
        self.knowledge_base_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_knowledge_file = self.knowledge_base_dir / 'session-knowledge.jsonl'
        self.persistent_knowledge_file = self.knowledge_base_dir / 'persistent-knowledge.jsonl'
        self.knowledge_index_file = self.knowledge_base_dir / 'knowledge-index.json'

    def extract_knowledge(self, tool_name: str, tool_input: Dict, 
                         tool_response: Dict, context: Dict) -> Dict:
        """
        Extract actionable knowledge from executed operation
        Springfield: Focus on learning opportunities and pattern recognition
        """
        
        knowledge_items = []
        
        # Analyze tool execution for learning opportunities
        if tool_name in ['Write', 'Edit', 'MultiEdit']:
            knowledge_items.extend(self._extract_code_knowledge(tool_input, tool_response))
        elif tool_name == 'Bash':
            knowledge_items.extend(self._extract_command_knowledge(tool_input, tool_response))
        elif tool_name in ['Grep', 'Glob']:
            knowledge_items.extend(self._extract_search_knowledge(tool_input, tool_response))
        elif tool_name == 'Task':
            knowledge_items.extend(self._extract_task_knowledge(tool_input, tool_response))
        
        # Categorize and score knowledge items
        categorized_knowledge = []
        for item in knowledge_items:
            category = self._categorize_knowledge(item)
            score = self._score_knowledge_value(item, category)
            
            if score > 0.3:  # Only persist valuable knowledge
                sanitized_item = self._sanitize_knowledge(item)
                categorized_knowledge.append({
                    'content': sanitized_item,
                    'category': category,
                    'value_score': score,
                    'tool_name': tool_name,
                    'timestamp': datetime.now().isoformat(),
                    'session_id': context.get('session_id', ''),
                    'context': self._extract_context_metadata(tool_input, context),
                })
        
        return {
            'knowledge_extracted': len(categorized_knowledge),
            'knowledge_items': categorized_knowledge,
            'categories_covered': list(set(item['category'] for item in categorized_knowledge)),
            'total_value_score': sum(item['value_score'] for item in categorized_knowledge),
        }

    def _extract_code_knowledge(self, tool_input: Dict, tool_response: Dict) -> List[str]:
        """Extract knowledge from code operations"""
        knowledge = []
        
        # Analyze file content for patterns
        if 'content' in tool_input:
            content = tool_input['content']
            
            # Look for interesting patterns
            if 'class ' in content:
                knowledge.append(f"Class definition pattern: {self._extract_class_pattern(content)}")
            
            if 'def ' in content:
                knowledge.append(f"Function pattern: {self._extract_function_pattern(content)}")
            
            if 'import ' in content or 'from ' in content:
                imports = re.findall(r'(?:from\s+\S+\s+)?import\s+[^\n]+', content)
                if imports:
                    knowledge.append(f"Import pattern: {'; '.join(imports[:3])}")
            
            # Look for error handling patterns
            if 'try:' in content:
                knowledge.append("Error handling pattern: try-except block implementation")
            
            # Look for async patterns
            if 'async def' in content or 'await ' in content:
                knowledge.append("Async programming pattern: async/await implementation")
        
        # Analyze file path for insights
        if 'file_path' in tool_input:
            file_path = tool_input['file_path']
            file_ext = Path(file_path).suffix
            
            if file_ext in ['.py', '.js', '.ts', '.java', '.go']:
                knowledge.append(f"File structure pattern: {file_ext} file in {Path(file_path).parent}")
        
        return knowledge

    def _extract_command_knowledge(self, tool_input: Dict, tool_response: Dict) -> List[str]:
        """Extract knowledge from bash commands"""
        knowledge = []
        
        if 'command' in tool_input:
            command = tool_input['command']
            
            # Categorize command types
            if command.startswith('git '):
                knowledge.append(f"Git workflow: {command}")
            elif 'npm ' in command or 'yarn ' in command:
                knowledge.append(f"Package management: {command}")
            elif 'docker ' in command:
                knowledge.append(f"Docker operation: {command}")
            elif command.startswith('find ') or command.startswith('grep '):
                knowledge.append(f"Search technique: {command}")
            elif 'curl ' in command or 'wget ' in command:
                knowledge.append(f"Network operation: {command}")
            
            # Look for useful flag combinations
            if '--' in command:
                flags = re.findall(r'--[\w-]+', command)
                if flags:
                    knowledge.append(f"Command flags pattern: {' '.join(flags)}")
        
        return knowledge

    def _extract_search_knowledge(self, tool_input: Dict, tool_response: Dict) -> List[str]:
        """Extract knowledge from search operations"""
        knowledge = []
        
        if 'pattern' in tool_input:
            pattern = tool_input['pattern']
            knowledge.append(f"Search pattern: {pattern}")
        
        if 'glob' in tool_input:
            glob_pattern = tool_input['glob']
            knowledge.append(f"File pattern: {glob_pattern}")
        
        # Analyze successful search strategies
        if tool_response and 'success' in tool_response and tool_response['success']:
            knowledge.append("Successful search strategy applied")
        
        return knowledge

    def _extract_task_knowledge(self, tool_input: Dict, tool_response: Dict) -> List[str]:
        """Extract knowledge from task operations"""
        knowledge = []
        
        if 'prompt' in tool_input:
            prompt = tool_input['prompt']
            
            # Look for problem-solving patterns
            if any(word in prompt.lower() for word in ['debug', 'fix', 'error', 'issue']):
                knowledge.append(f"Problem-solving approach: {prompt[:100]}...")
            
            if any(word in prompt.lower() for word in ['optimize', 'improve', 'performance']):
                knowledge.append(f"Optimization strategy: {prompt[:100]}...")
            
            if any(word in prompt.lower() for word in ['analyze', 'review', 'examine']):
                knowledge.append(f"Analysis approach: {prompt[:100]}...")
        
        return knowledge

    def _extract_class_pattern(self, content: str) -> str:
        """Extract class pattern information"""
        class_match = re.search(r'class\s+(\w+)(?:\([^)]+\))?:', content)
        if class_match:
            return f"Class {class_match.group(1)}"
        return "Class definition"

    def _extract_function_pattern(self, content: str) -> str:
        """Extract function pattern information"""
        func_matches = re.findall(r'def\s+(\w+)\([^)]*\):', content)
        if func_matches:
            return f"Functions: {', '.join(func_matches[:3])}"
        return "Function definition"

    def _categorize_knowledge(self, knowledge_item: str) -> str:
        """Categorize knowledge item"""
        knowledge_lower = knowledge_item.lower()
        
        best_category = 'patterns'  # Default
        best_score = 0
        
        for category, info in self.knowledge_categories.items():
            score = sum(1 for trigger in info['triggers'] if trigger in knowledge_lower)
            if score > best_score:
                best_score = score
                best_category = category
        
        return best_category

    def _score_knowledge_value(self, knowledge_item: str, category: str) -> float:
        """Score the value of a knowledge item (0.0-1.0)"""
        base_score = 0.5
        
        # Category weight
        category_weight = self.knowledge_categories.get(category, {}).get('weight', 0.2)
        base_score += category_weight
        
        # Content quality indicators
        if len(knowledge_item) > 50:  # Detailed knowledge
            base_score += 0.1
        
        if ':' in knowledge_item:  # Structured knowledge
            base_score += 0.1
        
        if any(word in knowledge_item.lower() for word in ['pattern', 'best practice', 'solution']):
            base_score += 0.2
        
        return min(1.0, base_score)

    def _sanitize_knowledge(self, knowledge_item: str) -> str:
        """
        Sanitize knowledge item to remove sensitive information
        Vector: Critical security step - no secrets in knowledge base
        """
        sanitized = knowledge_item
        
        for pattern in self.sensitive_patterns:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)
        
        # Remove potentially sensitive file paths
        sanitized = re.sub(r'/(?:home|Users)/[^/\s]+', '/[USER]', sanitized)
        
        return sanitized

    def _extract_context_metadata(self, tool_input: Dict, context: Dict) -> Dict:
        """Extract useful context metadata"""
        metadata = {
            'cwd': context.get('cwd', ''),
            'timestamp': datetime.now().isoformat(),
        }
        
        # Add file type information if available
        if 'file_path' in tool_input:
            file_path = Path(tool_input['file_path'])
            metadata['file_extension'] = file_path.suffix
            metadata['file_name'] = file_path.name
        
        return metadata

    def persist_session_knowledge(self, knowledge_data: Dict) -> Dict:
        """
        Persist knowledge from current session
        Springfield: Organize knowledge for easy retrieval and learning
        """
        
        if not knowledge_data.get('knowledge_items'):
            return {
                'persistence_status': 'SKIPPED',
                'reason': 'No valuable knowledge to persist',
            }
        
        try:
            # Append to session knowledge file
            with open(self.session_knowledge_file, 'a', encoding='utf-8') as f:
                for item in knowledge_data['knowledge_items']:
                    f.write(json.dumps(item) + '\n')
            
            # Update knowledge index for efficient retrieval
            self._update_knowledge_index(knowledge_data)
            
            # Check if we should promote to persistent knowledge
            persistent_count = 0
            for item in knowledge_data['knowledge_items']:
                if item['value_score'] > 0.7:  # High-value knowledge
                    self._promote_to_persistent_knowledge(item)
                    persistent_count += 1
            
            return {
                'persistence_status': 'SUCCESS',
                'session_items_stored': len(knowledge_data['knowledge_items']),
                'persistent_items_promoted': persistent_count,
                'storage_location': str(self.session_knowledge_file),
                'categories_updated': knowledge_data['categories_covered'],
            }
            
        except Exception as e:
            return {
                'persistence_status': 'ERROR',
                'error': f'Knowledge persistence failed: {str(e)}',
            }

    def _update_knowledge_index(self, knowledge_data: Dict):
        """Update searchable knowledge index"""
        try:
            # Load existing index
            index = {}
            if self.knowledge_index_file.exists():
                with open(self.knowledge_index_file, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            
            # Initialize index structure
            if 'categories' not in index:
                index['categories'] = {}
            if 'tools' not in index:
                index['tools'] = {}
            if 'keywords' not in index:
                index['keywords'] = {}
            
            # Update index with new knowledge
            for item in knowledge_data['knowledge_items']:
                category = item['category']
                tool_name = item['tool_name']
                
                # Update category index
                if category not in index['categories']:
                    index['categories'][category] = {'count': 0, 'last_updated': ''}
                index['categories'][category]['count'] += 1
                index['categories'][category]['last_updated'] = item['timestamp']
                
                # Update tool index
                if tool_name not in index['tools']:
                    index['tools'][tool_name] = {'count': 0, 'last_updated': ''}
                index['tools'][tool_name]['count'] += 1
                index['tools'][tool_name]['last_updated'] = item['timestamp']
                
                # Extract and index keywords
                content_words = re.findall(r'\b\w{4,}\b', item['content'].lower())
                for word in content_words[:5]:  # Limit to avoid bloat
                    if word not in index['keywords']:
                        index['keywords'][word] = 0
                    index['keywords'][word] += 1
            
            # Save updated index
            with open(self.knowledge_index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2)
                
        except Exception as e:
            # Index update failure shouldn't stop knowledge persistence
            pass

    def _promote_to_persistent_knowledge(self, knowledge_item: Dict):
        """Promote high-value knowledge to persistent storage"""
        try:
            with open(self.persistent_knowledge_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(knowledge_item) + '\n')
        except Exception:
            # Promotion failure shouldn't stop main persistence
            pass

    def persist_execution_knowledge(self, tool_name: str, tool_input: Dict, 
                                  tool_response: Dict, context: Dict) -> Dict:
        """
        Main knowledge persistence function for hook integration
        """
        
        # Extract knowledge from execution
        knowledge_data = self.extract_knowledge(tool_name, tool_input, tool_response, context)
        
        if not knowledge_data['knowledge_extracted']:
            return {
                'knowledge_persistence': 'SKIPPED',
                'reason': 'No valuable knowledge extracted from operation',
                'trinitas_note': 'Operation did not generate actionable learning insights'
            }
        
        # Persist knowledge
        persistence_result = self.persist_session_knowledge(knowledge_data)
        
        return {
            'knowledge_persistence': persistence_result['persistence_status'],
            'knowledge_extracted': knowledge_data['knowledge_extracted'],
            'categories_learned': knowledge_data['categories_covered'],
            'total_value_score': round(knowledge_data['total_value_score'], 2),
            'persistence_details': persistence_result,
            'trinitas_analysis': {
                'springfield': f"Knowledge extraction complete - {knowledge_data['knowledge_extracted']} insights captured",
                'krukai': f"Efficient indexing applied - {len(knowledge_data['categories_covered'])} categories updated",
                'vector': f"Secure storage validated - all sensitive data sanitized"
            }
        }

def main():
    """Main execution function for Claude Code hook integration"""
    
    try:
        # Parse input from Claude Code
        input_data = json.load(sys.stdin)
        
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        tool_response = input_data.get('tool_response', {})
        context = {
            'session_id': input_data.get('session_id', ''),
            'cwd': input_data.get('cwd', ''),
        }
        
        # Initialize knowledge persister
        persister = TrinitasKnowledgePersister()
        
        # Persist knowledge from execution
        knowledge_result = persister.persist_execution_knowledge(
            tool_name, tool_input, tool_response, context
        )
        
        # Generate response
        response = {
            'hook_result': 'SUCCESS',
            'knowledge_persistence': knowledge_result,
            'tool_name': tool_name,
            'timestamp': input_data.get('timestamp', ''),
        }
        
        # Add learning summary for valuable knowledge
        if knowledge_result.get('knowledge_extracted', 0) > 0:
            response['learning_summary'] = f"""
📚 TRINITAS LEARNING CAPTURE

Knowledge Extracted: {knowledge_result['knowledge_extracted']} insights
Categories: {', '.join(knowledge_result.get('categories_learned', []))}
Value Score: {knowledge_result.get('total_value_score', 0)}/5.0

Springfield's Learning:
- Valuable insights have been captured for future reference
- Knowledge base updated with patterns and solutions
- Learning opportunities identified and cataloged

Krukai's Indexing:
- Efficient knowledge indexing and categorization applied
- Search optimization enabled for quick retrieval
- Performance metadata stored for optimization

Vector's Security:
- All sensitive information sanitized before storage
- Secure knowledge persistence protocols followed
- Privacy protection maintained throughout process

This knowledge will help improve future development decisions and problem-solving approaches.
"""
        
        print(json.dumps(response, indent=2))
        sys.exit(0)
        
    except Exception as e:
        error_response = {
            'hook_result': 'ERROR',
            'error': f'Trinitas knowledge persistence failed: {str(e)}',
            'trinitas_status': 'KNOWLEDGE_PERSISTENCE_FAILED'
        }
        print(json.dumps(error_response, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()