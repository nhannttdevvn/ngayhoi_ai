"""Cấu hình đọc từ biến môi trường (xem .env.example). Không ghi bí mật trong mã nguồn."""
import os
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
DATA = Path(os.getenv("DATA_DIR", GOC / "data"))
OUT = Path(os.getenv("OUT_DIR", GOC / "out"))          # tệp sinh ra: chỉ mục, biểu đồ, nhật ký, poster
OUT.mkdir(parents=True, exist_ok=True)

DB_PATH = os.getenv("DB_PATH", str(OUT / "ngayhoi.db"))
SUC_CHUA = int(os.getenv("SUC_CHUA", "30"))             # Điều 3
TOI_DA_PHIEN = int(os.getenv("TOI_DA_PHIEN", "3"))      # Điều 3
PHUT_TRE_TOI_DA = int(os.getenv("PHUT_TRE_TOI_DA", "10"))  # Điều 5
SO_PHIEN_CONG_DIEM = int(os.getenv("SO_PHIEN_CONG_DIEM", "2"))  # Điều 6
DIEM_CONG = int(os.getenv("DIEM_CONG", "5"))            # Điều 6

# Mô hình ngôn ngữ chạy cục bộ (Buổi 1, 6, 7). LLM_MODE: auto | ollama | offline
LLM_MODE = os.getenv("LLM_MODE", "auto")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MO_HINH_SINH = os.getenv("MO_HINH_SINH", "qwen2.5:3b")
MO_HINH_NHUNG = os.getenv("MO_HINH_NHUNG", "bge-m3")
# Ngưỡng từ chối phải ĐO trên dữ liệu (scripts/danh_gia_rag.py); mỗi bộ nhúng một ngưỡng
NGUONG_OLLAMA = float(os.getenv("NGUONG_OLLAMA", "0.45"))
NGUONG_OFFLINE = float(os.getenv("NGUONG_OFFLINE", "0.37"))
TOP_K = int(os.getenv("TOP_K", "3"))
SO_VONG_AGENT = int(os.getenv("SO_VONG_AGENT", "5"))

# Xác thực: demo (chọn mã SV, chỉ dùng khi học/thử nghiệm) | header (đứng sau cổng SSO, đọc X-Remote-User)
AUTH_MODE = os.getenv("AUTH_MODE", "demo")
ADMIN_KEY = os.getenv("ADMIN_KEY", "")                  # bắt buộc đặt khi triển khai
ADMIN_GROUP = os.getenv("ADMIN_GROUP", "ctsv-admin")
ALLOWED_ORIGINS = [o for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if o]
# Thời điểm "hiện tại" giả lập (ISO), chỉ dùng khi demo/kiểm thử quy tắc hủy 24 giờ; để trống khi vận hành
THOI_DIEM = os.getenv("THOI_DIEM", "")
