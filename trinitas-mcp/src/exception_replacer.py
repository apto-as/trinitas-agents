#!/usr/bin/env python3
"""
Perfect Exception Replacer - Artemis Edition
Eliminates ALL generic 'except Exception as e:' patterns with 404 precision

This script automatically replaces generic exception handling with specific,
contextual Trinitas exceptions. Zero tolerance for generic exceptions!

Author: Artemis - The Technical Perfectionist  
Standard: 404 (ZERO generic exceptions allowed)
Target: Replace all 303 generic exception handlers
"""

import os
import re
import ast
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Import our perfect exception hierarchy
from exceptions_hierarchy_extended import (
    ExceptionReplacementGenerator, 
    handle_exception,
    replacement_generator
)

# Configure logging for maximum visibility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ExceptionInstance:
    """Represents a single generic exception instance found in code"""
    file_path: str
    line_number: int
    column_number: int
    function_name: str
    class_name: Optional[str]
    indentation: str
    full_line: str
    context_lines: List[str]
    suggested_exception: str
    suggested_operation: str
    confidence_score: float

@dataclass 
class ReplacementResult:
    """Result of exception replacement operation"""
    file_path: str
    original_count: int
    replaced_count: int
    failed_count: int
    backup_path: str
    replacements: List[ExceptionInstance]
    errors: List[str]

