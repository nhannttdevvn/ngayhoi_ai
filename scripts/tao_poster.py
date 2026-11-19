"""Tạo poster Ngày hội: nền tạo lại được (seed) + lớp chữ đúng từng dấu + kiểm tra (Buổi 10)."""
import sys

import _goc  # noqa: F401
from app import poster

if __name__ == "__main__":
    kq = poster.tao(int(sys.argv[1]) if len(sys.argv) > 1 else 48213)
    for k, v in kq.items():
        print(f"{k}: {v}")
