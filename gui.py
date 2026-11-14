
import tkinter as tk
from tkinter import ttk
import sys

from startup import get_pc_boot_time, get_app_start_time

from history import record_startup, load_recent_logs

from single_instance import (
    acquire_single_instance,
    minimize_if_unfocused
)


def create_app():

    root = tk.Tk()

    # ウィンドウの基本設定
    root.title("PC Startup Logger")
    root.geometry("520x420")
    root.resizable(False, False)

    # ウィンドウを中央に配置
    root.update_idletasks()

    x = (root.winfo_screenwidth() - 520) // 2
    y = (root.winfo_screenheight() - 420) // 2

    root.geometry(f"520x420+{x}+{y}")

    # 最前面に表示
    root.attributes("-topmost", True)

    # PC起動日時とアプリ起動日時を取得
    boot_time = get_pc_boot_time()
    app_time = get_app_start_time()

    # CSVに起動日時を保存
    is_new_record = record_startup(
        boot_time,
        app_time
    )

    # タイトル
    title = ttk.Label(
        root,
        text="PC Startup Logger",
        font=("Yu Gothic UI", 18, "bold")
    )
    title.pack(pady=(25, 15))

    # PC起動日時表示エリア
    current_frame = ttk.LabelFrame(
        root,
        text="今回のPC起動日時",
        padding=15
    )
    current_frame.pack(
        fill="x",
        padx=25,
        pady=10
    )

    boot_time_label = ttk.Label(
        current_frame,
        text=boot_time.strftime("%Y-%m-%d %H:%M:%S"),
        font=("Yu Gothic UI", 16, "bold")
    )
    boot_time_label.pack()

    # アプリ起動日時
    app_time_label = ttk.Label(
        root,
        text="アプリ起動日時: "
        + app_time.strftime("%Y-%m-%d %H:%M:%S"),
        font=("Yu Gothic UI", 9)
    )
    app_time_label.pack(pady=5)

    # 履歴表示エリア
    history_frame = ttk.LabelFrame(
        root,
        text="直近7日間の起動履歴",
        padding=10
    )
    history_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=10
    )

    # 履歴テーブル
    columns = ("date", "time")

    tree = ttk.Treeview(
        history_frame,
        columns=columns,
        show="headings",
        height=7
    )

    tree.heading("date", text="日付")
    tree.heading("time", text="起動時刻")

    tree.column(
        "date",
        width=200,
        anchor="center"
    )

    tree.column(
        "time",
        width=200,
        anchor="center"
    )

    tree.pack(
        fill="both",
        expand=True
    )

    # CSVから直近7日間の履歴を取得
    logs = load_recent_logs(days=7)

    # テーブルに履歴を表示
    for log in logs:

        tree.insert(
            "",
            "end",
            values=(
                log["date"],
                log["time"]
            )
        )

    # ステータス表示
    if is_new_record:
        status_text = "新しいPC起動履歴を保存しました"
    else:
        status_text = "今回のPC起動履歴は登録済みです"

    status_label = ttk.Label(
        root,
        text=status_text,
        font=("Yu Gothic UI", 9)
    )

    status_label.pack(
        pady=(0, 12)
    )

    # フォーカスが外れた場合の処理
    def on_focus_out(event):

        # 150ミリ秒後に状態を再確認
        root.after(
            150,
            lambda: minimize_if_unfocused(root)
        )

    root.bind(
        "<FocusOut>",
        on_focus_out
    )

    return root


if __name__ == "__main__":

    # 二重起動チェック
    if not acquire_single_instance():
        sys.exit(0)

    # アプリ起動
    app = create_app()

    app.mainloop()
