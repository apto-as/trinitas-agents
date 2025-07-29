#!/usr/bin/env python3
"""
Project Trinitas v2.0 - Code Quality Validation Hook
Post-execution quality analysis and improvement recommendations

Integrated by: Trinitas Meta-Intelligence System
- Springfield: User-friendly quality reports and improvement guidance
- Krukai: Efficient quality metrics calculation and optimization recommendations
- Vector: Comprehensive quality issue detection and risk assessment
"""

import sys
import json
import os
import re
import subprocess
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class TrinitasQualityValidator:
    """Trinitas-powered code quality validation system"""
    
    def __init__(self):
        # Vector: Strict quality thresholds for protection
        self.quality_thresholds = {
            'complexity_critical': 15,      # Cyclomatic complexity
            'complexity_warning': 10,       # Complexity warning level
            'line_length_max': 120,         # Maximum line length
            'function_length_max': 50,      # Maximum function length
            'class_length_max': 300,        # Maximum class length
            'comment_ratio_min': 0.15,      # Minimum comment-to-code ratio
            'duplication_threshold': 6,     # Lines for duplication detection
        }
        
        # Krukai: Performance-oriented quality metrics
        self.code_smells = {
            'long_function': r'def\s+\w+\([^)]*\):(?:[^def])*(?:\n.*){50,}',
            'deep_nesting': r'(?:\s{4}){5,}',  # 5+ levels of indentation
            'magic_numbers': r'\b(?<![\w.])[0-9]{2,}\b(?![\w.])',
            'hardcoded_strings': r'["\'][^"\']{20,}["\']',
            'empty_catch': r'except[^:]*:\s*pass',
            'too_many_params': r'def\s+\w+\([^)]*,[^)]*,[^)]*,[^)]*,[^)]*,',
        }
        
        # Springfield: User-friendly quality categories
        self.quality_categories = {
            'maintainability': ['complexity', 'readability', 'documentation'],
            'reliability': ['error_handling', 'testing', 'validation'],
            'performance': ['efficiency', 'optimization', 'resource_usage'],
            'security': ['input_validation', 'secrets', 'permissions'],
        }

    def analyze_file_quality(self, file_path: str) -> Dict:
        """
        Comprehensive file quality analysis
        Krukai: Efficient and thorough quality measurement
        """
        if not os.path.exists(file_path):
            return {'error': f'File not found: {file_path}'}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Basic metrics
            total_lines = len(lines)
            code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            comment_lines = len([line for line in lines if line.strip().startswith('#')])
            blank_lines = total_lines - code_lines - comment_lines
            
            # Quality analysis
            issues = []
            
            # Line length analysis
            long_lines = [(i+1, line) for i, line in enumerate(lines) 
                         if len(line) > self.quality_thresholds['line_length_max']]
            
            # Function/class length analysis
            function_lengths = self._analyze_function_lengths(content)
            class_lengths = self._analyze_class_lengths(content)
            
            # Code smell detection
            detected_smells = {}
            for smell_name, pattern in self.code_smells.items():
                matches = re.findall(pattern, content, re.MULTILINE)
                if matches:
                    detected_smells[smell_name] = len(matches)
            
            # Comment ratio
            comment_ratio = comment_lines / max(code_lines, 1)
            
            # Complexity estimation (simplified)
            complexity_score = self._estimate_complexity(content)
            
            return {
                'file_path': file_path,
                'metrics': {
                    'total_lines': total_lines,
                    'code_lines': code_lines,
                    'comment_lines': comment_lines,
                    'blank_lines': blank_lines,
                    'comment_ratio': comment_ratio,
                    'complexity_score': complexity_score,
                },
                'issues': {
                    'long_lines': len(long_lines),
                    'long_functions': len([f for f, l in function_lengths if l > self.quality_thresholds['function_length_max']]),
                    'long_classes': len([c for c, l in class_lengths if l > self.quality_thresholds['class_length_max']]),
                    'code_smells': detected_smells,
                },
                'quality_score': self._calculate_quality_score(
                    total_lines, code_lines, comment_ratio, complexity_score, 
                    len(long_lines), detected_smells
                ),
                'recommendations': self._generate_recommendations(
                    comment_ratio, complexity_score, detected_smells, long_lines
                )
            }
            
        except Exception as e:
            return {'error': f'Quality analysis failed: {str(e)}'}

    def _analyze_function_lengths(self, content: str) -> List[Tuple[str, int]]:
        """Analyze function lengths"""
        functions = []
        lines = content.split('\n')
        
        current_function = None
        function_start = 0
        indent_level = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('def '):
                if current_function:
                    functions.append((current_function, i - function_start))
                current_function = stripped.split('(')[0].replace('def ', '')
                function_start = i
                indent_level = len(line) - len(line.lstrip())
            elif current_function and stripped and len(line) - len(line.lstrip()) <= indent_level and not line.startswith(' '):
                functions.append((current_function, i - function_start))
                current_function = None
        
        if current_function:
            functions.append((current_function, len(lines) - function_start))
        
        return functions

    def _analyze_class_lengths(self, content: str) -> List[Tuple[str, int]]:
        """Analyze class lengths"""
        classes = []
        lines = content.split('\n')
        
        current_class = None
        class_start = 0
        indent_level = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('class '):
                if current_class:
                    classes.append((current_class, i - class_start))
                current_class = stripped.split('(')[0].replace('class ', '').rstrip(':')
                class_start = i
                indent_level = len(line) - len(line.lstrip())
            elif current_class and stripped and len(line) - len(line.lstrip()) <= indent_level and not line.startswith(' '):
                classes.append((current_class, i - class_start))
                current_class = None
        
        if current_class:
            classes.append((current_class, len(lines) - class_start))
        
        return classes

    def _estimate_complexity(self, content: str) -> int:
        """Simplified cyclomatic complexity estimation"""
        complexity_keywords = [
            'if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except:', 
            'finally:', 'with ', 'and ', 'or ', '?', 'case '
        ]
        
        complexity = 1  # Base complexity
        for keyword in complexity_keywords:
            complexity += content.lower().count(keyword)
        
        return complexity

    def _calculate_quality_score(self, total_lines: int, code_lines: int, 
                                comment_ratio: float, complexity: int, 
                                long_lines: int, smells: Dict) -> int:
        """Calculate overall quality score (0-100)"""
        score = 100
        
        # Comment ratio penalty
        if comment_ratio < self.quality_thresholds['comment_ratio_min']:
            score -= 20 * (self.quality_thresholds['comment_ratio_min'] - comment_ratio) / self.quality_thresholds['comment_ratio_min']
        
        # Complexity penalty
        if complexity > self.quality_thresholds['complexity_warning']:
            score -= min(30, (complexity - self.quality_thresholds['complexity_warning']) * 2)
        
        # Long lines penalty
        if long_lines > 0:
            score -= min(15, long_lines * 2)
        
        # Code smells penalty
        smell_penalty = sum(min(10, count * 2) for count in smells.values())
        score -= min(25, smell_penalty)
        
        return max(0, int(score))

    def _generate_recommendations(self, comment_ratio: float, complexity: int, 
                                smells: Dict, long_lines: List) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Springfield: User-friendly recommendations
        if comment_ratio < self.quality_thresholds['comment_ratio_min']:
            recommendations.append(f"Add more comments - current ratio {comment_ratio:.2f}, target {self.quality_thresholds['comment_ratio_min']:.2f}")
        
        if complexity > self.quality_thresholds['complexity_critical']:
            recommendations.append(f"CRITICAL: Reduce complexity from {complexity} to below {self.quality_thresholds['complexity_critical']}")
        elif complexity > self.quality_thresholds['complexity_warning']:
            recommendations.append(f"Consider refactoring to reduce complexity from {complexity} to below {self.quality_thresholds['complexity_warning']}")
        
        if long_lines:
            recommendations.append(f"Break {len(long_lines)} long lines (max {self.quality_thresholds['line_length_max']} chars)")
        
        for smell, count in smells.items():
            if count > 0:
                recommendations.append(f"Address {count} instances of {smell.replace('_', ' ')}")
        
        return recommendations

    def validate_execution_quality(self, tool_name: str, tool_input: Dict, 
                                 tool_response: Dict, context: Dict) -> Dict:
        """
        Validate quality of executed operation
        Returns quality assessment and recommendations
        """
        
        file_paths = []
        
        # Extract file paths from different tool types
        if tool_name in ['Write', 'Edit', 'MultiEdit']:
            if 'file_path' in tool_input:
                file_paths.append(tool_input['file_path'])
            elif 'edits' in tool_input:  # MultiEdit
                for edit in tool_input['edits']:
                    if 'file_path' in edit:
                        file_paths.append(edit['file_path'])
        
        if not file_paths:
            return {
                'quality_check': 'SKIPPED',
                'reason': 'No files to analyze',
                'trinitas_note': 'Operation did not involve file modifications'
            }
        
        # Analyze each file
        file_analyses = []
        overall_quality = 100
        critical_issues = []
        
        for file_path in file_paths:
            analysis = self.analyze_file_quality(file_path)
            if 'error' not in analysis:
                file_analyses.append(analysis)
                overall_quality = min(overall_quality, analysis['quality_score'])
                
                # Check for critical issues
                if analysis['quality_score'] < 50:
                    critical_issues.append(f"{file_path}: Quality score {analysis['quality_score']}/100")
                
                if analysis['metrics']['complexity_score'] > self.quality_thresholds['complexity_critical']:
                    critical_issues.append(f"{file_path}: Critical complexity level {analysis['metrics']['complexity_score']}")
        
        # Determine overall assessment
        if overall_quality >= 80:
            quality_level = 'EXCELLENT'
            decision = 'PASS'
        elif overall_quality >= 60:
            quality_level = 'GOOD'
            decision = 'PASS'
        elif overall_quality >= 40:
            quality_level = 'ACCEPTABLE'
            decision = 'WARN'
        else:
            quality_level = 'POOR'
            decision = 'WARN'
        
        return {
            'quality_check': quality_level,
            'overall_score': overall_quality,
            'decision': decision,
            'critical_issues': critical_issues,
            'file_analyses': file_analyses,
            'trinitas_analysis': {
                'springfield': f"Quality assessment complete - {len(file_analyses)} files analyzed",
                'krukai': f"Code quality metrics calculated - overall score {overall_quality}/100",
                'vector': f"Quality validation: {len(critical_issues)} critical issues detected"
            },
            'recommendations': self._generate_overall_recommendations(file_analyses)
        }

    def _generate_overall_recommendations(self, analyses: List[Dict]) -> List[str]:
        """Generate overall recommendations across all files"""
        all_recommendations = []
        
        for analysis in analyses:
            if 'recommendations' in analysis:
                file_path = analysis.get('file_path', 'unknown')
                for rec in analysis['recommendations']:
                    all_recommendations.append(f"{Path(file_path).name}: {rec}")
        
        # Deduplicate and prioritize
        unique_recommendations = list(set(all_recommendations))
        
        # Add general recommendations if needed
        if len(analyses) > 1:
            avg_score = sum(a.get('quality_score', 0) for a in analyses) / len(analyses)
            if avg_score < 70:
                unique_recommendations.insert(0, "Consider implementing code quality standards and review processes")
        
        return unique_recommendations[:10]  # Limit to top 10

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
        
        # Initialize validator
        validator = TrinitasQualityValidator()
        
        # Validate quality
        quality_result = validator.validate_execution_quality(
            tool_name, tool_input, tool_response, context
        )
        
        # Generate response
        response = {
            'hook_result': 'SUCCESS',
            'quality_validation': quality_result,
            'tool_name': tool_name,
            'timestamp': input_data.get('timestamp', ''),
        }
        
        # Add detailed quality report for poor quality code
        if quality_result.get('overall_score', 100) < 60:
            response['quality_guidance'] = f"""
📊 TRINITAS QUALITY ASSESSMENT

Overall Quality Score: {quality_result.get('overall_score', 0)}/100

Springfield's Guidance:
- Quality improvement will enhance long-term maintainability
- Consider dedicating time to refactoring and documentation
- Small, consistent improvements lead to significant gains

Krukai's Analysis:
- Code quality directly impacts performance and maintainability
- Implement automated quality checks in your development workflow
- Focus on reducing complexity and improving test coverage

Vector's Warning:
- Poor code quality increases security vulnerability risk
- Technical debt accumulates and becomes harder to address over time
- Quality issues may indicate deeper architectural problems

Priority Actions:
{chr(10).join('- ' + rec for rec in quality_result.get('recommendations', [])[:5])}
"""
        
        print(json.dumps(response, indent=2))
        sys.exit(0)
        
    except Exception as e:
        error_response = {
            'hook_result': 'ERROR',
            'error': f'Trinitas quality validation failed: {str(e)}',
            'trinitas_status': 'QUALITY_CHECK_FAILED'
        }
        print(json.dumps(error_response, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()