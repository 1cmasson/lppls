#!/usr/bin/env python3
"""
LPPLS Multi-Window Backtest Comparison

Tests LPPLS performance with different historical data window sizes:
- 30 days: Very recent, fast-moving
- 60 days: Short-term trends
- 90 days: Quarterly view
- 180 days: Half-year (original default)
- 365 days: Full year, major cycles

This helps identify the optimal window size for different crash types.
"""

from backtest_lppls import backtest_lppls, print_results
import json

def compare_windows():
    """Run backtest with multiple window sizes and compare results"""

    print("="*70)
    print("LPPLS MULTI-WINDOW BACKTEST COMPARISON")
    print("="*70)
    print("\nTesting window sizes: 30, 60, 90, 180, 365 days")
    print("This will take ~30-45 minutes total...\n")

    window_sizes = [30, 60, 90, 180, 365]
    all_results = {}

    for window in window_sizes:
        print(f"\n{'='*70}")
        print(f"TESTING {window}-DAY WINDOW")
        print(f"{'='*70}\n")

        results = backtest_lppls(
            crash_threshold_pct=20,
            lookforward_days=60,
            warning_window_days=60,
            test_interval_days=7,
            window_days=window
        )

        all_results[window] = results

        print(f"\n{window}-DAY WINDOW RESULTS:")
        print(f"  Precision: {results['metrics']['precision']*100:.1f}%")
        print(f"  Recall: {results['metrics']['recall']*100:.1f}%")
        print(f"  F1 Score: {results['metrics']['f1_score']:.3f}")
        print(f"  Avg Lead Time: {results['metrics']['avg_lead_time_days']:.1f} days")
        print(f"  True Positives: {results['metrics']['true_positives']}")
        print(f"  False Positives: {results['metrics']['false_positives']}")
        print(f"  False Negatives: {results['metrics']['false_negatives']}")

    print(f"\n{'='*70}")
    print("COMPARISON SUMMARY")
    print(f"{'='*70}\n")

    # Create comparison table
    print(f"{'Window':<10} {'Precision':<12} {'Recall':<12} {'F1':<10} {'Lead Time':<12} {'TP':<6} {'FP':<6} {'FN':<6}")
    print("-" * 80)

    for window in window_sizes:
        m = all_results[window]['metrics']
        print(f"{window:>3} days   {m['precision']*100:>6.1f}%      {m['recall']*100:>6.1f}%      "
              f"{m['f1_score']:>6.3f}   {m['avg_lead_time_days']:>6.1f} days   "
              f"{m['true_positives']:>3}    {m['false_positives']:>3}    {m['false_negatives']:>3}")

    # Find best performers
    print(f"\n{'='*70}")
    print("BEST PERFORMERS BY METRIC")
    print(f"{'='*70}\n")

    best_precision_window = max(window_sizes, key=lambda w: all_results[w]['metrics']['precision'])
    best_recall_window = max(window_sizes, key=lambda w: all_results[w]['metrics']['recall'])
    best_f1_window = max(window_sizes, key=lambda w: all_results[w]['metrics']['f1_score'])
    lowest_fp_window = min(window_sizes, key=lambda w: all_results[w]['metrics']['false_positives'])

    print(f"Best Precision:        {best_precision_window:>3} days ({all_results[best_precision_window]['metrics']['precision']*100:.1f}%)")
    print(f"Best Recall:           {best_recall_window:>3} days ({all_results[best_recall_window]['metrics']['recall']*100:.1f}%)")
    print(f"Best F1 Score:         {best_f1_window:>3} days ({all_results[best_f1_window]['metrics']['f1_score']:.3f})")
    print(f"Fewest False Alarms:   {lowest_fp_window:>3} days ({all_results[lowest_fp_window]['metrics']['false_positives']} FPs)")

    # Analyze patterns
    print(f"\n{'='*70}")
    print("ANALYSIS & RECOMMENDATIONS")
    print(f"{'='*70}\n")

    # Check if shorter windows are more precise
    short_precision = all_results[30]['metrics']['precision']
    long_precision = all_results[365]['metrics']['precision']

    if short_precision > long_precision * 1.2:
        print("✓ Shorter windows (30-60 days) have BETTER precision")
        print("  → Use for: Trading short-term corrections")
    elif long_precision > short_precision * 1.2:
        print("✓ Longer windows (180-365 days) have BETTER precision")
        print("  → Use for: Detecting major cycle tops")
    else:
        print("≈ Window size doesn't significantly affect precision")

    # Check recall patterns
    short_recall = all_results[30]['metrics']['recall']
    long_recall = all_results[365]['metrics']['recall']

    print()
    if short_recall > long_recall * 1.2:
        print("✓ Shorter windows CATCH MORE crashes")
        print("  → Better for: Risk-averse traders")
    elif long_recall > short_recall * 1.2:
        print("✓ Longer windows CATCH MORE crashes")
        print("  → Better for: Major trend reversals")
    else:
        print("≈ Window size doesn't significantly affect recall")

    # F1 score recommendation
    print(f"\n✓ OVERALL BEST PERFORMER: {best_f1_window}-day window (F1: {all_results[best_f1_window]['metrics']['f1_score']:.3f})")

    # Save comparison results
    comparison_data = {
        'window_sizes': window_sizes,
        'results': {}
    }

    for window in window_sizes:
        comparison_data['results'][str(window)] = {
            'metrics': all_results[window]['metrics'],
            'total_signals': len(all_results[window]['signals']),
            'total_crashes': len(all_results[window]['crashes'])
        }

    with open('backtest_window_comparison.json', 'w') as f:
        json.dump(comparison_data, f, indent=2)

    print(f"\nResults saved to: backtest_window_comparison.json")

    return all_results

if __name__ == "__main__":
    results = compare_windows()
