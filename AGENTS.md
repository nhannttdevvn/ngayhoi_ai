# Hệ thống Ngày hội việc làm tích hợp AI — quy tắc cho người và agent

## Cấu trúc
- app/: máy chủ FastAPI (main.py), nghiệp vụ đăng ký (dang_ky.py), RAG (rag.py), agent (agent.py),
  phân tích (phan_tich.py), tự động hóa (tu_dong.py), poster (poster.py)
- web/: giao diện HTML/JS thuần — không sửa khi làm việc ở app/
- data/: dữ liệu và quy chế — chỉ người phụ trách được sửa
- scripts/: công cụ dòng lệnh; tests/: pytest

## Chạy test
python -m pytest -q   (đứng ở thư mục gốc; không cần Ollama)

## Không được sửa
- tests/ và spec.md (chỉ người sửa)
- .github/ (cổng CI), data/quy_che.md

## Xong việc nghĩa là
- pytest xanh trên CI; PR dưới 200 dòng, một ý; mô tả theo mẫu 5 mục
- không ghép chuỗi vào SQL (chỉ dùng dấu ?); không ghi bí mật vào mã
