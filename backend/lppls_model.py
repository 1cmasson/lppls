import numpy as np
from scipy.optimize import minimize
from datetime import datetime, timedelta
import debugpy

class LPPLSModel:
    def __init__(self, time, price, start_date):
        self.time = time
        self.price = price
        self.start_date = start_date

    def lppls_func(self, t, tc, m, w, a, b, c1, c2):
        return a + b * np.power(tc - t, m) * (1 + c1 * np.cos(w * np.log(tc - t)) + c2 * np.sin(w * np.log(tc - t)))

    def fit(self):
        def obj_func(params):
            tc, m, w, a, b, c1, c2 = params

            # Prevent invalid parameter combinations
            if tc <= max(self.time):
                return 1e10

            try:
                y_pred = self.lppls_func(self.time, tc, m, w, a, b, c1, c2)

                # Check for NaN or Inf
                if np.any(np.isnan(y_pred)) or np.any(np.isinf(y_pred)):
                    return 1e10

                # Sum of squared errors
                return np.sum((y_pred - self.price) ** 2)
            except:
                return 1e10

        # Better initial guess based on data characteristics
        t_max = max(self.time)
        price_range = max(self.price) - min(self.price)

        # tc should be reasonably beyond the data (30-90 days is typical for prediction)
        tc_init = t_max + 60

        # Initial guess: [tc, m, w, a, b, c1, c2]
        initial_guess = [
            tc_init,           # Critical time: 60 days beyond data
            0.5,               # Power law exponent (typical range 0.1-0.9)
            6.28,              # Angular frequency (2*pi is common)
            np.mean(self.price),  # Price level near mean
            -price_range,      # Amplitude (negative for bubble)
            0.1,               # Cosine amplitude
            0.1                # Sine amplitude
        ]

        # Improved bounds: [tc, m, w, a, b, c1, c2]
        bounds = [
            (t_max + 10, t_max + 365),  # tc: 10-365 days beyond data
            (0.1, 0.99),                # m: reasonable power law range
            (2, 25),                    # w: typical oscillation frequency
            (min(self.price) * 0.1, max(self.price) * 10),  # a: price level
            (-price_range * 100, price_range * 100),        # b: amplitude
            (-1, 1),                    # c1: cosine term
            (-1, 1)                     # c2: sine term
        ]

        result = minimize(obj_func, initial_guess, method='L-BFGS-B', bounds=bounds,
                         options={'maxiter': 10000, 'ftol': 1e-10})

        # Check if parameters hit bounds (indicates poor fit)
        params = result.x
        tc, m, w, a, b, c1, c2 = params

        warnings = []
        if abs(tc - bounds[0][0]) < 1:
            warnings.append(f"⚠️  tc hit lower bound ({bounds[0][0]:.1f})")
        if abs(tc - bounds[0][1]) < 1:
            warnings.append(f"⚠️  tc hit upper bound ({bounds[0][1]:.1f})")
        if abs(m - bounds[1][0]) < 0.01:
            warnings.append(f"⚠️  m hit lower bound ({bounds[1][0]})")
        if abs(m - bounds[1][1]) < 0.01:
            warnings.append(f"⚠️  m hit upper bound ({bounds[1][1]})")

        if warnings:
            print("Parameter fitting warnings:")
            for w in warnings:
                print(f"  {w}")

        print(f"Optimization success: {result.success}")
        print(f"Final cost: {result.fun:.2e}")

        return result.x

    def predict(self, params, time_range):
        tc, m, w, a, b, c1, c2 = params
        predicted_prices = self.lppls_func(time_range, tc, m, w, a, b, c1, c2)
        return predicted_prices

    def format_results(self, params, time_range):
        tc, m, w, a, b, c1, c2 = params
        predicted_prices = self.predict(params, time_range)
        results = []

        for i, t in enumerate(time_range):
            date = (self.start_date + timedelta(days=int(t))).strftime('%Y-%m-%d')
            actual_price = self.price[i] if i < len(self.price) else None
            predicted_price = predicted_prices[i]

            # Cap predictions at critical time minus a small buffer
            # Beyond tc, the model predicts a singularity (crash)
            if t >= tc - 1:
                predicted_price = None  # Don't predict past critical time

            # Handle NaN values
            if predicted_price is not None and (np.isnan(predicted_price) or np.isinf(predicted_price)):
                predicted_price = None

            results.append({
                'date': date,
                'actual_price': actual_price,
                'predicted_price': predicted_price
            })

        return results