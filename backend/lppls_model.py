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
            y_pred = self.lppls_func(self.time, tc, m, w, a, b, c1, c2)
            return np.sum((y_pred - self.price) ** 2)

        initial_guess = [max(self.time) + 1, 0.5, 6.28, 0, 1, 0.1, 0.1]
        bounds = [(max(self.time), max(self.time) + 365), (0, 1), (0, 20), (None, None), (None, None), (None, None), (None, None)]

        result = minimize(obj_func, initial_guess, method='L-BFGS-B', bounds=bounds)
        return result.x

    def predict(self, params, time_range):
        tc, m, w, a, b, c1, c2 = params
        predicted_prices = self.lppls_func(time_range, tc, m, w, a, b, c1, c2)
        return predicted_prices

    def format_results(self, params, time_range):
        predicted_prices = self.predict(params, time_range)
        results = []

        for i, t in enumerate(time_range):
            date = (self.start_date + timedelta(days=int(t))).strftime('%Y-%m-%d')
            actual_price = self.price[i] if i < len(self.price) else None
            predicted_price = predicted_prices[i]

            results.append({
                'date': date,
                'actual_price': actual_price,
                'predicted_price': predicted_price
            })

        return results