#!/usr/bin/env python3
"""Benchmark strategy performance for validation."""

import os
import sys
import importlib.util
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import subprocess

class MockGameState:
    """Mock game state for testing strategy performance."""
    
    def __init__(self):
        self.history = []
        self.last_result = None
        self.current_balance = 1000
        self.total_bet = 0
        self.spin_count = 0
    
    def add_result(self, number: int):
        """Add a spin result."""
        self.history.append(number)
        self.last_result = number
        self.spin_count += 1

def run_strategy_benchmark(strategy_path: Path, num_spins: int = 1000, timeout: int = 30) -> Dict[str, Any]:
    """Benchmark a single strategy with timeout protection."""
    results = {
        "file": strategy_path.name,
        "success": False,
        "error": None,
        "metrics": {},
        "execution_time": 0
    }
    
    start_time = time.time()
    
    try:
        # Load the strategy module
        spec = importlib.util.spec_from_file_location("strategy_module", strategy_path)
        if spec is None or spec.loader is None:
            results["error"] = "Could not load module"
            return results
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find strategy class
        strategy_class = None
        for name, obj in vars(module).items():
            if name.endswith("Strategy") and hasattr(obj, "place_bet"):
                strategy_class = obj
                break
        
        if strategy_class is None:
            results["error"] = "No strategy class found"
            return results
        
        # Initialize strategy
        strategy = strategy_class()
        game_state = MockGameState()
        
        # Get default parameters
        defaults = strategy.get_defaults() if hasattr(strategy, "get_defaults") else {}
        bankroll = defaults.get("bankroll", 1000)
        game_state.current_balance = bankroll
        
        # Performance tracking
        total_bet_amount = 0
        max_bet = 0
        min_bet = float('inf')
        bet_count = 0
        errors = 0
        
        # Run simulation
        import random
        random.seed(42)  # Reproducible results
        
        for spin in range(num_spins):
            # Check timeout
            if time.time() - start_time > timeout:
                results["error"] = f"Timeout after {timeout}s"
                break
            
            try:
                # Get bet from strategy
                bet_info = strategy.place_bet(game_state)
                
                if bet_info is None:
                    continue
                
                # Process bet
                if isinstance(bet_info, dict):
                    bet_amount = sum(bet_info.values()) if bet_info else 0
                elif isinstance(bet_info, (int, float)):
                    bet_amount = bet_info
                else:
                    bet_amount = 0
                
                if bet_amount > 0:
                    total_bet_amount += bet_amount
                    max_bet = max(max_bet, bet_amount)
                    min_bet = min(min_bet, bet_amount)
                    bet_count += 1
                
                # Simulate spin result
                result = random.randint(0, 36)
                game_state.add_result(result)
                
            except Exception as e:
                errors += 1
                if errors > 10:  # Too many errors
                    results["error"] = f"Too many errors during simulation: {e}"
                    break
        
        execution_time = time.time() - start_time
        
        # Calculate metrics
        if bet_count > 0:
            avg_bet = total_bet_amount / bet_count
            bet_variance = max_bet - min_bet if min_bet != float('inf') else 0
        else:
            avg_bet = 0
            bet_variance = 0
            min_bet = 0
        
        results.update({
            "success": True,
            "execution_time": execution_time,
            "metrics": {
                "spins_completed": game_state.spin_count,
                "total_bets_placed": bet_count,
                "total_bet_amount": total_bet_amount,
                "average_bet": avg_bet,
                "max_bet": max_bet,
                "min_bet": min_bet if min_bet != float('inf') else 0,
                "bet_variance": bet_variance,
                "errors_encountered": errors,
                "execution_time_ms": execution_time * 1000,
                "bets_per_second": bet_count / execution_time if execution_time > 0 else 0
            }
        })
        
    except Exception as e:
        results["error"] = str(e)
        results["execution_time"] = time.time() - start_time
    
    return results

