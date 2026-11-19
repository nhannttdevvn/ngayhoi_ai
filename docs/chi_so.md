# Hợp đồng chỉ số (Buổi 8)

| Tên | Dùng để | Tử số | Mẫu số | Xử lý dữ liệu | Người chịu trách nhiệm |
|-----|---------|-------|--------|---------------|------------------------|
| TL_LUOT_CO_QUET | Báo cáo Ban tổ chức về mức độ tham gia | Cặp (ma_sv, ma_phien) có ≥ 1 lần quét, đếm một lần | Số dòng dang_ky | Trùng: đếm một lần · Viết thường: UPPER · Trống: vẫn tính có đến · Người lạ: loại | Nhóm IT |
| TL_LUOT_DUNG_GIO | Xét cộng điểm rèn luyện (Điều 5, 6) | Cặp có quét, CAST(phut_tre) ≤ 10, đếm một lần | Số dòng dang_ky | Trùng: một lần · UPPER · Trống: tính vắng, đưa vào ngoại lệ · Người lạ: loại | Phòng CTSV |
| TL_SINH_VIEN_CO_DEN | Đánh giá độ phủ sinh viên | Sinh viên có quét ≥ 1 phiên đã đăng ký | Số sinh viên trong dang_ky | Như TL_LUOT_CO_QUET | Ban tổ chức |

Nguồn: data/dang_ky.csv, data/diem_danh.csv. Báo cáo phải ghi TÊN chỉ số, không gọi chung là "tỷ lệ tham dự".
Mọi câu SQL tính chỉ số phải cho đúng đáp án trên tập nhỏ (scripts/kiem_tap_nho.py) trước khi chạy dữ liệu thật.
