#!/usr/bin/env python3
"""
LPPLS Backtesting Framework

Tests the LPPLS model's ability to predict Bitcoin crashes by:
1. Rolling window analysis through historical data
2. Comparing predictions against actual price movements
3. Calculating hit rates, false positives, and lead times
"""

import json
import numpy as np
from datetime import datetime, timedelta
from lppls_model import LPPLSModel
import sys

def load_btc_data():
    """Load BTC historical data"""
    with open('BTC-USD.json', 'r') as f:
        return json.load(f)

def find_crashes(prices, dates, threshold_pct, lookforward_days):
    """
    Find all crashes in the dataset

    Args:
        prices: Array of prices
        dates: Array of dates
        threshold_pct: Minimum drop % to count as crash (e.g., 20 for 20%)
        lookforward_days: Days to look forward for crash

    Returns:
        List of (index, crash_date, drop_pct, days_to_crash)
    """
    crashes = []

    for i in range(len(prices) - lookforward_days):
        current_price = prices[i]
        future_prices = prices[i+1:i+lookforward_days+1]

        if len(future_prices) == 0:
            continue

        min_future_price = min(future_prices)
        drop_pct = ((current_price - min_future_price) / current_price) * 100

        if drop_pct >= threshold_pct:
            # Find when the crash happened
            crash_idx = i + 1 + np.argmin(future_prices)
            days_to_crash = crash_idx - i
            crashes.append({
                'index': i,
                'date': dates[i],
                'crash_date': dates[crash_idx],
                'drop_pct': drop_pct,
                'days_to_crash': days_to_crash,
                'current_price': current_price,
                'crash_price': min_future_price
            })

    # Deduplicate - keep only the first detection of each crash
    unique_crashes = []
    last_crash_idx = -50  # Start far back

    for crash in crashes:
        if crash['index'] - last_crash_idx > 30:  # At least 30 days apart
            unique_crashes.append(crash)
            last_crash_idx = crash['index']

    return unique_crashes

def run_lppls_at_point(prices, dates, end_idx, window_days=180):
    """
    Run LPPLS model at a specific point in time

    Args:
        prices: Full price array
        dates: Full date array
        end_idx: Index to end analysis at (simulating real-time)
        window_days: Days of history to use

    Returns:
        dict with LPPLS results or None if failed
    """
    # Find start index (window_days back)
    end_date = dates[end_idx]
    start_date = end_date - timedelta(days=window_days)

    # Get data in window
    window_data = [(dates[i], prices[i]) for i in range(end_idx+1)
                   if dates[i] >= start_date]

    if len(window_data) < 50:
        return None

    window_dates = [d[0] for d in window_data]
    window_prices = np.array([d[1] for d in window_data])

    # Calculate time array
    start = window_dates[0]
    time = np.array([(d - start).days for d in window_dates])

    try:
        # Fit LPPLS model
        model = LPPLSModel(time, window_prices, start)
        params = model.fit()

        tc, m, w, a, b, c1, c2 = params

        # Calculate days until predicted crash
        days_to_tc = tc - time[-1]
        tc_date = end_date + timedelta(days=int(days_to_tc))

        # Calculate fit quality
        predicted = model.predict(params, time)
        errors = np.abs(predicted - window_prices)
        mean_error_pct = np.mean(errors / window_prices) * 100

        return {
            'date': end_date,
            'tc': tc,
            'tc_date': tc_date,
            'days_to_tc': days_to_tc,
            'm': m,
            'w': w,
            'a': a,
            'b': b,
            'c1': c1,
            'c2': c2,
            'fit_error_pct': mean_error_pct,
            'current_price': prices[end_idx],
            'is_bubble': b < 0  # Negative b indicates bubble
        }
    except Exception as e:
        return None

