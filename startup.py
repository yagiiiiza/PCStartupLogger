
import psutil
from datetime import datetime


def get_pc_boot_time():
    """
    WindowsのOS起動日時を取得する
    """

    # OS起動時刻を取得
    timestamp = psutil.boot_time()

    # Unixタイムスタンプを日本時間の日時に変換
    boot_datetime = datetime.fromtimestamp(timestamp)

    return boot_datetime


def get_app_start_time():
    """
    アプリケーションの起動日時を取得する
    """

    return datetime.now()


if __name__ == "__main__":

    boot_time = get_pc_boot_time()
    app_time = get_app_start_time()

    print("PC起動日時:", boot_time.strftime("%Y-%m-%d %H:%M:%S"))
    print("アプリ起動日時:", app_time.strftime("%Y-%m-%d %H:%M:%S"))
