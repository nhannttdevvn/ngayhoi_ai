"""Phân tích (Buổi 8), tự động hóa (Buổi 9), poster (Buổi 10)."""
import sqlite3

from app import phan_tich, poster, tu_dong


def test_tap_nho_dung_dap_an_tinh_tay():
    m = sqlite3.connect(":memory:")
    m.executescript("""CREATE TABLE dang_ky(ma_sv, ma_phien); CREATE TABLE diem_danh(ma_sv, ma_phien, phut_tre);
        INSERT INTO dang_ky VALUES ('A','P01'),('B','P01'),('C','P01'),('D','P01');
        INSERT INTO diem_danh VALUES ('A','P01','0'),('A','P01','0'),('B','p01','2'),('E','P01','0');""")
    assert m.execute(phan_tich.CHI_SO["TL_LUOT_CO_QUET"][1]).fetchone()[0] == 50.0


def test_ho_so_tim_du_4_loai_loi(k):
    hs = phan_tich.ho_so(k)
    assert len(hs["trung"]) == 3 and len(hs["khong_chuan"]) == 1 and len(hs["trong"]) == 1 and len(hs["nguoi_la"]) == 1


def test_chay_lai_khong_cong_hai_lan(k):
    a = tu_dong.chay(k); b = tu_dong.chay(k)
    assert a["cong_moi"] == a["du_dieu_kien"] > 0 and b["cong_moi"] == 0


def test_ngoai_le_co_ly_do(k):
    ly_do = {n["ly_do"] for n in tu_dong.chay(k)["ngoai_le"]}
    assert ly_do == {"THIEU_GIO", "KHONG_DANG_KY"}


def test_poster_tuong_phan_va_doi_chieu():
    kq = poster.tao(48213)
    assert all(v >= 4.5 for v in kq["tuong_phan"].values()) and all(kq["doi_chieu"].values())


def test_cung_seed_cung_nen():
    import numpy as np
    assert np.array_equal(np.asarray(poster.sinh_nen(7)), np.asarray(poster.sinh_nen(7)))
