"""Cho phép chạy các script trong scripts/ từ thư mục gốc dự án: python scripts/<ten>.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
