# Đặc tả: Đăng ký phiên Ngày hội việc làm

Sức chứa: 30 sinh viên/phiên, đếm riêng từng phiên (Điều 3). Mỗi sinh viên tối đa 3 phiên.
Mã sinh viên lấy từ phiên đăng nhập, không lấy từ dữ liệu gửi lên.
Thứ tự báo lỗi: KHONG_CO_PHIEN → DA_DANG_KY → HET_CHO / QUA_SO_PHIEN.

| # | Đang có | Hành động | Kết quả mong đợi | Test |
|---|---------|-----------|------------------|------|
| 1 | P05 còn chỗ | SV đăng ký P05 | 201 | test_1 |
| 2 | P01 có 29 người | SV mới đăng ký P01 | 201 (người thứ 30 vẫn được) | test_2 |
| 3 | P01 có 30 người | SV mới đăng ký P01 | 409 HET_CHO | test_3 |
| 4 | P01 có 30, gồm SV đó | SV đó đăng ký lại P01 | 409 DA_DANG_KY | test_4 |
| 5 | P01 có 30 người | SV đăng ký P02 | 201 (đếm riêng từng phiên) | test_5 |
| 6 | SV đã có 3 phiên | Đăng ký phiên thứ 4 | 409 QUA_SO_PHIEN | test_6 |
| 7 | — | Gửi thiếu ma_phien | 422 | test_7 |
| 8 | Chưa đăng nhập | Đăng ký | 401 | test_8 |
| 9 | Chưa đăng ký P02 | Hủy P02 | 404 KHONG_CO | test_9 |
| 10 | Đã đăng ký, còn > 24 giờ | Hủy | 200 | test_10 |
| 11 | P11 còn 2 chỗ | 40 SV bấm cùng lúc | đúng 2 × 201, còn lại 409 HET_CHO | scripts/ban_dong_thoi.py |

Ngoài phạm vi: danh sách chờ khi hết chỗ; khóa đăng ký do vắng 2 lần (Điều 4) — xử lý ở phiên bản sau.
