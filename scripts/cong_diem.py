"""Tác vụ cộng điểm rèn luyện — chạy theo lịch (Task Scheduler / cron). Chạy lại an toàn."""
import _goc  # noqa: F401
from app import db, tu_dong

if __name__ == "__main__":
    kq = tu_dong.chay(db.ket_noi())
    print(f"Đủ điều kiện: {kq['du_dieu_kien']} · cộng mới: {kq['cong_moi']} · đã cộng trước: {kq['da_cong_truoc']}"
          f" · ngoại lệ: {len(kq['ngoai_le'])}")
    for n in kq["ngoai_le"]:
        print("  ngoại lệ:", n["ma_sv"], n["ma_phien"], n["ly_do"])
