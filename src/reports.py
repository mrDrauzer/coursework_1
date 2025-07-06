import json
import logging
from datetime import datetime, timedelta

import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def log(func):
    """Декоратор для логирования вызова функции."""

    def wrapper(*args, **kwargs):
        logging.info(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        return func(*args, **kwargs)

    return wrapper


@log
def report_by_category(df: pd.DataFrame, category: str, date_from: str) -> str:
    """
    Отчёт: траты по категории за последние 3 месяца с даты date_from.
    :param df: DataFrame с транзакциями (ожидаются столбцы 'category', 'date', 'amount')
    :param category: категория трат
    :param date_from: дата отсчёта (строка в формате 'YYYY-MM-DD')
    :return: JSON-строка с суммой трат по категории
    """
    date_from_dt = datetime.strptime(date_from, "%Y-%m-%d")
    date_to_dt = date_from_dt + timedelta(days=90)
    # Убедимся, что столбец 'date' — это datetime
    df["date"] = pd.to_datetime(df["date"])
    mask = (df["category"] == category) & (df["date"] >= date_from_dt) & (df["date"] < date_to_dt)
    total = df.loc[mask, "amount"].sum()
    result = {
        "category": category,
        "period_start": date_from,
        "period_end": date_to_dt.strftime("%Y-%m-%d"),
        "total": float(total),
    }
    return json.dumps(result, ensure_ascii=False)


@log
def report_by_weekday(df: pd.DataFrame, date_from: str = None) -> str:
    """
    Отчёт: траты по дням недели.
    :param df: DataFrame с транзакциями (ожидаются столбцы 'date', 'amount')
    :param date_from: необязательная дата отсчёта (строка в формате 'YYYY-MM-DD')
    :return: JSON-строка с расходами по дням недели
    """
    df["date"] = pd.to_datetime(df["date"])
    if date_from:
        date_from_dt = datetime.strptime(date_from, "%Y-%m-%d")
        df = df[df["date"] >= date_from_dt]
    df["weekday"] = df["date"].dt.day_name()
    result = df.groupby("weekday")["amount"].sum().to_dict()
    # Приведём к float для сериализации
    result = {k: float(v) for k, v in result.items()}
    return json.dumps(result, ensure_ascii=False)


@log
def report_by_workday(df: pd.DataFrame, category: str, date_from: str) -> str:
    """
    Отчёт: траты по категории в рабочие и выходные дни за 3 месяца.
    :param df: DataFrame с транзакциями (ожидаются столбцы 'category', 'date', 'amount')
    :param category: категория трат
    :param date_from: дата отсчёта (строка в формате 'YYYY-MM-DD')
    :return: JSON-строка с расходами по рабочим и выходным дням
    """
    date_from_dt = datetime.strptime(date_from, "%Y-%m-%d")
    date_to_dt = date_from_dt + timedelta(days=90)
    df["date"] = pd.to_datetime(df["date"])
    mask = (df["category"] == category) & (df["date"] >= date_from_dt) & (df["date"] < date_to_dt)
    df_filtered = df.loc[mask].copy()
    df_filtered["is_workday"] = df_filtered["date"].dt.weekday < 5  # 0-4 — рабочие
    workday_sum = df_filtered[df_filtered["is_workday"]]["amount"].sum()
    weekend_sum = df_filtered[~df_filtered["is_workday"]]["amount"].sum()
    result = {
        "category": category,
        "period_start": date_from,
        "period_end": date_to_dt.strftime("%Y-%m-%d"),
        "workday_total": float(workday_sum),
        "weekend_total": float(weekend_sum),
    }
    return json.dumps(result, ensure_ascii=False)
