# LPPLS API Usage Guide

## Quick Start

```bash
# Start the backend
cd backend
source venv/bin/activate
python app.py

# Server runs at http://localhost:8000
# GraphQL Playground: http://localhost:8000/graphql
```

---

## Available GraphQL Endpoints

### 1. **Test with Sample Data** (Fastest)
```graphql
query {
  testLpplsAnalysis {
    results {
      date
      actualPrice
      predictedPrice
    }
  }
}
```

**What it does:** Tests LPPLS on synthetic bubble data (8,475% growth over 10 months)

**Use this for:** Verifying the model works, understanding LPPLS parameters

---

### 2. **Real BTC Data Analysis** (Most Useful)
```graphql
query {
  btcLpplsAnalysis(startDate: "2020-01-01", endDate: "2021-11-01") {
    results {
      date
      actualPrice
      predictedPrice
    }
  }
}
```

**Parameters:**
- `startDate` (optional): Start analyzing from this date (format: YYYY-MM-DD)
- `endDate` (optional): Stop analyzing at this date
- If omitted, uses all available data (2014-2024)

**Use this for:** Analyzing historical BTC bubbles, backtesting strategies

**Examples:**
```graphql
# 2017 Bubble
btcLpplsAnalysis(startDate: "2016-01-01", endDate: "2017-12-31")

# 2021 Bubble
btcLpplsAnalysis(startDate: "2020-01-01", endDate: "2021-12-31")

# 2024 Run-up
btcLpplsAnalysis(startDate: "2023-01-01", endDate: "2024-08-01")

# All history
btcLpplsAnalysis
```

---

### 3. **Live Market Data** (Requires Internet)
```graphql
query {
  lpplsAnalysis(symbol: "BTC-USD") {
    results {
      date
      actualPrice
      predictedPrice
    }
  }
}
```

**Parameters:**
- `symbol`: Yahoo Finance ticker (e.g., "BTC-USD", "MSTR", "AAPL")

**What it does:** Fetches last 365 days from Yahoo Finance, runs LPPLS, predicts next 30 days

**Use this for:** Real-time analysis of current market conditions

**Note:** Requires internet connection to Yahoo Finance API

---

## Understanding the Output

### Response Structure
```json
{
  "data": {
    "btcLpplsAnalysis": {
      "results": [
        {
          "date": "2021-11-01",
          "actualPrice": 61004.41,
          "predictedPrice": 62869.51
        },
        {
          "date": "2021-11-02",
          "actualPrice": null,
          "predictedPrice": 63245.87
        }
      ]
    }
  }
}
```

**Fields:**
- `date`: Date of the data point
- `actualPrice`: Historical price (null for future predictions)
- `predictedPrice`: LPPLS model prediction (null if beyond critical time)

---

## Server Logs: Understanding LPPLS Parameters

When you run a query, the server prints detailed analysis:

```
============================================================
LPPLS Analysis on Real BTC Data
============================================================
Data points: 671
Date range: 2020-01-01 to 2021-11-01
Price range: $7,200.17 to $65,992.84
Price increase: 747.3%

============================================================
LPPLS Parameters:
============================================================
tc (critical time):     1034.94 days (2022-10-31)
m (power law exponent): 0.8262
w (log-periodic freq):  11.1426
a (price level):        105085.82
b (amplitude):          -350.52
c1 (cos amplitude):     0.0526
c2 (sin amplitude):     -0.1241
============================================================
```

### Parameter Explanations

#### **tc (Critical Time)** - MOST IMPORTANT
- **What it is:** Predicted crash date
- **Typical range:** 10-365 days beyond last data point
- **How to interpret:**
  - `tc` close to end of data (10-30 days): **IMMEDIATE RISK** 🔴
  - `tc` medium term (30-90 days): **ELEVATED RISK** 🟡
  - `tc` far out (90+ days): **LOWER RISK** 🟢

**Example:** If tc = 60 days out, the model predicts a crash in ~2 months

---

#### **m (Power Law Exponent)**
- **What it is:** How fast the bubble accelerates
- **Typical range:** 0.1 to 0.99
- **How to interpret:**
  - `m = 0.1-0.3`: Slow, steady bubble (classic pattern) ✓
  - `m = 0.4-0.7`: Moderate acceleration ✓
  - `m = 0.8-0.99`: Fast, explosive bubble ⚠️

**Lower m = More stable**
**Higher m = More dangerous**

**Example:**
- 2017: m = 0.20 (classic bubble)
- 2021: m = 0.83 (explosive, high risk)

---

#### **w (Log-Periodic Frequency)**
- **What it is:** How many corrections/oscillations during the bubble
- **Typical range:** 2 to 25
- **How to interpret:**
  - `w = 2-5`: Smooth growth, few corrections
  - `w = 6-15`: Moderate volatility
  - `w = 15-25`: Very choppy, many oscillations

**Lower w = Smooth rally**
**Higher w = Volatile rally**

**Example:**
- 2017: w = 2.0 (smooth parabola)
- 2021: w = 11.1 (choppy with many corrections)

---

#### **b (Amplitude)**
- **What it is:** Direction and strength of the bubble
- **Typical range:** -10,000 to +10,000 (varies by price)
- **How to interpret:**
  - **b < 0**: BUBBLE detected (price diverging upward) 🔴
  - **b > 0**: Crash recovery (price recovering from low)

**If b is negative, you're in a bubble.**

**Example:**
- 2017: b = -18,151 (strong bubble)
- 2021: b = -350 (weaker signal, but still bubble)

---

