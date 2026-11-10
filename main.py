from num_series import sine_series, summarize, simple_moving_average

data = sine_series(20, noise=0.5, seed=42)
stats = summarize(data)
sma = simple_moving_average(data, 3)

print("Данные:", data)
print("Статистика:", stats)
print("SMA (window=3):", sma)
