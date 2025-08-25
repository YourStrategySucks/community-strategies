#!/usr/bin/env python3
"""Validate strategy metadata and implementation."""

import os
import sys
import importlib.util
import inspect
from pathlib import Path
from typing import List, Dict, Any

def validate_strategy_file(strategy_path: Path) -> Dict[str, Any]:
    """Validate a single strategy file."""
    results = {
        "file": strategy_path.name,
        "valid": True,
        "errors": [],
        "warnings": [],
        "metadata": {}
    }
    
    try:
        # Add the src directory to Python path for proper imports
        src_dir = strategy_path.parent.parent.parent / "src"
        if src_dir.exists() and str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))
        
        # For relative imports to work, we need to import as part of the package
        strategy_name = strategy_path.stem
        module_name = f"yss_strategies.contributed.{strategy_name}"
        
        try:
            # Try importing as a package module first
            if module_name in sys.modules:
                # Remove from cache to force reload
                del sys.modules[module_name]
            
            # Also clear any parent modules from cache
            parent_modules = ["yss_strategies", "yss_strategies.contributed"]
            for parent in parent_modules:
                if parent in sys.modules:
                    del sys.modules[parent]
            
            module = importlib.import_module(module_name)
        except ImportError as e:
            # Fallback: Load the module directly with a different approach
            try:
                # Import the base module first to make relative imports work
                base_module = importlib.import_module("yss_strategies.base")
                
                # Now load the strategy module
                spec = importlib.util.spec_from_file_location(module_name, strategy_path)
                if spec is None or spec.loader is None:
                    results["valid"] = False
                    results["errors"].append("Could not load module specification")
                    return results
                    
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module  # Add to sys.modules before execution
                spec.loader.exec_module(module)
            except Exception as fallback_error:
                results["valid"] = False
                results["errors"].append(f"Error loading strategy: {fallback_error}")
                return results
        
        # Find strategy classes
        strategy_classes = []
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if name.endswith("Strategy") and hasattr(obj, "place_bet"):
                strategy_classes.append(obj)
        
        if not strategy_classes:
            results["valid"] = False
            results["errors"].append("No strategy class found (must end with 'Strategy' and have 'place_bet' method)")
            return results
        
        if len(strategy_classes) > 1:
            results["warnings"].append(f"Multiple strategy classes found: {[cls.__name__ for cls in strategy_classes]}")
        
        # Validate the main strategy class
        strategy_class = strategy_classes[0]
        
        # Check required methods
        required_methods = ["place_bet", "get_defaults"]
        for method in required_methods:
            if not hasattr(strategy_class, method):
                results["valid"] = False
                results["errors"].append(f"Missing required method: {method}")
        
        # Validate get_defaults method
        if hasattr(strategy_class, "get_defaults"):
            try:
                defaults = strategy_class.get_defaults()
                if not isinstance(defaults, dict):
                    results["valid"] = False
                    results["errors"].append("get_defaults() must return a dictionary")
                else:
                    # Check required metadata fields
                    required_fields = ["contributor_name", "strategy_description"]
                    for field in required_fields:
                        if field not in defaults:
                            results["valid"] = False
                            results["errors"].append(f"Missing required metadata field: {field}")
                        elif not defaults[field] or defaults[field].strip() == "":
                            results["valid"] = False
                            results["errors"].append(f"Empty required metadata field: {field}")
                    
                    # Check recommended fields
                    recommended_fields = ["bankroll", "base_bet", "target_profit"]
                    for field in recommended_fields:
                        if field not in defaults:
                            results["warnings"].append(f"Missing recommended field: {field}")
                    
                    results["metadata"] = defaults
                    
            except Exception as e:
                results["valid"] = False
                results["errors"].append(f"Error calling get_defaults(): {e}")
        
        # Check docstring
        if not strategy_class.__doc__ or len(strategy_class.__doc__.strip()) < 20:
            results["warnings"].append("Strategy class should have a comprehensive docstring")
        
        # Check place_bet method signature
        if hasattr(strategy_class, "place_bet"):
            sig = inspect.signature(strategy_class.place_bet)
            params = list(sig.parameters.keys())
            if len(params) < 2 or params[1] != "game_state":
                results["warnings"].append("place_bet method should have 'game_state' as second parameter")
        
    except Exception as e:
        results["valid"] = False
        results["errors"].append(f"Error loading strategy: {e}")
    
    return results

def validate_all_strategies(strategies_dir: Path, pr_mode: bool = False) -> bool:
    """Validate all strategies in the directory."""
    print("🔍 Validating strategy implementations...")
    
    if pr_mode:
        # In PR mode, only validate changed files
        import subprocess
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "origin/main...HEAD"],
                capture_output=True, text=True, check=True
            )
            changed_files = [f for f in result.stdout.strip().split("\n") 
                           if f.endswith(".py") and "contributed" in f]
            if not changed_files:
                print("✅ No strategy files changed in this PR")
                return True
            strategy_files = [Path(f) for f in changed_files if Path(f).exists()]
        except subprocess.CalledProcessError:
            print("⚠️ Could not determine changed files, validating all")
            pr_mode = False
    
    if not pr_mode:
        strategy_files = list(strategies_dir.glob("*.py"))
        strategy_files = [f for f in strategy_files if f.name != "__init__.py"]
    
    if not strategy_files:
        print("⚠️ No strategy files found to validate")
        return True
    
    all_valid = True
    total_strategies = len(strategy_files)
    
    for strategy_file in strategy_files:
        print(f"\n📋 Validating {strategy_file.name}...")
        results = validate_strategy_file(strategy_file)
        
        if results["valid"]:
            print(f"✅ {strategy_file.name} is valid")
            if results["metadata"]:
                contributor = results["metadata"].get("contributor_name", "Unknown")
                description = results["metadata"].get("strategy_description", "No description")
                print(f"   👤 Contributor: {contributor}")
                print(f"   📖 Description: {description[:80]}{'...' if len(description) > 80 else ''}")
        else:
            print(f"❌ {strategy_file.name} has errors:")
            for error in results["errors"]:
                print(f"   🔸 {error}")
            all_valid = False
        
        if results["warnings"]:
            print(f"⚠️ Warnings for {strategy_file.name}:")
            for warning in results["warnings"]:
                print(f"   🔸 {warning}")
    
    print(f"\n📊 Summary: {total_strategies} strategies validated")
    if all_valid:
        print("🎉 All strategies are valid!")
    else:
        print("💥 Some strategies have validation errors")
    
    return all_valid

def main():
    """Main validation entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate YSS strategy implementations")
    parser.add_argument("--strategies-dir", type=Path, 
                       default=Path("src/yss_strategies/contributed"),
                       help="Directory containing strategy files")
    parser.add_argument("--pr-mode", action="store_true",
                       help="Only validate files changed in current PR")
    
    args = parser.parse_args()
    
    if not args.strategies_dir.exists():
        print(f"❌ Strategy directory not found: {args.strategies_dir}")
        sys.exit(1)
    
    success = validate_all_strategies(args.strategies_dir, args.pr_mode)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
