import csv
from datetime import datetime

import requests


def fetch_bybit_data():
    url = "https://api.bybit.com/v5/market/kline"
    params = {
        "category": "spot",  # "linear" для фьючерсов
        "symbol": "BTCUSDT",
        "interval": "60",  # Варианты: 1,3,5,15,30,60,120,240,D,W,M
        "limit": 1000,  # Максимум 1000 свечей
    }

    try:
        print("Запрос данных с Bybit API...")
        response = requests.get(url, params=params)
        response.raise_for_status()  # Проверка ошибок HTTP

        data = response.json()

        if data["retCode"] != 0:
            raise Exception(f"API Error: {data['retMsg']}")

        klines = data["result"]["list"]

        # Преобразуем timestamp и сортируем от старых к новым
        formatted_data = []
        for k in reversed(klines):
            timestamp = datetime.fromtimestamp(int(k[0]) / 1000).strftime("%Y-%m-%d %H:%M:%S")
            formatted_data.append(
                [
                    timestamp,
                    float(k[1]),  # Open
                    float(k[2]),  # High
                    float(k[3]),  # Low
                    float(k[4]),  # Close
                    float(k[5]),  # Volume
                    float(k[6]),  # Turnover
                ]
            )

        # Сохраняем в CSV
        filename = f"bybit_{params['symbol']}_{params['interval']}.csv"
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Open", "High", "Low", "Close", "Volume", "Turnover"])
            writer.writerows(formatted_data)

        print(f"Данные сохранены в {filename}")
        print(f"Получено {len(formatted_data)} записей")

        return filename

    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return None


# Запуск функции
if __name__ == "__main__":
    fetch_bybit_data()
