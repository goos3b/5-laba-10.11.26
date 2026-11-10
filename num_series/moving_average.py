from typing import List, Sequence

def check_window(window: int, n: int) -> None:
    """Окно — целое >= 1 и не больше длины ряда."""
    if isinstance(window, bool) or not isinstance(window, int):
        raise ValueError(
            f"window должно быть целым числом (получено: {window!r})"
        )
    if window < 1:
        raise ValueError(
            f"window должно быть >= 1 (получено: {window})"
        )
    if window > n:
        raise ValueError(
            f"окно ({window}) больше ряда ({n})"
        )

def simple_moving_average(data: Sequence[float],
                          window: int) -> List[float]:
    """SMA через бегущую сумму (O(n))."""
    n = len(data)
    if n == 0:
        raise ValueError("Ряд пуст: расчёт SMA невозможен")
    check_window(window, n)

    running = sum(data[:window])
    result = [running / window]
    for i in range(window, n):
        running += data[i] - data[i - window]
        result.append(running / window)
    return result