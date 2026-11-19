# Triển khai trong hệ thống của Nhà trường

## 1. Điều kiện bắt buộc trước khi vận hành chính thức
1. Xác thực: đặt AUTH_MODE=header; đặt ứng dụng sau cổng SSO của Nhà trường (ví dụ reverse proxy có xác thực
   Microsoft 365/Google Workspace), cổng điền tiêu đề X-Remote-User (mã SV) và X-Remote-Groups (nhóm quyền).
   Không mở cổng 8000 ra Internet; chế độ demo chỉ dùng cho học tập.
2. HTTPS tại reverse proxy; ADMIN_KEY ngẫu nhiên ≥ 32 ký tự lưu trong kho bí mật, không trong mã.
3. Dữ liệu thật: thay data/*.csv bằng dữ liệu xuất từ hệ thống quản lý đào tạo và máy quét QR (giữ nguyên tên cột);
   chạy python scripts/nap_du_lieu.py. Quy chế thật thay data/quy_che.md (giữ tiêu đề dạng "## Điều n.").
4. Bảo vệ dữ liệu cá nhân: tuân thủ Nghị định 13/2023/NĐ-CP; thông báo mục đích xử lý; thời hạn lưu theo Điều 9 quy chế;
   phân quyền xem thống kê, ngoại lệ cho Phòng CTSV.
5. Mô hình: chạy Ollama trên máy chủ nội bộ (docker-compose.yml); đo lại ngưỡng bằng scripts/danh_gia_rag.py
   với câu hỏi vàng do Phòng CTSV soạn; giữ cổng xác nhận của agent.

## 2. Vận hành
- Sao lưu out/ngayhoi.db hằng ngày (sqlite3 out/ngayhoi.db ".backup out/backup_YYYYMMDD.db").
- Lịch cộng điểm: Windows `schtasks /create /tn CongDiem /sc daily /st 18:00 /tr "<python> <đường dẫn tuyệt đối>\scripts\cong_diem.py"`;
  Linux `0 18 * * * cd /opt/ngayhoi-ai && .venv/bin/python scripts/cong_diem.py`.
- Phòng CTSV duyệt out/ngoai_le.csv mỗi ngày; nhập out/cong_diem.csv vào hệ thống điểm rèn luyện (bước giữ người).
- Theo dõi out/nhat_ky_agent.jsonl: số lần ghi qua agent phải trùng số lần người dùng bấm Xác nhận.

## 3. Giới hạn đã biết
- SQLite phù hợp quy mô một ngày hội (vài nghìn lượt). Quy mô lớn hơn: chuyển PostgreSQL, giữ nguyên câu INSERT … SELECT.
- Chế độ offline dùng TF-IDF + từ điển đồng nghĩa (data/dong_nghia.json); từ điển được hiệu chỉnh trên bộ câu hỏi vàng
  nên cần thêm bộ câu kiểm tra độc lập trước khi tin vào kết quả 10/10.
- Nền poster mặc định do thuật toán sinh; muốn dùng ảnh do mô hình sinh, đặt tệp data/poster/nen.png và ghi đủ sổ tài sản.
