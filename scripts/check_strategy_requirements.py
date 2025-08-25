#!/usr/bin/env python3
"""Check strategy requirements and dependencies."""

import os
import sys
import ast
import re
from pathlib import Path
from typing import List, Dict, Set, Any

class StrategyDependencyChecker:
    """Analyze strategy files for dependencies and requirements."""
    
    def __init__(self):
        # Allowed standard library modules
        self.allowed_stdlib = {
            'math', 'random', 'itertools', 'collections', 'functools',
            'operator', 'json', 'time', 'datetime', 'decimal', 'fractions',
            'statistics', 'copy', 'typing', 'dataclasses', 'enum', 'abc'
        }
        
        # Allowed third-party packages
        self.allowed_packages = {
            'numpy', 'scipy', 'pandas', 'matplotlib', 'seaborn'
        }
        
        # Forbidden modules/patterns
        self.forbidden = {
            'os', 'sys', 'subprocess', 'threading', 'multiprocessing',
            'socket', 'urllib', 'requests', 'http', 'ftplib', 'smtplib',
            'sqlite3', 'mysql', 'psycopg2', 'pymongo', 'redis',
            'pickle', 'shelve', 'dbm', 'marshal', 'eval', 'exec',
            'open', 'file', '__import__', 'importlib'
        }

def analyze_imports(file_path: Path) -> Dict[str, Any]:
    """Analyze imports in a Python file."""
    results = {
        "file": file_path.name,
        "imports": [],
        "forbidden_imports": [],
        "unknown_imports": [],
        "valid": True,
        "errors": []
    }
    
    checker = StrategyDependencyChecker()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            results["valid"] = False
            results["errors"].append(f"Syntax error: {e}")
            return results
        
        # Find all imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    results["imports"].append(alias.name)
                    
                    # Check if forbidden
                    if module_name in checker.forbidden:
                        results["forbidden_imports"].append(alias.name)
                        results["valid"] = False
                    # Check if allowed
                    elif module_name not in checker.allowed_stdlib and module_name not in checker.allowed_packages:
                        results["unknown_imports"].append(alias.name)
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split('.')[0]
                    results["imports"].append(node.module)
                    
                    # Check if forbidden
                    if module_name in checker.forbidden:
                        results["forbidden_imports"].append(node.module)
                        results["valid"] = False
                    # Check if allowed
                    elif module_name not in checker.allowed_stdlib and module_name not in checker.allowed_packages:
                        results["unknown_imports"].append(node.module)
        
        # Check for dangerous function calls
        dangerous_calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', 'open', '__import__']:
                        dangerous_calls.append(node.func.id)
                        results["valid"] = False
        
        if dangerous_calls:
            results["forbidden_imports"].extend(dangerous_calls)
            results["errors"].append(f"Dangerous function calls: {dangerous_calls}")
        
        # Check for file operations in string content
        file_patterns = [
            r'open\s*\(',
            r'with\s+open\s*\(',
            r'file\s*\(',
            r'\.read\s*\(',
            r'\.write\s*\(',
            r'\.save\s*\(',
            r'\.load\s*\('
        ]
        
        for pattern in file_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                results["errors"].append(f"Potential file operation detected: {pattern}")
                results["valid"] = False
        
    except Exception as e:
        results["valid"] = False
        results["errors"].append(f"Analysis error: {e}")
    
    return results

