"""Nghiệp vụ đăng ký / hủy đăng ký (Buổi 3, 4). Dùng chung cho API và agent.

Bảo đảm theo đặc tả (spec.md):
  - Thứ tự báo lỗi: KHONG_CO_PHIEN → DA_DANG_KY → HET_CHO / QUA_SO_PHIEN.
  - Đếm và ghi trong MỘT câu lệnh INSERT … SELECT … WHERE: không còn khe hở khi nhiều người bấm cùng lúc.
  - UNIQUE(ma_sv, ma_phien) là lưới an toàn cuối cùng.
"""
import os
import sqlite3
import time
from datetime import datetime, timedelta

from . import config

HAN_HUY_GIO = 24   # Điều 4


class LoiNghiepVu(Exception):
    def __init__(self, ma: int, chi_tiet: str):
        self.ma, self.chi_tiet = ma, chi_tiet


def bay_gio() -> datetime:
    return datetime.fromisoformat(config.THOI_DIEM) if config.THOI_DIEM else datetime.now()


def con_cho(db: sqlite3.Connection, ma_phien: str) -> int:
    r = db.execute("SELECT suc_chua - (SELECT COUNT(*) FROM dang_ky WHERE ma_phien = p.ma_phien) "
                   "FROM phien p WHERE ma_phien = ?", (ma_phien,)).fetchone()
    if r is None:
        raise LoiNghiepVu(404, "KHONG_CO_PHIEN")
    return int(r[0])


def dang_ky(db: sqlite3.Connection, ma_sv: str, ma_phien: str) -> dict:
    ma_phien = ma_phien.strip().upper()
    con_cho(db, ma_phien)                                   # 404 nếu không có phiên
    if db.execute("SELECT 1 FROM dang_ky WHERE ma_sv = ? AND ma_phien = ?", (ma_sv, ma_phien)).fetchone():
        raise LoiNghiepVu(409, "DA_DANG_KY")
    if os.getenv("MO_PHONG_KHE_HO") == "1":        # CHỈ dùng trong thí nghiệm Bước 2: bản lỗi đếm-rồi-ghi
        return _dang_ky_co_khe_ho(db, ma_sv, ma_phien)
    try:
        cur = db.execute(
            """INSERT INTO dang_ky (ma_sv, ma_phien)
               SELECT ?, ?
               WHERE (SELECT COUNT(*) FROM dang_ky WHERE ma_phien = ?)
                     < (SELECT suc_chua FROM phien WHERE ma_phien = ?)
                 AND (SELECT COUNT(*) FROM dang_ky WHERE ma_sv = ?) < ?""",
            (ma_sv, ma_phien, ma_phien, ma_phien, ma_sv, config.TOI_DA_PHIEN))
    except sqlite3.IntegrityError:
        raise LoiNghiepVu(409, "DA_DANG_KY")
    if cur.rowcount == 0:
        so_phien = db.execute("SELECT COUNT(*) FROM dang_ky WHERE ma_sv = ?", (ma_sv,)).fetchone()[0]
        raise LoiNghiepVu(409, "QUA_SO_PHIEN" if so_phien >= config.TOI_DA_PHIEN else "HET_CHO")
    return {"ok": True, "ma_sv": ma_sv, "ma_phien": ma_phien}


def _dang_ky_co_khe_ho(db, ma_sv, ma_phien):
    """Bản SAI để thí nghiệm: đếm, (ngủ 50 ms phóng to khe hở), rồi mới ghi — vượt sức chứa khi đông người."""
    n = db.execute("SELECT COUNT(*) FROM dang_ky WHERE ma_phien = ?", (ma_phien,)).fetchone()[0]
    time.sleep(0.05)
    if n >= config.SUC_CHUA:
        raise LoiNghiepVu(409, "HET_CHO")
    try:
        db.execute("INSERT INTO dang_ky (ma_sv, ma_phien) VALUES (?, ?)", (ma_sv, ma_phien))
    except sqlite3.IntegrityError:
        raise LoiNghiepVu(409, "DA_DANG_KY")
    return {"ok": True, "ma_sv": ma_sv, "ma_phien": ma_phien}


def huy(db: sqlite3.Connection, ma_sv: str, ma_phien: str) -> dict:
    ma_phien = ma_phien.strip().upper()
    if not db.execute("SELECT 1 FROM dang_ky WHERE ma_sv = ? AND ma_phien = ?", (ma_sv, ma_phien)).fetchone():
        raise LoiNghiepVu(404, "KHONG_CO")                 # kiểm KHONG_CO trước QUA_HAN_HUY
    gio = db.execute("SELECT gio_bat_dau FROM phien WHERE ma_phien = ?", (ma_phien,)).fetchone()[0]
    if bay_gio() > datetime.fromisoformat(gio) - timedelta(hours=HAN_HUY_GIO):
        raise LoiNghiepVu(409, "QUA_HAN_HUY")
    db.execute("DELETE FROM dang_ky WHERE ma_sv = ? AND ma_phien = ?", (ma_sv, ma_phien))
    return {"ok": True}


def danh_sach_phien(db: sqlite3.Connection, ma_sv: str | None = None) -> list[dict]:
    rows = db.execute("""SELECT p.*, p.suc_chua - COUNT(d.ma_sv) AS con_cho,
                                MAX(d.ma_sv = ?) AS da_dang_ky
                         FROM phien p LEFT JOIN dang_ky d ON d.ma_phien = p.ma_phien
                         GROUP BY p.ma_phien ORDER BY p.gio_bat_dau, p.ma_phien""", (ma_sv or "",)).fetchall()
    return [{**dict(r), "da_dang_ky": bool(r["da_dang_ky"])} for r in rows]
