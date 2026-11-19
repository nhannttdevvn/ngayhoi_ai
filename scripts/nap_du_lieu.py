"""Nạp (lại) 4 tệp CSV trong data/ vào cơ sở dữ liệu. Xóa đăng ký phát sinh khi thử nghiệm."""
import _goc  # noqa: F401
from app import db

if __name__ == "__main__":
    k = db.ket_noi()
    k.execute("DELETE FROM da_cong"); k.execute("DELETE FROM hanh_dong_cho")
    print(db.nap_csv(k))
