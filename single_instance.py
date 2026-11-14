
import ctypes
import time
from ctypes import wintypes


# Windows APIの読み込み
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
user32 = ctypes.WinDLL("user32", use_last_error=True)


# Mutexのハンドルを保持
_mutex_handle = None

# アプリのウィンドウタイトル
WINDOW_TITLE = "PC Startup Logger"

# Windows API定数
ERROR_ALREADY_EXISTS = 183
SW_RESTORE = 9
GA_ROOT = 2

HWND_TOPMOST = wintypes.HWND(-1)

SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_SHOWWINDOW = 0x0040


# APIの引数・戻り値の型を定義
kernel32.CreateMutexW.argtypes = [
    wintypes.LPVOID,
    wintypes.BOOL,
    wintypes.LPCWSTR
]
kernel32.CreateMutexW.restype = wintypes.HANDLE

kernel32.CloseHandle.argtypes = [
    wintypes.HANDLE
]
kernel32.CloseHandle.restype = wintypes.BOOL

user32.FindWindowW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.LPCWSTR
]
user32.FindWindowW.restype = wintypes.HWND

user32.ShowWindow.argtypes = [
    wintypes.HWND,
    ctypes.c_int
]
user32.ShowWindow.restype = wintypes.BOOL

user32.SetForegroundWindow.argtypes = [
    wintypes.HWND
]
user32.SetForegroundWindow.restype = wintypes.BOOL

user32.GetForegroundWindow.restype = wintypes.HWND

user32.GetAncestor.argtypes = [
    wintypes.HWND,
    wintypes.UINT
]
user32.GetAncestor.restype = wintypes.HWND

user32.SetWindowPos.argtypes = [
    wintypes.HWND,
    wintypes.HWND,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.UINT
]
user32.SetWindowPos.restype = wintypes.BOOL


def acquire_single_instance():
    """
    Mutexを利用して二重起動を防止する。
    """

    global _mutex_handle

    mutex_name = "Local\\PCStartupLogger_Mutex"

    # 前回のAPI呼び出しのエラー情報をクリア
    ctypes.set_last_error(0)

    handle = kernel32.CreateMutexW(
        None,
        True,
        mutex_name
    )

    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())

    # Mutexがすでに存在する場合
    if ctypes.get_last_error() == ERROR_ALREADY_EXISTS:

        kernel32.CloseHandle(handle)

        activate_existing_window()

        return False

    # プロセス終了までハンドルを保持
    _mutex_handle = handle

    return True


def activate_existing_window():
    """
    既存のウィンドウを検索して前面に表示する。
    """

    for _ in range(20):

        hwnd = user32.FindWindowW(
            None,
            WINDOW_TITLE
        )

        if hwnd:

            # 最小化されていれば復元
            user32.ShowWindow(
                hwnd,
                SW_RESTORE
            )

            # 最前面に設定
            user32.SetWindowPos(
                hwnd,
                HWND_TOPMOST,
                0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
            )

            # フォーカスを移動
            user32.SetForegroundWindow(hwnd)

            return

        time.sleep(0.1)


def minimize_if_unfocused(root):
    """
    別のアプリにフォーカスが移った場合、
    自分のウィンドウを最小化する。
    """

    if not root.winfo_exists():
        return

    # 現在アクティブなウィンドウを取得
    foreground = user32.GetForegroundWindow()

    # 自分のウィンドウのルートハンドルを取得
    own_window = user32.GetAncestor(
        root.winfo_id(),
        GA_ROOT
    )

    # アクティブウィンドウのルートハンドルを取得
    foreground_root = None

    if foreground:
        foreground_root = user32.GetAncestor(
            foreground,
            GA_ROOT
        )

    # 自分のアプリ以外がアクティブなら最小化
    if foreground_root != own_window:

        root.attributes("-topmost", False)

        root.iconify()
