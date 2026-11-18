from .generator import random_series, sine_series, trend_series
from .stats import mean, median, summarize, variance, stdev 
from .moving_average import (simple_moving_average, simple_moving_average_deque,centered_moving_average,exponential_moving_average, benchmark_moving_average, )
from .io__json import save_series_to_json, load_series_from_json
from .generator import uniform_series 
__all__ = [
    "random_series", "sine_series", "trend_series",
    "mean", "median", "range", "summarize",
    "simple_moving_average",
    "centered_moving_average",
    "exponential_moving_average",
    "save_series_to_json",
    "load_series_from_json",
    "simple_moving_average_deque",
    "benchmark_moving_average",
    "variance", "stdev", "uniform_series"]

__version__ = "1.0.0"