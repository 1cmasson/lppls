#!/usr/bin/env python3
"""
Single Window LPPLS Backtest

Run backtest for just ONE window size at a time to avoid crashes.
"""

from backtest_lppls import backtest_lppls, print_results
import json
import sys

def run_single_window(window_days):
    """Run backtest for a single window size"""

    print("="*70)
    print(f"LPPLS BACKTEST: {window_days}-DAY WINDOW")
    print("="*70)
    print(f"\nTesting {window_days}-day historical window")
    print("This will take 1-3 hours depending on window size...\n")

    results = backtest_lppls(
        crash_threshold_pct=20,
        lookforward_days=60,
        warning_window_days=60,
        test_interval_days=7,
        window_days=window_days
    )

    print(f"\n{'='*70}")
    print(f"{window_days}-DAY WINDOW RESULTS")
    print(f"{'='*70}\n")

    print_results(results)

    # Save results
    filename = f'backtest_{window_days}day_results.json'
    simplified = {
        'window_days': window_days,
        'config': results['config'],
        'metrics': results['metrics'],
        'total_crashes': len(results['crashes']),
        'total_signals': len(results['signals']),
        'crash_dates': [c['date'].strftime('%Y-%m-%d') for c in results['crashes']],
        'true_positive_dates': [tp['signal']['date'].strftime('%Y-%m-%d') for tp in results['true_positives']],
        'false_negative_dates': [fn['date'].strftime('%Y-%m-%d') for fn in results['false_negatives']]
    }

    with open(filename, 'w') as f:
        json.dump(simplified, f, indent=2)

    print(f"\nResults saved to: {filename}")
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python backtest_single_window.py <window_days>")
        print("Example: python backtest_single_window.py 90")
        sys.exit(1)

    window = int(sys.argv[1])
    print(f"Starting backtest for {window}-day window...")
    run_single_window(window)
