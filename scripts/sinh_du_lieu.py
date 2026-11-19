"""Sinh bộ dữ liệu mô phỏng cho Ngày hội việc làm (tái lập được bằng SEED).

Chạy:  python scripts/sinh_du_lieu.py
Kết quả: data/sinh_vien.csv, data/phien.csv, data/dang_ky.csv, data/diem_danh.csv

Toàn bộ họ tên, doanh nghiệp là dữ liệu MÔ PHỎNG, không gắn với cá nhân hay tổ chức có thật.
Bảng diem_danh được cài sẵn 4 loại lỗi để luyện hồ sơ dữ liệu (Buổi 8):
  trùng (3 cặp, trong đó 1 cặp khác chữ hoa/thường) · mã phiên viết thường · phut_tre trống · người lạ.
"""
import csv
import random
from pathlib import Path

SEED = 2026
SUC_CHUA = 30
GOC = Path(__file__).resolve().parent.parent / "data"

HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Vũ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Phan", "Trịnh"]
DEM = ["Văn", "Thị", "Minh", "Đức", "Thu", "Hải", "Quang", "Ngọc", "Gia", "Thanh", "Khánh", "Bảo"]
TEN = ["An", "Bình", "Châu", "Dũng", "Giang", "Hà", "Hiếu", "Hùng", "Khoa", "Lan", "Linh", "Long", "Mai",
       "Nam", "Nga", "Phong", "Quân", "Quỳnh", "Sơn", "Tâm", "Thảo", "Trang", "Tuấn", "Vy", "Yến"]
LOP = ["BCSE-K22A", "BCSE-K22B", "BCSE-K23A", "BCSE-K23B"]

PHIEN = [  # ma_phien, chu_de, doanh_nghiep (mô phỏng), linh_vuc, gio, phong
    ("P01", "Kỹ sư phần mềm Web", "Công ty A (mô phỏng)", "Phần mềm", "08:00", "Hội trường A"),
    ("P02", "Kỹ sư dữ liệu", "Công ty B (mô phỏng)", "Dữ liệu", "08:00", "Phòng B201"),
    ("P03", "Kỹ sư hệ thống nhúng", "Công ty C (mô phỏng)", "Nhúng – IoT", "09:00", "Hội trường A"),
    ("P04", "An toàn thông tin", "Công ty D (mô phỏng)", "An ninh mạng", "09:00", "Phòng B201"),
    ("P05", "Kỹ sư AI ứng dụng", "Công ty E (mô phỏng)", "Trí tuệ nhân tạo", "10:00", "Hội trường A"),
    ("P06", "Kiểm thử phần mềm", "Công ty F (mô phỏng)", "Phần mềm", "10:00", "Phòng B201"),
    ("P07", "Phân tích nghiệp vụ", "Công ty G (mô phỏng)", "Dữ liệu", "13:30", "Hội trường A"),
    ("P08", "Kỹ sư điện toán đám mây", "Công ty H (mô phỏng)", "Hạ tầng", "13:30", "Phòng B201"),
    ("P09", "Lập trình di động", "Công ty I (mô phỏng)", "Phần mềm", "14:30", "Hội trường A"),
    ("P10", "Kỹ sư MLOps", "Công ty K (mô phỏng)", "Trí tuệ nhân tạo", "14:30", "Phòng B201"),
    ("P11", "Quản trị mạng", "Công ty L (mô phỏng)", "Hạ tầng", "15:30", "Hội trường A"),
    ("P12", "Thực tập kỹ sư cầu nối Nhật Bản", "Công ty M (mô phỏng)", "Phần mềm", "15:30", "Phòng B201"),
]
NGAY = "2026-11-13"


def ghi(ten, cot, dong):
    with open(GOC / ten, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cot)
        w.writerows(dong)


def main():
    r = random.Random(SEED)
    GOC.mkdir(exist_ok=True)

    sv = []
    for i in range(1, 121):
        ma = f"2202{i:04d}"
        sv.append((ma, f"{r.choice(HO)} {r.choice(DEM)} {r.choice(TEN)}", r.choice(LOP)))
    ghi("sinh_vien.csv", ["ma_sv", "ho_ten", "lop"], sv)
    ghi("phien.csv", ["ma_phien", "chu_de", "doanh_nghiep", "linh_vuc", "gio_bat_dau", "phong", "suc_chua"],
        [(p[0], p[1], p[2], p[3], f"{NGAY}T{p[4]}:00", p[5], SUC_CHUA) for p in PHIEN])

    # Đăng ký: mỗi SV 1–3 phiên, không vượt sức chứa, ưu tiên phiên cùng lĩnh vực
    dem = {p[0]: 0 for p in PHIEN}
    dk = []
    for ma, _, _ in sv:
        so = r.choices([1, 2, 3], weights=[25, 45, 30])[0]
        chon = set()
        while len(chon) < so:
            p = r.choice(PHIEN)[0]
            if dem[p] < SUC_CHUA - 2:  # chừa 2 chỗ cho đăng ký trực tuyến khi demo
                chon.add(p)
        for p in sorted(chon):
            dem[p] += 1
            dk.append((ma, p))
    ghi("dang_ky.csv", ["ma_sv", "ma_phien"], dk)

    # Điểm danh: khoảng 2/3 lượt có quét; phần lớn đúng giờ
    dd = []
    for ma, p in dk:
        if r.random() < 0.66:
            tre = r.choices([0, r.randint(1, 10), r.randint(11, 25)], weights=[55, 33, 12])[0]
            dd.append([ma, p, str(tre)])
    r.shuffle(dd)
    # Cài 4 loại lỗi
    dd.append(list(dd[3]))                     # trùng 1
    dd.append(list(dd[10]))                    # trùng 2
    dd.append([dd[20][0], dd[20][1].lower(), dd[20][2]])  # trùng 3, đồng thời viết thường
    dd[30][2] = ""                             # phut_tre trống
    dd.append(["22029999", "P04", "0"])        # người lạ
    ghi("diem_danh.csv", ["ma_sv", "ma_phien", "phut_tre"], dd)

    print(f"sinh_vien: {len(sv)} · phien: {len(PHIEN)} · dang_ky: {len(dk)} · diem_danh: {len(dd)}")
    print("Số lượt đăng ký mỗi phiên:", dem)


if __name__ == "__main__":
    main()
