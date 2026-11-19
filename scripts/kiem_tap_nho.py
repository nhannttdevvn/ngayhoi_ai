"""Kiểm câu SQL tính tỷ lệ trên TẬP NHỎ có đáp án tính tay (Buổi 8) trước khi tin nó trên dữ liệu thật.
Tập nhỏ: dang_ky A,B,C,D (P01); diem_danh (A,P01,0),(A,P01,0),(B,p01,2),(E,P01,0) → đáp án 50%."""
import sqlite3

import _goc  # noqa: F401
from app.phan_tich import CHI_SO

SQL_AI_BAN_DAU = "SELECT COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dang_ky) FROM diem_danh"

if __name__ == "__main__":
    m = sqlite3.connect(":memory:")
    m.executescript("""CREATE TABLE dang_ky(ma_sv, ma_phien); CREATE TABLE diem_danh(ma_sv, ma_phien, phut_tre);
        INSERT INTO dang_ky VALUES ('A','P01'),('B','P01'),('C','P01'),('D','P01');
        INSERT INTO diem_danh VALUES ('A','P01','0'),('A','P01','0'),('B','p01','2'),('E','P01','0');""")
    print("Đáp án tính tay      : 50.0")
    print("SQL bản đầu của AI   :", m.execute(SQL_AI_BAN_DAU).fetchone()[0])
    print("SQL TL_LUOT_CO_QUET  :", m.execute(CHI_SO["TL_LUOT_CO_QUET"][1]).fetchone()[0])
