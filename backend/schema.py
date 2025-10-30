import strawberry
from typing import List, Optional
import yfinance as yf
from datetime import datetime, timedelta
from lppls_model import LPPLSModel
import numpy as np

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

schema = strawberry.Schema(query=Query)