def backtest_lppls(crash_threshold_pct=20, lookforward_days=60,
                   warning_window_days=60, test_interval_days=7,
                   window_days=180):
    """
    Run full backtest

    Args:
        crash_threshold_pct: Minimum drop to count as crash (default 20%)
        lookforward_days: Days to look forward for crashes
        warning_window_days: How far in advance tc should be to count as warning
        test_interval_days: Test every N days (7 = weekly)
        window_days: Days of history to use for LPPLS fitting

    Returns:
        dict with full results
    """
    print("="*70)
    print("LPPLS EXHAUSTIVE BACKTEST")
    print("="*70)
    print(f"Crash threshold: {crash_threshold_pct}%")
    print(f"Lookforward period: {lookforward_days} days")
    print(f"Warning window: {warning_window_days} days")
    print(f"Test interval: {test_interval_days} days")
    print(f"LPPLS window: {window_days} days")
    print("="*70)

    # Load data
    btc_data = load_btc_data()
    dates = [datetime.strptime(d['Date'], '%Y-%m-%d') for d in btc_data]
    prices = np.array([float(d['Close']) for d in btc_data])

    print(f"\nLoaded {len(dates)} days of BTC data")
    print(f"Date range: {dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}")
    print(f"Price range: ${prices[0]:.2f} to ${max(prices):.2f}")

    # Find all crashes
    print(f"\nFinding all {crash_threshold_pct}%+ crashes...")
    crashes = find_crashes(prices, dates, crash_threshold_pct, lookforward_days)
    print(f"Found {len(crashes)} crashes:")
    for crash in crashes:
        print(f"  {crash['date'].strftime('%Y-%m-%d')}: "
              f"-{crash['drop_pct']:.1f}% over {crash['days_to_crash']} days "
              f"(${crash['current_price']:.0f} → ${crash['crash_price']:.0f})")

    # Run LPPLS at regular intervals
    print(f"\nRunning LPPLS model every {test_interval_days} days...")
    lppls_signals = []

    start_idx = window_days + 100  # Need enough history
    end_idx = len(dates) - lookforward_days  # Need future data to validate

    test_points = list(range(start_idx, end_idx, test_interval_days))
    total_tests = len(test_points)

    for count, idx in enumerate(test_points):
        if count % 20 == 0:
            print(f"  Progress: {count}/{total_tests} ({100*count/total_tests:.1f}%)")

        result = run_lppls_at_point(prices, dates, idx, window_days)
        if result and result['is_bubble'] and 0 < result['days_to_tc'] <= warning_window_days:
            lppls_signals.append({
                'index': idx,
                **result
            })

    print(f"\nLPPLS issued {len(lppls_signals)} warnings")

    # Evaluate signals
    print("\nEvaluating signal accuracy...")

    true_positives = []  # Correctly predicted crashes
    false_positives = []  # Warned but no crash
    false_negatives = []  # Crashed but no warning

    # Check each LPPLS signal
    for signal in lppls_signals:
        signal_idx = signal['index']
        signal_date = signal['date']

        # Look forward for actual crash
        future_prices = prices[signal_idx:signal_idx+lookforward_days+1]
        current_price = prices[signal_idx]

        if len(future_prices) > 1:
            min_future = min(future_prices[1:])
            actual_drop_pct = ((current_price - min_future) / current_price) * 100

            if actual_drop_pct >= crash_threshold_pct:
                crash_idx = signal_idx + np.argmin(future_prices[1:]) + 1
                true_positives.append({
                    'signal': signal,
                    'actual_drop_pct': actual_drop_pct,
                    'days_to_crash': crash_idx - signal_idx,
                    'predicted_days': signal['days_to_tc']
                })
            else:
                false_positives.append({
                    'signal': signal,
                    'actual_drop_pct': actual_drop_pct
                })

    # Check crashes that weren't predicted
    for crash in crashes:
        crash_idx = crash['index']
        crash_date = crash['date']

        # Look back for warnings
        warned = False
        for signal in lppls_signals:
            if signal['index'] < crash_idx <= signal['index'] + warning_window_days:
                warned = True
                break

        if not warned:
            false_negatives.append(crash)

    # Calculate metrics
    tp_count = len(true_positives)
    fp_count = len(false_positives)
    fn_count = len(false_negatives)

    precision = tp_count / (tp_count + fp_count) if (tp_count + fp_count) > 0 else 0
    recall = tp_count / (tp_count + fn_count) if (tp_count + fn_count) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    # Lead time analysis
    avg_lead_time = np.mean([tp['days_to_crash'] for tp in true_positives]) if true_positives else 0

    return {
        'config': {
            'crash_threshold_pct': crash_threshold_pct,
            'lookforward_days': lookforward_days,
            'warning_window_days': warning_window_days,
            'test_interval_days': test_interval_days,
            'window_days': window_days
        },
        'crashes': crashes,
        'signals': lppls_signals,
        'true_positives': true_positives,
        'false_positives': false_positives,
        'false_negatives': false_negatives,
        'metrics': {
            'total_crashes': len(crashes),
            'total_signals': len(lppls_signals),
            'true_positives': tp_count,
            'false_positives': fp_count,
            'false_negatives': fn_count,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'avg_lead_time_days': avg_lead_time
        }
    }