def check_strategy_requirements(strategy_path: Path) -> Dict[str, Any]:
    """Check if strategy meets all requirements."""
    results = {
        "file": strategy_path.name,
        "valid": True,
        "errors": [],
        "warnings": [],
        "size_check": {},
        "complexity_check": {},
        "import_check": {}
    }
    
    try:
        # File size check
        file_size = strategy_path.stat().st_size
        results["size_check"] = {
            "size_bytes": file_size,
            "size_kb": round(file_size / 1024, 2),
            "too_large": file_size > 100 * 1024  # 100KB limit
        }
        
        if results["size_check"]["too_large"]:
            results["valid"] = False
            results["errors"].append(f"File too large: {results['size_check']['size_kb']}KB (max 100KB)")
        
        # Read content
        with open(strategy_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Line count check
        lines = content.split('\n')
        line_count = len(lines)
        non_empty_lines = len([line for line in lines if line.strip()])
        
        results["complexity_check"] = {
            "total_lines": line_count,
            "non_empty_lines": non_empty_lines,
            "too_many_lines": line_count > 1000
        }
        
        if results["complexity_check"]["too_many_lines"]:
            results["warnings"].append(f"File is quite large: {line_count} lines")
        
        # Import analysis
        import_results = analyze_imports(strategy_path)
        results["import_check"] = import_results
        
        if not import_results["valid"]:
            results["valid"] = False
            results["errors"].extend(import_results["errors"])
        
        if import_results["forbidden_imports"]:
            results["errors"].append(f"Forbidden imports: {import_results['forbidden_imports']}")
        
        if import_results["unknown_imports"]:
            results["warnings"].append(f"Unknown imports (may need approval): {import_results['unknown_imports']}")
        
        # Check for class definition
        if 'class ' not in content:
            results["valid"] = False
            results["errors"].append("No class definition found")
        
        # Check for required methods
        required_patterns = [
            r'def\s+place_bet\s*\(',
            r'def\s+get_defaults\s*\('
        ]
        
        for pattern in required_patterns:
            if not re.search(pattern, content):
                method_name = pattern.split('\\s+')[1]
                results["valid"] = False
                results["errors"].append(f"Missing required method: {method_name}")
        
        # Check for docstrings
        if '"""' not in content and "'''" not in content:
            results["warnings"].append("No docstrings found - consider adding documentation")
        
        # Check for hardcoded paths or URLs
        suspicious_patterns = [
            r'["\'][A-Za-z]:\\',  # Windows paths
            r'["\']/',             # Unix paths
            r'http[s]?://',        # URLs
            r'ftp://',
            r'localhost',
            r'127\.0\.0\.1'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, content):
                results["warnings"].append(f"Suspicious pattern detected: {pattern}")
        
    except Exception as e:
        results["valid"] = False
        results["errors"].append(f"Requirements check error: {e}")
    
    return results

def check_all_requirements(strategies_dir: Path) -> bool:
    """Check requirements for all strategies."""
    print("🔍 Checking strategy requirements and dependencies...")
    
    # Find strategy files
    strategy_files = list(strategies_dir.glob("*.py"))
    strategy_files = [f for f in strategy_files if f.name != "__init__.py"]
    
    if not strategy_files:
        print("⚠️ No strategy files found to check")
        return True
    
    print(f"📋 Checking {len(strategy_files)} strategy files...")
    
    all_valid = True
    issues_found = []
    
    for strategy_file in strategy_files:
        print(f"\n🔎 Checking {strategy_file.name}...")
        results = check_strategy_requirements(strategy_file)
        
        if results["valid"]:
            print(f"✅ {strategy_file.name} passes all checks")
            
            # Show size info
            size_info = results["size_check"]
            print(f"   📏 Size: {size_info['size_kb']}KB")
            
            # Show complexity info
            complexity = results["complexity_check"]
            print(f"   📊 Lines: {complexity['non_empty_lines']} non-empty")
            
            # Show imports
            imports = results["import_check"]["imports"]
            if imports:
                print(f"   📦 Imports: {', '.join(imports[:5])}")
                if len(imports) > 5:
                    print(f"        (+ {len(imports) - 5} more)")
        else:
            print(f"❌ {strategy_file.name} has requirement violations:")
            for error in results["errors"]:
                print(f"   🔸 {error}")
            all_valid = False
            issues_found.append(strategy_file.name)
        
        # Show warnings
        if results["warnings"]:
            print(f"⚠️ Warnings for {strategy_file.name}:")
            for warning in results["warnings"]:
                print(f"   🔸 {warning}")
    
    # Summary
    print(f"\n📊 Requirements Check Summary:")
    print(f"   📁 Files checked: {len(strategy_files)}")
    print(f"   ✅ Valid files: {len(strategy_files) - len(issues_found)}")
    print(f"   ❌ Files with issues: {len(issues_found)}")
    
    if issues_found:
        print(f"   🚨 Files needing attention: {', '.join(issues_found)}")
    
    if all_valid:
        print("🎉 All strategies meet requirements!")
    else:
        print("💥 Some strategies have requirement violations")
    
    return all_valid

def main():
    """Main requirements checking entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check YSS strategy requirements")
    parser.add_argument("--strategies-dir", type=Path,
                       default=Path("src/yss_strategies/contributed"),
                       help="Directory containing strategy files")
    
    args = parser.parse_args()
    
    if not args.strategies_dir.exists():
        print(f"❌ Strategy directory not found: {args.strategies_dir}")
        sys.exit(1)
    
    success = check_all_requirements(args.strategies_dir)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
