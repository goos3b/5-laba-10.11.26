from __future__ import annotations

import argparse
import sys
from datetime import datetime 
from typing import List

from num_series import (
    random_series, sine_series, trend_series,
    mean, median, spread, summarize,
    simple_moving_average, centered_moving_average, exponential_moving_average,
    save_series_to_json, load_series_from_json
)
try:
    from num_series.stats import save_to_json
    HAS_SAVE_TO_JSON = True
except ImportError:
    HAS_SAVE_TO_JSON = False
    
def build_series(kind: str, n: int, seed: int) -> List[float]:
    """Возвращает числовой ряд заданного типа."""
    if kind == "random":
        return random_series(n, low=-50, high=50, seed=seed)
    if kind == "sine":
        return sine_series(n, amplitude=10, frequency=2, noise=1.5, seed=seed)
    if kind == "trend":
        return trend_series(n, start=0, step=1.0, noise=0.5, seed=seed)
    raise ValueError(f"Неизвестный тип ряда: {kind!r}")


# -------------------------------------------------------------------
# Печать
# -------------------------------------------------------------------

def print_series(title: str, values: List[float], fmt: str = "{:>10.3f}") -> None:
    """Печатает ряд в одну строку с выравниванием."""
    if not values:
        print(f"\n{title}: (пусто)")
        return
    print(f"\n{title} (n={len(values)}):")
    # Разбиваем вывод на строки по 10 элементов, чтобы не улетало за экран
    chunk_size = 10
    for i in range(0, len(values), chunk_size):
        chunk = values[i:i + chunk_size]
        print(" " + " ".join(fmt.format(v) for v in chunk))


def print_header(kind: str, n: int) -> None:
    print("=" * 60)
    print(f"Тип ряда: {kind}, n = {n}")
    print("-" * 60)


def print_stats(stats: dict) -> None:
    """Печатает блок базовых статистических показателей."""
    print(f"Среднее арифметическое : {stats['mean']:>10.4f}")
    print(f"Медиана       : {stats['median']:>10.4f}")
    print(f"Размах (max - min) : {stats['spread']:>10.4f}")
    print(f"min / max    : {stats['min']:>10.4f} / {stats['max']:.4f}")


def print_footer() -> None:
    print("=" * 60)


# -------------------------------------------------------------------
# Разбор аргументов
# -------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Алгоритмическая обработка числовых рядов",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--kind", choices=["random", "sine", "trend"], default="sine",
        help="тип генерируемого ряда",
    )
    parser.add_argument(
        "--n", type=int, default=20,
        help="количество точек в ряде",
    )
    parser.add_argument(
        "--window", type=int, default=3,
        help="размер окна для скользящей средней",
    )
    parser.add_argument(
        "--alpha", type=float, default=0.3,
        help="коэффициент сглаживания для EMA, 0 < alpha <= 1",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="зерно ГПСЧ для воспроизводимости",
    )
    parser.add_argument(
        "--export", metavar="FILE",
        help="экспорт исходного ряда в CSV-файл",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="вывод результата в формате JSON в консоль",
    )
    parser.add_argument(
        "--save", action="store_true",
        help="сохранить полный результат в output/result.json",
    )
    return parser


# -------------------------------------------------------------------
# Экспорт
# -------------------------------------------------------------------

def export_csv(data: List[float], filename: str) -> None:
    """Сохраняет ряд в CSV: столбцы i (номер точки) и value (значение)."""
    import csv
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["i", "value"])
            for i, v in enumerate(data):
                writer.writerow([i, v])
    except OSError as e:
        raise OSError(f"Не удалось записать файл {filename}: {e}")


def export_json(payload: dict) -> None:
    """Печатает результат в формате JSON."""
    import json
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def safe_save_to_json(payload: dict, filename: str) -> bool:
    """Обёртка для сохранения, чтобы программа не падала, если функции нет."""
    if not HAS_SAVE_TO_JSON:
        print(f"Предупреждение: функция save_to_json не найдена. Файл {filename} не будет создан.", file=sys.stderr)
        return False
    
    try:
        save_to_json(payload, filename)
        return True
    except Exception as e:
        print(f"Ошибка при сохранении в {filename}: {e}", file=sys.stderr)
        return False


# -------------------------------------------------------------------
# main
# -------------------------------------------------------------------

def main(argv: List[str] | None = None) -> int:
    """Точка входа. Возвращает код выхода (0 — успех, 1 — ошибка)."""
    args = build_parser().parse_args(argv)

    try:
        # 1. Расчёт данных
        data = build_series(args.kind, args.n, args.seed)
        stats = summarize(data)
        
        sma = simple_moving_average(data, args.window)
        ema = exponential_moving_average(data, args.alpha)
        
        cma = (
            centered_moving_average(data, args.window)
            if args.window % 2 == 1 else None
        )

        # 2. Сборка итогового словаря (только внутри try, где данные уже есть)
        result = {
            "kind": args.kind,
            "n": args.n,
            "created": datetime.now().isoformat(),
            "data": data,
            "stats": stats,
            "sma": sma,
            "ema": ema,
            "cma": cma
        }

        # 3. Сохранение в JSON файл (если пользователь попросил флагом --save)
        if args.save:
            if safe_save_to_json(result, "output/result.json"):
                print("Готово! Данные сохранены в output/result.json")

        # 4. Вывод в консоль в формате JSON (если пользователь попросил флагом --json)
        if args.json:
            export_json(result)
            # Если нужен только JSON, можно завершить здесь, но оставим вывод статистики ниже, если не указано иное
            # return 0 

    except ValueError as err:
        # Понятное сообщение вместо «сырого» трейсбека
        print(f"Ошибка: {err}.", file=sys.stderr)
        return 1
    except Exception as err:
        # Ловим любые другие неожиданные ошибки
        print(f"Критическая ошибка: {err}.", file=sys.stderr)
        return 1

    # 5. Вывод результатов в консоль (табличный вид)
    print_header(args.kind, args.n)
    print_stats(stats)

    print_series("Исходный ряд", data)
    print_series(f"SMA (window={args.window})", sma)
    print_series(f"EMA (alpha={args.alpha})", ema)
    
    if cma is not None:
        print_series(f"Центрированное MA (window={args.window})", cma)

    print_footer()

    # 6. Экспорт в CSV
    if args.export:
        try:
            export_csv(data, args.export)
            print(f"Экспортировано в {args.export}")
        except OSError as err:
            print(f"Ошибка записи в файл: {err}.", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
