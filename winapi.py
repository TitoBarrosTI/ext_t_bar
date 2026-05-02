# winapi.py
import ctypes
import ctypes.wintypes
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt

user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32

def get_scale_factor() -> float:
    hdc = ctypes.windll.gdi32.CreateDCW("DISPLAY", None, None, None)
    dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)
    ctypes.windll.gdi32.DeleteDC(hdc)
    return dpi / 96.0

def get_taskbar_rect() -> ctypes.wintypes.RECT:
    hwnd = user32.FindWindowW("Shell_TrayWnd", None)
    rect = ctypes.wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    scale = get_scale_factor()
    rect.left   = int(rect.left   / scale)
    rect.top    = int(rect.top    / scale)
    rect.right  = int(rect.right  / scale)
    rect.bottom = int(rect.bottom / scale)
    return rect

def extract_icon(exe_path: str, size: int = 32) -> QPixmap | None:
    hicon_large = ctypes.c_void_p(0)
    hicon_small = ctypes.c_void_p(0)

    count = shell32.ExtractIconExW(
        exe_path, 0,
        ctypes.byref(hicon_large),
        ctypes.byref(hicon_small),
        1
    )

    if count == 0:
        return None

    hicon = hicon_large if hicon_large.value else hicon_small
    if not hicon.value:
        return None

    pixmap = _hicon_to_pixmap(hicon.value, size)

    user32.DestroyIcon(hicon_large)
    user32.DestroyIcon(hicon_small)

    return pixmap

def _hicon_to_pixmap(hicon: int, size: int) -> QPixmap | None:
    hdc_screen = ctypes.windll.gdi32.CreateDCW("DISPLAY", None, None, None)
    hdc_mem    = ctypes.windll.gdi32.CreateCompatibleDC(hdc_screen)

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [
            ("biSize",          ctypes.c_uint32),
            ("biWidth",         ctypes.c_int32),
            ("biHeight",        ctypes.c_int32),
            ("biPlanes",        ctypes.c_uint16),
            ("biBitCount",      ctypes.c_uint16),
            ("biCompression",   ctypes.c_uint32),
            ("biSizeImage",     ctypes.c_uint32),
            ("biXPelsPerMeter", ctypes.c_int32),
            ("biYPelsPerMeter", ctypes.c_int32),
            ("biClrUsed",       ctypes.c_uint32),
            ("biClrImportant",  ctypes.c_uint32),
        ]

    bmi = BITMAPINFOHEADER()
    bmi.biSize        = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.biWidth       = size
    bmi.biHeight      = -size  # negativo = top-down
    bmi.biPlanes      = 1
    bmi.biBitCount    = 32
    bmi.biCompression = 0

    bits = ctypes.c_void_p(0)
    hbmp = ctypes.windll.gdi32.CreateDIBSection(
        hdc_mem, ctypes.byref(bmi), 0,
        ctypes.byref(bits), None, 0
    )

    old_bmp = ctypes.windll.gdi32.SelectObject(hdc_mem, hbmp)
    ctypes.windll.user32.DrawIconEx(
        hdc_mem, 0, 0, hicon, size, size, 0, None, 3
    )

    buf = (ctypes.c_byte * (size * size * 4))()
    ctypes.windll.gdi32.GetBitmapBits(hbmp, size * size * 4, buf)

    ctypes.windll.gdi32.SelectObject(hdc_mem, old_bmp)
    ctypes.windll.gdi32.DeleteObject(hbmp)
    ctypes.windll.gdi32.DeleteDC(hdc_mem)
    ctypes.windll.gdi32.DeleteDC(hdc_screen)

    img = QImage(bytes(buf), size, size, QImage.Format.Format_ARGB32)
    return QPixmap.fromImage(img)

def create_mutex(name: str) -> ctypes.c_void_p:
    handle = ctypes.windll.kernel32.CreateMutexW(None, True, name)
    return handle

def is_already_running(name: str) -> bool:
    ERROR_ALREADY_EXISTS = 183
    handle = create_mutex(name)
    return ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS