"""Thí nghiệm đồng thời (Buổi 4): N sinh viên KHÁC NHAU, chưa đăng ký phiên đó, bấm đăng ký cùng một lúc.
Chạy khi máy chủ đang chạy:  python scripts/ban_dong_thoi.py P10 40
Kỳ vọng: số 201 đúng bằng số chỗ còn lại trước thí nghiệm; phần còn lại nhận 409 HET_CHO."""
import sqlite3
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

import httpx

import _goc  # noqa: F401
from app import config

URL = "http://localhost:8000"
PHIEN = sys.argv[1] if len(sys.argv) > 1 else "P10"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 40


def chon_sinh_vien():
    """Chọn N sinh viên chưa đăng ký PHIEN và còn dưới 3 phiên — để mọi từ chối chỉ do hết chỗ."""
    k = sqlite3.connect(config.DB_PATH)
    return [r[0] for r in k.execute(
        """SELECT s.ma_sv FROM sinh_vien s WHERE s.ma_sv NOT IN (SELECT ma_sv FROM dang_ky WHERE ma_phien = ?)
           AND (SELECT COUNT(*) FROM dang_ky d WHERE d.ma_sv = s.ma_sv) < ? ORDER BY s.ma_sv LIMIT ?""",
        (PHIEN, config.TOI_DA_PHIEN, N))]


def gui(ma):
    r = httpx.post(f"{URL}/api/dang-ky", json={"ma_phien": PHIEN}, headers={"X-Ma-SV": ma}, timeout=30)
    return f"{r.status_code} {r.json().get('detail', '')}".strip()


if __name__ == "__main__":
    ds = chon_sinh_vien()
    truoc = httpx.get(f"{URL}/api/con-cho", params={"ma_phien": PHIEN}).json()["con_cho"]
    with ThreadPoolExecutor(max_workers=len(ds)) as ex:
        dem = Counter(ex.map(gui, ds))
    sau = httpx.get(f"{URL}/api/con-cho", params={"ma_phien": PHIEN}).json()["con_cho"]
    print(f"Phiên {PHIEN}: còn {truoc} chỗ · {len(ds)} sinh viên bấm cùng lúc → {dict(dem)} · còn {sau} chỗ sau")
    print("ĐẠT: không vượt sức chứa" if sau >= 0 and dem["201"] == truoc else f"KHÔNG ĐẠT: vượt sức chứa ({-sau} người)")