def benchmark_all_strategies(strategies_dir: Path, num_spins: int = 1000, 
                           timeout: int = 30, max_workers: int = 4) -> bool:
    """Benchmark all strategies with performance validation."""
    print(f"🚀 Benchmarking strategies ({num_spins} spins per strategy)...")
    
    # Find strategy files
    strategy_files = list(strategies_dir.glob("*.py"))
    strategy_files = [f for f in strategy_files if f.name != "__init__.py"]
    
    if not strategy_files:
        print("⚠️ No strategy files found to benchmark")
        return True
    
    print(f"📊 Found {len(strategy_files)} strategies to benchmark")
    
    # Run benchmarks
    all_results = []
    failed_strategies = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(run_strategy_benchmark, strategy_file, num_spins, timeout): strategy_file
            for strategy_file in strategy_files
        }
        
        for future in futures:
            strategy_file = futures[future]
            try:
                result = future.result(timeout=timeout + 5)  # Extra buffer
                all_results.append(result)
                
                if result["success"]:
                    metrics = result["metrics"]
                    print(f"✅ {result['file']}: "
                          f"{metrics['spins_completed']} spins, "
                          f"{metrics['total_bets_placed']} bets, "
                          f"{metrics['execution_time_ms']:.1f}ms")
                else:
                    print(f"❌ {result['file']}: {result['error']}")
                    failed_strategies.append(result['file'])
                    
            except TimeoutError:
                print(f"⏰ {strategy_file.name}: Benchmark timeout")
                failed_strategies.append(strategy_file.name)
            except Exception as e:
                print(f"💥 {strategy_file.name}: Benchmark error - {e}")
                failed_strategies.append(strategy_file.name)
    
    # Performance analysis
    successful_results = [r for r in all_results if r["success"]]
    
    if successful_results:
        print(f"\n📈 Performance Summary ({len(successful_results)} successful):")
        
        # Calculate statistics
        execution_times = [r["execution_time"] for r in successful_results]
        avg_time = sum(execution_times) / len(execution_times)
        max_time = max(execution_times)
        
        bets_per_second = [r["metrics"]["bets_per_second"] for r in successful_results]
        avg_bps = sum(bets_per_second) / len(bets_per_second)
        
        print(f"   ⏱️  Average execution time: {avg_time:.2f}s")
        print(f"   🐌 Slowest strategy: {max_time:.2f}s")
        print(f"   🏃 Average bets/second: {avg_bps:.1f}")
        
        # Flag performance issues
        performance_issues = []
        for result in successful_results:
            if result["execution_time"] > 10:  # More than 10s for 1000 spins
                performance_issues.append(f"{result['file']} (slow: {result['execution_time']:.1f}s)")
            elif result["metrics"]["errors_encountered"] > 5:
                performance_issues.append(f"{result['file']} (errors: {result['metrics']['errors_encountered']})")
        
        if performance_issues:
            print(f"⚠️ Performance concerns:")
            for issue in performance_issues:
                print(f"   🔸 {issue}")
    
    # Save detailed results
    results_file = strategies_dir.parent / "benchmark_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "summary": {
                "total_strategies": len(strategy_files),
                "successful": len(successful_results),
                "failed": len(failed_strategies),
                "failed_strategies": failed_strategies
            },
            "results": all_results
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    # Determine success
    success_rate = len(successful_results) / len(strategy_files) if strategy_files else 1
    if success_rate < 0.8:  # Less than 80% success rate
        print(f"💥 Low success rate: {success_rate:.1%}")
        return False
    elif failed_strategies:
        print(f"⚠️ Some strategies failed: {failed_strategies}")
        return len(failed_strategies) <= 2  # Allow up to 2 failures
    else:
        print("🎉 All strategies benchmarked successfully!")
        return True

def main():
    """Main benchmarking entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark YSS strategy performance")
    parser.add_argument("--strategies-dir", type=Path,
                       default=Path("src/yss_strategies/contributed"),
                       help="Directory containing strategy files")
    parser.add_argument("--spins", type=int, default=1000,
                       help="Number of spins to simulate per strategy")
    parser.add_argument("--timeout", type=int, default=30,
                       help="Timeout per strategy in seconds")
    parser.add_argument("--workers", type=int, default=4,
                       help="Number of parallel workers")
    
    args = parser.parse_args()
    
    if not args.strategies_dir.exists():
        print(f"❌ Strategy directory not found: {args.strategies_dir}")
        sys.exit(1)
    
    success = benchmark_all_strategies(
        args.strategies_dir, 
        args.spins, 
        args.timeout, 
        args.workers
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
