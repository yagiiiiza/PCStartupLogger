
import csv
import os
from pathlib import Path
from datetime import datetime, timedelta


# CSVの保存先
APP_DATA = Path(os.environ["APPDATA"])

DATA_DIR = APP_DATA / "PCStartupLogger"

CSV_PATH = DATA_DIR / "startup_history.csv"


# CSVの列名
FIELDNAMES = [
    "PC起動日時",
    "アプリ記録日時"
]


def initialize_csv():
    """
    保存先フォルダとCSVファイルを初期化する
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not CSV_PATH.exists() or CSV_PATH.stat().st_size == 0:

        with open(
            CSV_PATH,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=FIELDNAMES
            )

            writer.writeheader()


def record_startup(boot_time, app_time):
    """
    PC起動日時をCSVに保存する
    同じ起動日時が存在する場合は登録しない
    """

    initialize_csv()

    boot_time_str = boot_time.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    app_time_str = app_time.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # 既存データを確認
    with open(
        CSV_PATH,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if row["PC起動日時"] == boot_time_str:
                return False

    # 新しい起動日時を追加
    with open(
        CSV_PATH,
        "a",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDNAMES
        )

        writer.writerow({
            "PC起動日時": boot_time_str,
            "アプリ記録日時": app_time_str
        })

    return True


def load_recent_logs(days=7):
    """
    直近7日間のPC起動履歴を取得する
    """

    initialize_csv()

    logs = []

    # 今日を含む直近7日間
    start_date = datetime.now().date() - timedelta(
        days=days - 1
    )

    with open(
        CSV_PATH,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            try:
                boot_time = datetime.strptime(
                    row["PC起動日時"],
                    "%Y-%m-%d %H:%M:%S"
                )

                if boot_time.date() >= start_date:

                    logs.append({
                        "date": boot_time.strftime(
                            "%Y-%m-%d"
                        ),
                        "time": boot_time.strftime(
                            "%H:%M:%S"
                        )
                    })

            except (ValueError, KeyError, TypeError):
                continue

    # 新しい履歴を上に表示
    logs.sort(
        key=lambda log: (
            log["date"],
            log["time"]
        ),
        reverse=True
    )

    return logs
