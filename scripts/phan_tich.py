"""Hồ sơ dữ liệu, ba chỉ số có tên riêng và biểu đồ theo phiên (Buổi 8)."""
import _goc  # noqa: F401
from app import db, phan_tich

if __name__ == "__main__":
    k = db.ket_noi()
    for ten, ds in phan_tich.ho_so(k).items():
        print(f"[{ten}] {len(ds)} dòng:", "; ".join("·".join(map(str, d.values())) for d in ds))
    for ten, v in phan_tich.chi_so(k).items():
        print(f"{ten:22} {v['gia_tri']:5.1f}%  — {v['dinh_nghia']}")
    print("Biểu đồ:", phan_tich.ve_bieu_do(k))
