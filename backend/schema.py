import strawberry
from typing import List, Optional
import yfinance as yf
from datetime import datetime, timedelta
from lppls_model import LPPLSModel
import numpy as np
import json
import pandas as pd

@strawberry.type
class PricePoint:
    date: str
    price: float

@strawberry.type
class LPPLSResultPoint:
    date: str
    actual_price: Optional[float]
    predicted_price: float

@strawberry.type
class LPPLSResult:
    results: List[LPPLSResultPoint]

@strawberry.type
class Query:
    @strawberry.field
    def lppls_analysis(self, symbol: str) -> LPPLSResult:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

        # Download data with error handling
        data = yf.download(symbol, start=start_date, end=end_date)

        # Check if data was successfully downloaded
        if data.empty:
            raise ValueError(f"No data available for symbol '{symbol}'. Please check the symbol or try again later.")

        time = np.array((data.index - data.index[0]).days)
        price = np.array(data['Close'])

        # Validate that we have enough data points
        if len(time) < 10:
            raise ValueError(f"Insufficient data for symbol '{symbol}'. Need at least 10 data points, got {len(time)}.")

        model = LPPLSModel(time, price, start_date)
        params = model.fit()
        print("Parameters: ",params)

        future_days = 30
        future_time = np.arange(time[-1] + 1, time[-1] + future_days + 1)


        all_time = np.concatenate([time, future_time])
        results = model.format_results(params, all_time)

        return LPPLSResult(
            results=[
                LPPLSResultPoint(
                    date=result['date'],
                    actual_price=result['actual_price'],
                    predicted_price=result['predicted_price']
                )
                for result in results
            ]
        )

    @strawberry.field
    def test_lppls_analysis(self) -> LPPLSResult:
        """Test LPPLS analysis using sample bubble data from JSON file"""

        # Load sample data
        with open('sample_data.json', 'r') as f:
            sample_data = json.load(f)

        # Convert to arrays
        dates = [datetime.strptime(item['date'], '%Y-%m-%d') for item in sample_data['data']]
        prices = np.array([item['price'] for item in sample_data['data']])

        # Calculate time in days from start
        start_date = dates[0]
        time = np.array([(d - start_date).days for d in dates])

        print(f"\n{'='*60}")
        print(f"LPPLS Model Test with Sample Bubble Data")
        print(f"{'='*60}")
        print(f"Data points: {len(time)}")
        print(f"Date range: {dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}")
        print(f"Price range: ${prices[0]:.2f} to ${prices[-1]:.2f}")
        print(f"Price increase: {((prices[-1] / prices[0]) - 1) * 100:.1f}%")

        # Fit LPPLS model
        model = LPPLSModel(time, prices, start_date)
        params = model.fit()

        tc, m, w, a, b, c1, c2 = params

        print(f"\n{'='*60}")
        print(f"LPPLS Parameters:")
        print(f"{'='*60}")
        print(f"tc (critical time):     {tc:.2f} days ({(start_date + timedelta(days=int(tc))).strftime('%Y-%m-%d')})")
        print(f"m (power law exponent): {m:.4f}")
        print(f"w (log-periodic freq):  {w:.4f}")
        print(f"a (price level):        {a:.2f}")
        print(f"b (amplitude):          {b:.2f}")
        print(f"c1 (cos amplitude):     {c1:.4f}")
        print(f"c2 (sin amplitude):     {c2:.4f}")
        print(f"{'='*60}\n")

        # Generate predictions for existing data + 30 days future
        future_days = 30
        future_time = np.arange(time[-1] + 1, time[-1] + future_days + 1)
        all_time = np.concatenate([time, future_time])

        results = model.format_results(params, all_time)

        return LPPLSResult(
            results=[
                LPPLSResultPoint(
                    date=result['date'],
                    actual_price=result['actual_price'],
                    predicted_price=result['predicted_price']
                )
                for result in results
            ]
        )

schema = strawberry.Schema(query=Query)