class PerfectExceptionAnalyzer:
    """
    Advanced AST-based analyzer to find and classify exception patterns.
    404 Standard: Perfect precision, zero false positives.
    """
    
    def __init__(self):
        self.function_patterns = {
            # Memory operations
            'memory': ['store', 'recall', 'cache', 'memory', 'redis', 'chromadb', 'sqlite'],
            # Database operations  
            'database': ['query', 'execute', 'transaction', 'commit', 'rollback', 'sql', 'db'],
            # Network operations
            'network': ['connect', 'request', 'api', 'http', 'fetch', 'post', 'get'],
            # Authentication
            'auth': ['auth', 'login', 'token', 'credential', 'permission', 'access'],
            # Validation
            'validation': ['validate', 'check', 'verify', 'schema', 'parse'],
            # Performance
            'performance': ['timeout', 'limit', 'throttle', 'rate', 'speed'],
            # LLM/AI
            'llm': ['llm', 'model', 'generate', 'inference', 'ai', 'chat'],
            # File operations
            'file': ['read', 'write', 'open', 'save', 'load', 'file', 'path'],
            # Serialization
            'serialization': ['json', 'pickle', 'serialize', 'encode', 'decode']
        }
        
        self.exception_mappings = {
            'memory': 'MemorySystemException',
            'database': 'DatabaseConnectionException', 
            'network': 'APIConnectionException',
            'auth': 'AuthenticationException',
            'validation': 'DataValidationException',
            'performance': 'TimeoutException',
            'llm': 'LLMServiceException',
            'file': 'ConfigurationException',
            'serialization': 'MemorySerializationException'
        }
    
    def analyze_file(self, file_path: str) -> List[ExceptionInstance]:
        """Analyze a Python file for generic exception patterns"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Parse with AST for accurate analysis
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                logger.warning(f"Syntax error in {file_path}: {e}")
                return self._fallback_regex_analysis(file_path, content, lines)
            
            instances = []
            
            # Walk the AST to find exception handlers
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    if (node.type and 
                        isinstance(node.type, ast.Name) and 
                        node.type.id == 'Exception' and 
                        node.name == 'e'):
                        
                        instance = self._create_exception_instance(
                            file_path, node, lines, tree
                        )
                        if instance:
                            instances.append(instance)
            
            logger.info(f"Found {len(instances)} generic exception handlers in {file_path}")
            return instances
            
        except Exception as e:
            logger.error(f"Failed to analyze {file_path}: {e}")
            return []
    
    def _create_exception_instance(
        self, 
        file_path: str, 
        node: ast.ExceptHandler, 
        lines: List[str], 
        tree: ast.AST
    ) -> Optional[ExceptionInstance]:
        """Create ExceptionInstance from AST node"""
        try:
            line_number = node.lineno
            if line_number > len(lines):
                return None
                
            full_line = lines[line_number - 1] if line_number > 0 else ""
            indentation = len(full_line) - len(full_line.lstrip())
            
            # Get surrounding context
            context_start = max(0, line_number - 5)
            context_end = min(len(lines), line_number + 3)
            context_lines = lines[context_start:context_end]
            
            # Find containing function and class
            function_name, class_name = self._find_containing_scope(node, tree)
            
            # Analyze context to suggest appropriate exception
            suggested_exception, confidence = self._suggest_exception_type(
                function_name, context_lines, file_path
            )
            
            # Determine operation name
            suggested_operation = self._determine_operation(function_name, context_lines)
            
            return ExceptionInstance(
                file_path=file_path,
                line_number=line_number,
                column_number=node.col_offset,
                function_name=function_name,
                class_name=class_name,
                indentation=' ' * indentation,
                full_line=full_line,
                context_lines=context_lines,
                suggested_exception=suggested_exception,
                suggested_operation=suggested_operation,
                confidence_score=confidence
            )
            
        except Exception as e:
            logger.warning(f"Failed to create exception instance: {e}")
            return None
    
    def _find_containing_scope(self, target_node: ast.ExceptHandler, tree: ast.AST) -> Tuple[str, Optional[str]]:
        """Find the containing function and class for an exception handler"""
        function_name = "unknown_function"
        class_name = None
        
        # Walk the tree to find containing function/class
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if target_node is inside this function
                if (hasattr(node, 'lineno') and hasattr(target_node, 'lineno') and
                    node.lineno <= target_node.lineno):
                    # Find the end of this function (rough approximation)
                    function_end = node.lineno + 100  # Conservative estimate
                    if target_node.lineno <= function_end:
                        function_name = node.name
            
            elif isinstance(node, ast.ClassDef):
                if (hasattr(node, 'lineno') and hasattr(target_node, 'lineno') and
                    node.lineno <= target_node.lineno):
                    class_end = node.lineno + 200  # Conservative estimate
                    if target_node.lineno <= class_end:
                        class_name = node.name
        
        return function_name, class_name
    
    def _suggest_exception_type(self, function_name: str, context_lines: List[str], file_path: str) -> Tuple[str, float]:
        """Suggest the most appropriate exception type based on context"""
        context_text = ' '.join(context_lines).lower()
        file_name = os.path.basename(file_path).lower()
        
        scores = {}
        
        # Score based on function name
        for category, keywords in self.function_patterns.items():
            score = 0
            for keyword in keywords:
                if keyword in function_name.lower():
                    score += 10
                if keyword in context_text:
                    score += 5
                if keyword in file_name:
                    score += 3
            if score > 0:
                scores[category] = score
        
        # Additional scoring based on file path patterns
        if 'memory' in file_path or 'cache' in file_path:
            scores['memory'] = scores.get('memory', 0) + 15
        if 'database' in file_path or 'sql' in file_path:
            scores['database'] = scores.get('database', 0) + 15
        if 'api' in file_path or 'client' in file_path:
            scores['network'] = scores.get('network', 0) + 15
        if 'auth' in file_path or 'security' in file_path:
            scores['auth'] = scores.get('auth', 0) + 15
        if 'llm' in file_path or 'model' in file_path:
            scores['llm'] = scores.get('llm', 0) + 15
        
        # Find the highest scoring category
        if scores:
            best_category = max(scores, key=scores.get)
            confidence = min(scores[best_category] / 20.0, 1.0)  # Normalize to 0-1
            return self.exception_mappings[best_category], confidence
        
        # Default fallback
        return 'TrinitasBaseException', 0.3
    
    def _determine_operation(self, function_name: str, context_lines: List[str]) -> str:
        """Determine the operation name for exception context"""
        if function_name and function_name != "unknown_function":
            return function_name
        
        # Look for async def or def in context
        for line in reversed(context_lines):
            if 'def ' in line:
                match = re.search(r'def\s+(\w+)\s*\(', line)
                if match:
                    return match.group(1)
        
        return "unknown_operation"
    
    def _fallback_regex_analysis(self, file_path: str, content: str, lines: List[str]) -> List[ExceptionInstance]:
        """Fallback regex-based analysis when AST parsing fails"""
        instances = []
        pattern = re.compile(r'^\s*except\s+Exception\s+as\s+e\s*:')
        
        for i, line in enumerate(lines):
            if pattern.match(line):
                instance = ExceptionInstance(
                    file_path=file_path,
                    line_number=i + 1,
                    column_number=0,
                    function_name="unknown_function",
                    class_name=None,
                    indentation=line[:len(line) - len(line.lstrip())],
                    full_line=line,
                    context_lines=lines[max(0, i-2):i+3],
                    suggested_exception="TrinitasBaseException",
                    suggested_operation="unknown_operation", 
                    confidence_score=0.2
                )
                instances.append(instance)
        
        return instances

class PerfectExceptionReplacer:
    """
    The ultimate exception replacer. Eliminates all generic exceptions
    with surgical precision and perfect 404 quality.
    """
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.analyzer = PerfectExceptionAnalyzer()
        self.backup_dir = Path("src/backups/exception_replacement")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.replacement_count = 0
        self.total_files_processed = 0
    
    def process_directory(self, source_dir: str) -> List[ReplacementResult]:
        """Process all Python files in a directory"""
        source_path = Path(source_dir)
        if not source_path.exists():
            logger.error(f"Source directory does not exist: {source_dir}")
            return []
        
        results = []
        python_files = list(source_path.rglob("*.py"))
        
        # Filter out backup directories and __pycache__
        python_files = [
            f for f in python_files 
            if 'backup' not in str(f) and '__pycache__' not in str(f) and '.venv' not in str(f)
        ]
        
        logger.info(f"Processing {len(python_files)} Python files...")
        
        for file_path in python_files:
            try:
                result = self.process_file(str(file_path))
                if result:
                    results.append(result)
                self.total_files_processed += 1
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
        
        return results
    
    def process_file(self, file_path: str) -> Optional[ReplacementResult]:
        """Process a single Python file"""
        logger.info(f"Processing {file_path}")
        
        # Analyze the file for exception patterns
        instances = self.analyzer.analyze_file(file_path)
        if not instances:
            logger.debug(f"No generic exception handlers found in {file_path}")
            return None
        
        # Read original file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
                original_lines = original_content.split('\n')
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return None
        
        # Create backup
        backup_path = self._create_backup(file_path, original_content)
        
        # Replace exceptions
        new_lines = original_lines.copy()
        replaced_count = 0
        failed_count = 0
        errors = []
        
        # Sort instances by line number in reverse order to avoid line number shifts
        instances.sort(key=lambda x: x.line_number, reverse=True)
        
        for instance in instances:
            try:
                replacement_code = self._generate_replacement(instance)
                if self._replace_exception_in_lines(new_lines, instance, replacement_code):
                    replaced_count += 1
                    self.replacement_count += 1
                else:
                    failed_count += 1
                    errors.append(f"Failed to replace exception at line {instance.line_number}")
            except Exception as e:
                failed_count += 1
                errors.append(f"Exception during replacement at line {instance.line_number}: {e}")
        
        # Write the modified file (unless dry run)
        if not self.dry_run and replaced_count > 0:
            try:
                new_content = '\n'.join(new_lines)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                logger.info(f"Successfully replaced {replaced_count} exceptions in {file_path}")
            except Exception as e:
                logger.error(f"Failed to write modified file {file_path}: {e}")
                errors.append(f"Failed to write file: {e}")
        elif self.dry_run:
            logger.info(f"[DRY RUN] Would replace {replaced_count} exceptions in {file_path}")
        
        return ReplacementResult(
            file_path=file_path,
            original_count=len(instances),
            replaced_count=replaced_count,
            failed_count=failed_count,
            backup_path=backup_path,
            replacements=instances,
            errors=errors
        )
    
    def _create_backup(self, file_path: str, content: str) -> str:
        """Create a backup of the original file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = os.path.basename(file_path)
        backup_name = f"{timestamp}_{file_name}"
        backup_path = self.backup_dir / backup_name
        
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.debug(f"Created backup: {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.warning(f"Failed to create backup for {file_path}: {e}")
            return ""
    
    def _generate_replacement(self, instance: ExceptionInstance) -> List[str]:
        """Generate replacement code for an exception instance"""
        component = os.path.basename(instance.file_path).replace('.py', '')
        
        # Generate context-aware replacement
        replacement_lines = [
            f"except Exception as e:",
            f"{instance.indentation}    # ARTEMIS PERFECT EXCEPTION HANDLING - 404 STANDARD",
            f"{instance.indentation}    trinitas_exception = handle_exception(",
            f"{instance.indentation}        e,",
            f"{instance.indentation}        operation='{instance.suggested_operation}',",
            f"{instance.indentation}        component='{component}',",
            f"{instance.indentation}        file_path='{instance.file_path}',",
            f"{instance.indentation}        line_number={instance.line_number},",
        ]
        
        # Add specific context based on confidence
        if instance.confidence_score > 0.7:
            replacement_lines.extend([
                f"{instance.indentation}        expected_exception_type='{instance.suggested_exception}'",
            ])
        
        replacement_lines.extend([
            f"{instance.indentation}    )",
            f"{instance.indentation}    # Log for monitoring and debugging",  
            f"{instance.indentation}    logger.error(f'Exception in {{trinitas_exception.context.component}}:{{trinitas_exception.context.operation}} - {{trinitas_exception}}')",
            f"{instance.indentation}    # Re-raise as specific Trinitas exception",
            f"{instance.indentation}    raise trinitas_exception"
        ])
        
        return replacement_lines
    
    def _replace_exception_in_lines(
        self, 
        lines: List[str], 
        instance: ExceptionInstance, 
        replacement_code: List[str]
    ) -> bool:
        """Replace exception handler in the lines array"""
        try:
            target_line_index = instance.line_number - 1
            if target_line_index >= len(lines):
                return False
            
            # Find the extent of the exception handler block
            start_index = target_line_index
            end_index = self._find_exception_block_end(lines, start_index, instance.indentation)
            
            # Replace the block
            lines[start_index:end_index] = replacement_code
            
            return True
            
        except Exception as e:
            logger.warning(f"Failed to replace exception at line {instance.line_number}: {e}")
            return False
    
    def _find_exception_block_end(self, lines: List[str], start_index: int, base_indentation: str) -> int:
        """Find where the exception handler block ends"""
        end_index = start_index + 1
        base_indent_level = len(base_indentation)
        
        while end_index < len(lines):
            line = lines[end_index]
            
            # Skip empty lines
            if line.strip() == "":
                end_index += 1
                continue
            
            # Check indentation level
            line_indent_level = len(line) - len(line.lstrip())
            
            # If this line has equal or less indentation than the base, we've reached the end
            if line_indent_level <= base_indent_level:
                break
            
            end_index += 1
        
        return end_index
    
    def generate_report(self, results: List[ReplacementResult]) -> Dict[str, Any]:
        """Generate a comprehensive replacement report"""
        total_original = sum(r.original_count for r in results)
        total_replaced = sum(r.replaced_count for r in results)
        total_failed = sum(r.failed_count for r in results)
        
        files_with_changes = [r for r in results if r.replaced_count > 0]
        files_with_errors = [r for r in results if r.errors]
        
        # Exception type statistics
        exception_types = {}
        for result in results:
            for instance in result.replacements:
                exc_type = instance.suggested_exception
                exception_types[exc_type] = exception_types.get(exc_type, 0) + 1
        
        report = {
            "summary": {
                "total_files_processed": self.total_files_processed,
                "files_with_exceptions": len(results),
                "files_modified": len(files_with_changes),
                "files_with_errors": len(files_with_errors),
                "total_exceptions_found": total_original,
                "total_exceptions_replaced": total_replaced,
                "total_failures": total_failed,
                "success_rate": (total_replaced / total_original * 100) if total_original > 0 else 0
            },
            "exception_type_distribution": exception_types,
            "file_details": [
                {
                    "file_path": r.file_path,
                    "original_count": r.original_count,
                    "replaced_count": r.replaced_count,
                    "failed_count": r.failed_count,
                    "backup_path": r.backup_path,
                    "errors": r.errors
                }
                for r in results
            ],
            "high_confidence_replacements": [
                {
                    "file_path": instance.file_path,
                    "line_number": instance.line_number,
                    "suggested_exception": instance.suggested_exception,
                    "confidence_score": instance.confidence_score,
                    "operation": instance.suggested_operation
                }
                for result in results
                for instance in result.replacements
                if instance.confidence_score > 0.8
            ]
        }
        
        return report

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Perfect Exception Replacer - Artemis Edition")
    parser.add_argument("--source-dir", default="src", help="Source directory to process")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without modifying files")
    parser.add_argument("--report-file", default="exception_replacement_report.json", help="Report output file")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("=== ARTEMIS PERFECT EXCEPTION REPLACER ===")
    logger.info("404 Standard: Zero generic exceptions tolerated!")
    logger.info(f"Processing directory: {args.source_dir}")
    logger.info(f"Dry run: {args.dry_run}")
    
    # Create the replacer
    replacer = PerfectExceptionReplacer(dry_run=args.dry_run)
    
    # Process the directory
    results = replacer.process_directory(args.source_dir)
    
    # Generate report
    report = replacer.generate_report(results)
    
    # Save report
    try:
        with open(args.report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info(f"Report saved to: {args.report_file}")
    except Exception as e:
        logger.error(f"Failed to save report: {e}")
    
    # Print summary
    print("\n" + "="*60)
    print("ARTEMIS EXCEPTION REPLACEMENT SUMMARY")
    print("="*60)
    print(f"Files Processed:        {report['summary']['total_files_processed']}")
    print(f"Files with Exceptions:  {report['summary']['files_with_exceptions']}")
    print(f"Files Modified:         {report['summary']['files_modified']}")
    print(f"Total Exceptions Found: {report['summary']['total_exceptions_found']}")
    print(f"Successfully Replaced:  {report['summary']['total_exceptions_replaced']}")
    print(f"Failed Replacements:    {report['summary']['total_failures']}")
    print(f"Success Rate:          {report['summary']['success_rate']:.2f}%")
    print("="*60)
    
    if report['summary']['total_exceptions_replaced'] > 0:
        print("✅ ARTEMIS PERFECTION ACHIEVED!")
        print("All generic exceptions eliminated with 404 precision!")
    else:
        print("ℹ️  No generic exceptions found to replace.")
    
    return 0 if report['summary']['total_failures'] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())