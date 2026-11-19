"""Phân tích dữ liệu có kiểm chứng (Buổi 8). Định nghĩa chỉ số: docs/chi_so.md."""
import sqlite3

from . import config

HO_SO = {  # 4 phép kiểm hồ sơ dữ liệu
    "trung": """SELECT ma_sv, UPPER(ma_phien) AS ma_phien, COUNT(*) AS so_lan FROM diem_danh
                GROUP BY ma_sv, UPPER(ma_phien) HAVING COUNT(*) > 1""",
    "khong_chuan": "SELECT ma_sv, ma_phien FROM diem_danh WHERE ma_phien <> UPPER(ma_phien)",
    "trong": "SELECT ma_sv, ma_phien FROM diem_danh WHERE TRIM(COALESCE(phut_tre, '')) = ''",
    "nguoi_la": """SELECT d.ma_sv, UPPER(d.ma_phien) AS ma_phien FROM diem_danh d LEFT JOIN dang_ky k
                   ON k.ma_sv = d.ma_sv AND k.ma_phien = UPPER(d.ma_phien) WHERE k.ma_sv IS NULL""",
}

# Ba định nghĩa có tên riêng — không gọi chung là "tỷ lệ tham dự"
CHI_SO = {
    "TL_LUOT_CO_QUET": ("Lượt đăng ký có ≥ 1 lần quét (bỏ trùng, chuẩn hóa chữ hoa, loại người lạ) ÷ lượt đăng ký",
        """SELECT COUNT(DISTINCT d.ma_sv || '|' || UPPER(d.ma_phien)) * 100.0 / (SELECT COUNT(*) FROM dang_ky)
           FROM diem_danh d JOIN dang_ky k ON k.ma_sv = d.ma_sv AND k.ma_phien = UPPER(d.ma_phien)"""),
    "TL_LUOT_DUNG_GIO": ("Lượt có quét và đến muộn ≤ 10 phút (Điều 5; ô trống tính vắng) ÷ lượt đăng ký — dùng xét điểm rèn luyện",
        f"""SELECT COUNT(DISTINCT d.ma_sv || '|' || UPPER(d.ma_phien)) * 100.0 / (SELECT COUNT(*) FROM dang_ky)
            FROM diem_danh d JOIN dang_ky k ON k.ma_sv = d.ma_sv AND k.ma_phien = UPPER(d.ma_phien)
            WHERE TRIM(d.phut_tre) <> '' AND CAST(d.phut_tre AS INTEGER) <= {config.PHUT_TRE_TOI_DA}"""),
    "TL_SINH_VIEN_CO_DEN": ("Sinh viên có quét ít nhất một phiên đã đăng ký ÷ sinh viên đã đăng ký",
        """SELECT COUNT(DISTINCT d.ma_sv) * 100.0 / (SELECT COUNT(DISTINCT ma_sv) FROM dang_ky)
           FROM diem_danh d JOIN dang_ky k ON k.ma_sv = d.ma_sv AND k.ma_phien = UPPER(d.ma_phien)"""),
}

THEO_PHIEN = """SELECT k.ma_phien, COUNT(*) AS n,
       COUNT(DISTINCT CASE WHEN d.ma_sv IS NOT NULL THEN k.ma_sv END) AS co_quet
  FROM dang_ky k LEFT JOIN (SELECT DISTINCT ma_sv, UPPER(ma_phien) AS ma_phien FROM diem_danh) d
    ON d.ma_sv = k.ma_sv AND d.ma_phien = k.ma_phien
 GROUP BY k.ma_phien ORDER BY k.ma_phien"""


def ho_so(db: sqlite3.Connection) -> dict:
    return {k: [dict(r) for r in db.execute(q)] for k, q in HO_SO.items()}


def chi_so(db: sqlite3.Connection) -> dict:
    return {k: {"dinh_nghia": d, "gia_tri": round(db.execute(q).fetchone()[0] or 0, 1)} for k, (d, q) in CHI_SO.items()}


def theo_phien(db: sqlite3.Connection) -> list[dict]:
    return [{**dict(r), "ty_le": round(r["co_quet"] * 100 / r["n"], 1)} for r in db.execute(THEO_PHIEN)]


def ve_bieu_do(db: sqlite3.Connection, tep=None) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    tep = tep or config.OUT / "bieu_do_ty_le.png"
    ds = theo_phien(db)
    fig, ax = plt.subplots(figsize=(10, 4.6), dpi=150)
    x = range(len(ds))
    ax.bar(x, [d["ty_le"] for d in ds], color="#1f4e79")
    for i, d in enumerate(ds):
        ax.text(i, d["ty_le"] + 1.5, f"{d['ty_le']:.0f}%", ha="center", fontsize=9)
    ax.set_xticks(list(x), [f"{d['ma_phien']}\nn={d['n']}" for d in ds], fontsize=9)
    ax.set_ylim(0, 100)                                   # trục từ 0
    ax.set_ylabel("%")
    ax.set_title("Tỷ lệ lượt đăng ký có quét mã, theo phiên", loc="left", fontsize=12, fontweight="bold")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.text(0.01, 0.01, "Định nghĩa: lượt có ≥ 1 lần quét, bỏ trùng, chuẩn hóa mã phiên, loại người không đăng ký "
             "÷ lượt đăng ký của phiên · n = số lượt đăng ký · Nguồn: dang_ky.csv, diem_danh.csv", fontsize=8, color="#444")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(tep)
    plt.close(fig)
    return str(tep)
