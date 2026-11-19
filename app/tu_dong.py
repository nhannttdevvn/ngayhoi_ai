"""Tự động cộng điểm rèn luyện (Buổi 9): chạy lại an toàn, ngoại lệ vào hàng đợi, có nhật ký.

Quy tắc (Điều 5, 6): tham dự ĐÚNG GIỜ (muộn ≤ 10 phút) từ 2 phiên ĐÃ ĐĂNG KÝ trở lên → +5 điểm.
Mọi dòng điểm danh ra ở một trong hai nơi: danh sách đủ điều kiện, hoặc hàng đợi ngoại lệ (kèm lý do).
"""
import csv
import sqlite3
from datetime import datetime

from . import config

DU_DIEU_KIEN = f"""
SELECT d.ma_sv
  FROM diem_danh d JOIN dang_ky k ON k.ma_sv = d.ma_sv AND k.ma_phien = UPPER(d.ma_phien)
 WHERE TRIM(d.phut_tre) <> '' AND CAST(d.phut_tre AS INTEGER) <= {config.PHUT_TRE_TOI_DA}   -- Điều 5
 GROUP BY d.ma_sv
HAVING COUNT(DISTINCT UPPER(d.ma_phien)) >= {config.SO_PHIEN_CONG_DIEM}                   -- Điều 6
 ORDER BY d.ma_sv"""

NGOAI_LE = """
SELECT d.ma_sv, UPPER(d.ma_phien) AS ma_phien,
       CASE WHEN k.ma_sv IS NULL THEN 'KHONG_DANG_KY' ELSE 'THIEU_GIO' END AS ly_do
  FROM diem_danh d LEFT JOIN dang_ky k ON k.ma_sv = d.ma_sv AND k.ma_phien = UPPER(d.ma_phien)
 WHERE k.ma_sv IS NULL OR TRIM(COALESCE(d.phut_tre, '')) = ''"""


def chay(db: sqlite3.Connection) -> dict:
    hom_nay = datetime.now().strftime("%Y-%m-%d")
    du = [r[0] for r in db.execute(DU_DIEU_KIEN)]
    moi = 0
    for sv in du:   # khóa chính ma_sv + INSERT OR IGNORE: chạy lại không cộng hai lần
        moi += db.execute("INSERT OR IGNORE INTO da_cong VALUES (?, ?, ?)", (sv, config.DIEM_CONG, hom_nay)).rowcount
    ngoai_le = [dict(r) for r in db.execute(NGOAI_LE)]

    with open(config.OUT / "cong_diem.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["ma_sv", "diem", "can_cu"])
        w.writerows([[sv, config.DIEM_CONG, "Điều 6"] for sv in du])
    with open(config.OUT / "ngoai_le.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["ma_sv", "ma_phien", "ly_do"]); w.writeheader(); w.writerows(ngoai_le)
    dong = f"{datetime.now():%Y-%m-%d %H:%M:%S} du={len(du)} moi={moi} ngoai_le={len(ngoai_le)}"
    with open(config.OUT / "nhat_ky_cong_diem.txt", "a", encoding="utf-8") as f:
        f.write(dong + "\n")
    return {"du_dieu_kien": len(du), "cong_moi": moi, "da_cong_truoc": len(du) - moi,
            "ngoai_le": ngoai_le, "nhat_ky": dong}
