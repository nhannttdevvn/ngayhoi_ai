"""Pha chuẩn bị của RAG: cắt quy chế theo Điều, nhúng, lưu out/chi_muc.json. Chạy lại mỗi khi sửa quy chế."""
import _goc  # noqa: F401
from app import rag

if __name__ == "__main__":
    kq = rag.xay_chi_muc()
    print(f"Đã nhúng {kq['so_doan']} đoạn · chế độ {kq['che_do']} · {kq['so_chieu']} chiều")
