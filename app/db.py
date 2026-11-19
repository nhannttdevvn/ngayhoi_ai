"""Cơ sở dữ liệu SQLite: lược đồ, nạp dữ liệu CSV (Buổi 3, 4, 8, 9)."""
import csv
import sqlite3

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS sinh_vien(ma_sv TEXT PRIMARY KEY, ho_ten TEXT, lop TEXT);
CREATE TABLE IF NOT EXISTS phien(ma_phien TEXT PRIMARY KEY, chu_de TEXT, doanh_nghiep TEXT,
    linh_vuc TEXT, gio_bat_dau TEXT, phong TEXT, suc_chua INTEGER);
CREATE TABLE IF NOT EXISTS dang_ky(ma_sv TEXT, ma_phien TEXT, thoi_diem TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ma_sv, ma_phien));
CREATE TABLE IF NOT EXISTS diem_danh(ma_sv TEXT, ma_phien TEXT, phut_tre TEXT);
CREATE TABLE IF NOT EXISTS da_cong(ma_sv TEXT PRIMARY KEY, diem INTEGER, ngay TEXT);
CREATE TABLE IF NOT EXISTS hanh_dong_cho(id TEXT PRIMARY KEY, ma_sv TEXT, cong_cu TEXT,
    tham_so TEXT, tao_luc TEXT DEFAULT CURRENT_TIMESTAMP, trang_thai TEXT DEFAULT 'cho');
"""

def ket_noi(path: str | None = None) -> sqlite3.Connection:
    """Mỗi yêu cầu một kết nối; isolation_level=None: mỗi câu lệnh tự commit (nguyên tử)."""
    db = sqlite3.connect(path or config.DB_PATH, check_same_thread=False, isolation_level=None, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=15000")
    db.executescript(SCHEMA)
    return db


def nap_csv(db: sqlite3.Connection, xoa_cu: bool = True) -> dict:
    """Nạp 4 tệp CSV trong data/ vào cơ sở dữ liệu. Trả về số dòng mỗi bảng."""
    so = {}
    for bang in ["sinh_vien", "phien", "dang_ky", "diem_danh"]:
        with open(config.DATA / f"{bang}.csv", encoding="utf-8") as f:
            r = list(csv.DictReader(f))
        if xoa_cu:
            db.execute(f"DELETE FROM {bang}")
        cot = list(r[0].keys())
        db.executemany(f"INSERT OR IGNORE INTO {bang} ({','.join(cot)}) VALUES ({','.join('?' * len(cot))})",
                       [tuple(d[c] for c in cot) for d in r])
        so[bang] = db.execute(f"SELECT COUNT(*) FROM {bang}").fetchone()[0]
    return so