def print_results(results):
    """Print backtest results in readable format"""
    print("\n" + "="*70)
    print("BACKTEST RESULTS")
    print("="*70)

    metrics = results['metrics']

    print(f"\nTotal crashes detected in data: {metrics['total_crashes']}")
    print(f"Total LPPLS warnings issued: {metrics['total_signals']}")
    print()
    print(f"True Positives (correct warnings): {metrics['true_positives']}")
    print(f"False Positives (false alarms): {metrics['false_positives']}")
    print(f"False Negatives (missed crashes): {metrics['false_negatives']}")
    print()
    print(f"Precision (when it warns, how often correct): {metrics['precision']*100:.1f}%")
    print(f"Recall (% of crashes it catches): {metrics['recall']*100:.1f}%")
    print(f"F1 Score (overall accuracy): {metrics['f1_score']:.3f}")
    print(f"Average Lead Time: {metrics['avg_lead_time_days']:.1f} days")

    print("\n" + "="*70)
    print("TRUE POSITIVES (Correct Predictions):")
    print("="*70)
    for tp in results['true_positives']:
        sig = tp['signal']
        print(f"{sig['date'].strftime('%Y-%m-%d')}: "
              f"Predicted crash in {tp['predicted_days']:.0f} days, "
              f"actual crash in {tp['days_to_crash']} days "
              f"(-{tp['actual_drop_pct']:.1f}%)")

    print("\n" + "="*70)
    print("FALSE NEGATIVES (Missed Crashes):")
    print("="*70)
    for fn in results['false_negatives']:
        print(f"{fn['date'].strftime('%Y-%m-%d')}: "
              f"Crashed -{fn['drop_pct']:.1f}% but NO WARNING issued")

    print("\n" + "="*70)
    print("CONCLUSION:")
    print("="*70)

    if metrics['precision'] >= 0.6 and metrics['recall'] >= 0.5:
        print("✅ LPPLS shows promise for crash prediction")
        print(f"   - Catches {metrics['recall']*100:.0f}% of crashes")
        print(f"   - {metrics['precision']*100:.0f}% of warnings are correct")
        print(f"   - Gives ~{metrics['avg_lead_time_days']:.0f} days warning")
    elif metrics['precision'] >= 0.4 or metrics['recall'] >= 0.4:
        print("⚠️  LPPLS has limited predictive power")
        print("   - Better than random, but not reliable alone")
        print("   - Should be combined with other indicators")
    else:
        print("❌ LPPLS performs poorly for crash prediction")
        print("   - Not better than random guessing")
        print("   - Not recommended for trading decisions")

if __name__ == "__main__":
    print("Starting LPPLS Exhaustive Backtest...")
    print("This will take 15-20 minutes...\n")

    # Run backtest with default parameters
    results = backtest_lppls(
        crash_threshold_pct=20,
        lookforward_days=60,
        warning_window_days=60,
        test_interval_days=7,
        window_days=180
    )

    print_results(results)

    # Save simplified results to JSON (avoid circular references)
    print("\nSaving results to backtest_results.json...")

    simplified_results = {
        'config': results['config'],
        'metrics': results['metrics'],
        'total_crashes': len(results['crashes']),
        'total_signals': len(results['signals']),
        'true_positives_count': len(results['true_positives']),
        'false_positives_count': len(results['false_positives']),
        'false_negatives_count': len(results['false_negatives']),
        'crash_dates': [c['date'].strftime('%Y-%m-%d') for c in results['crashes']],
        'true_positive_dates': [tp['signal']['date'].strftime('%Y-%m-%d') for tp in results['true_positives']],
        'false_negative_dates': [fn['date'].strftime('%Y-%m-%d') for fn in results['false_negatives']]
    }

    with open('backtest_results.json', 'w') as f:
        json.dump(simplified_results, f, indent=2)

    print("Done! Results saved.")