#### **c1, c2 (Oscillation Amplitudes)**
- **What they are:** Control the log-periodic oscillations
- **Typical range:** -1 to +1
- **How to interpret:**
  - Small values (±0.1): Smooth growth
  - Large values (±0.5+): Large swings during bubble

**Less important than tc, m, w, and b**

---

#### **Fit Error %**
- **What it is:** How well LPPLS fits historical data
- **Typical range:** 5% to 30%
- **How to interpret:**
  - `< 10%`: Excellent fit ✓
  - `10-20%`: Good fit ✓
  - `20-30%`: Acceptable fit ⚠️
  - `> 30%`: Poor fit ❌

**Lower error = More confidence in prediction**

**Example:**
- 2017: 11.9% error (good fit)
- 2021: 25.4% error (acceptable but less reliable)

---

## Red Flags & Warnings

The server will print warnings for parameter issues:

### ⚠️ **"tc hit lower bound"**
```
⚠️  tc hit lower bound (10.0)
```
**Meaning:** Model wants to predict crash immediately (in 10 days)
**Action:** VERY HIGH RISK - consider taking profits

---

### ⚠️ **"tc hit upper bound"**
```
⚠️  tc hit upper bound (365.0)
```
**Meaning:** Model can't find a good crash date (too far out)
**Action:** Probably NOT in bubble, or data is too noisy

---

### ⚠️ **"m hit lower bound"**
```
⚠️  m hit lower bound (0.1)
```
**Meaning:** Bubble is accelerating very slowly
**Action:** Either early bubble phase OR false positive

---

### ⚠️ **"m hit upper bound"**
```
⚠️  m hit upper bound (0.99)
```
**Meaning:** Bubble is accelerating extremely fast
**Action:** HIGH RISK - parabolic move, likely to crash soon

---

### ⚠️ **"Optimization success: False"**
```
Optimization success: False
```
**Meaning:** Model couldn't fit the data properly
**Action:** DON'T TRUST THIS PREDICTION - data is too noisy

---

## Trading Signal Examples

### 🔴 **HIGH RISK Signal**
```
tc:  32 days (close to end)
m:   0.85 (fast acceleration)
w:   15.2 (volatile)
b:   -15,000 (strong bubble)
fit: 8.5% (excellent fit)
warnings: none
```
**Action:** Strong sell signal - reduce position by 50-75%

---

### 🟡 **MEDIUM RISK Signal**
```
tc:  67 days (medium term)
m:   0.45 (moderate acceleration)
w:   6.3 (normal volatility)
b:   -3,200 (bubble detected)
fit: 18% (acceptable fit)
warnings: none
```
**Action:** Caution - reduce position by 25-50%, set tighter stops

---

### 🟢 **LOW RISK Signal**
```
tc:  180 days (far out)
m:   0.22 (slow acceleration)
w:   3.1 (smooth)
b:   -1,500 (weak bubble)
fit: 24% (mediocre fit)
warnings: tc hit upper bound
```
**Action:** Low concern - maintain position, normal management

---

### ❌ **INVALID Signal (Ignore)**
```
Optimization success: False
warnings: m hit upper bound, tc hit lower bound
fit: 35% (poor fit)
```
**Action:** Ignore this signal - model failed

---

## cURL Examples

### Test with sample data
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ testLpplsAnalysis { results { date actualPrice predictedPrice } } }"}'
```

### Analyze 2021 BTC bubble
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ btcLpplsAnalysis(startDate: \"2020-01-01\", endDate: \"2021-11-01\") { results { date actualPrice predictedPrice } } }"}'
```

### Get current MSTR analysis (requires internet)
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ lpplsAnalysis(symbol: \"MSTR\") { results { date actualPrice predictedPrice } } }"}'
```

---

## Python Example

```python
import requests
import json

url = "http://localhost:8000/graphql"

query = """
{
  btcLpplsAnalysis(startDate: "2020-01-01", endDate: "2021-11-01") {
    results {
      date
      actualPrice
      predictedPrice
    }
  }
}
"""

response = requests.post(url, json={"query": query})
data = response.json()

results = data['data']['btcLpplsAnalysis']['results']

# Find last actual price
last_actual = [r for r in results if r['actualPrice'] is not None][-1]
print(f"Last price: ${last_actual['actualPrice']:.2f}")
print(f"Prediction: ${last_actual['predictedPrice']:.2f}")
```

---

## Common Questions

### Q: Why are some predictedPrice values null?
**A:** Beyond the critical time (tc), the model predicts a singularity (crash). We return null instead of infinite/NaN values.

### Q: What's a good crash threshold to test?
**A:**
- 10%: Catches small corrections (too sensitive)
- 20%: Good balance (recommended)
- 30%: Only major crashes (less sensitive)

### Q: How often should I run LPPLS?
**A:**
- Daily: Overkill, parameters change slowly
- Weekly: Good balance (what backtest used)
- Monthly: Too slow, might miss signals

### Q: Should I trust LPPLS when fit error > 20%?
**A:** Proceed with caution. >20% error means the model isn't fitting well. Look for confirming signals from other indicators.

### Q: Can I use this for stocks (MSTR, TSLA, etc.)?
**A:** Yes, use the `lpplsAnalysis` endpoint with Yahoo Finance symbols. But remember: LPPLS works best on crypto-like parabolic moves.

---

## Next Steps

1. **Read the backtest analysis:** See `BACKTEST_ANALYSIS.md` for honest assessment
2. **Run your own tests:** Try different date ranges on BTC data
3. **Experiment with parameters:** Edit `backtest_lppls.py` to test different thresholds
4. **Combine indicators:** Use LPPLS with RSI, moving averages, volume, etc.

---

*Updated: 2024-10-30*
