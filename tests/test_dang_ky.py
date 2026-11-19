"""Đặc tả spec.md — mỗi dòng của bảng ví dụ là một test (Buổi 3, 4)."""
from conftest import sv


def lap_day(k, ma_phien, n):
    """Đưa phiên về đúng n người (xóa đăng ký sẵn có, thêm SV giả định 2202xxxx)."""
    k.execute("DELETE FROM dang_ky WHERE ma_phien = ?", (ma_phien,))
    for i in range(n):
        k.execute("INSERT INTO dang_ky(ma_sv, ma_phien) VALUES (?, ?)", (f"9900{i:04d}", ma_phien))


def test_1_dang_ky_thanh_cong(client, k):
    k.execute("DELETE FROM dang_ky WHERE ma_sv = '22020001'")
    r = client.post("/api/dang-ky", json={"ma_phien": "P05"}, headers=sv())
    assert r.status_code == 201


def test_2_nguoi_thu_30_van_duoc(client, k):
    lap_day(k, "P01", 29)
    k.execute("DELETE FROM dang_ky WHERE ma_sv = '22020001'")
    assert client.post("/api/dang-ky", json={"ma_phien": "P01"}, headers=sv()).status_code == 201


def test_3_nguoi_thu_31_bi_tu_choi(client, k):
    lap_day(k, "P01", 30)
    k.execute("DELETE FROM dang_ky WHERE ma_sv = '22020001'")
    r = client.post("/api/dang-ky", json={"ma_phien": "P01"}, headers=sv())
    assert r.status_code == 409 and r.json()["detail"] == "HET_CHO"


def test_4_da_dang_ky_khi_day_bao_dung_ly_do(client, k):
    lap_day(k, "P01", 29)
    k.execute("DELETE FROM dang_ky WHERE ma_sv = '22020001'")
    k.execute("INSERT INTO dang_ky(ma_sv, ma_phien) VALUES ('22020001', 'P01')")   # đủ 30, gồm 22020001
    r = client.post("/api/dang-ky", json={"ma_phien": "P01"}, headers=sv())
    assert r.status_code == 409 and r.json()["detail"] == "DA_DANG_KY"


def test_5_dem_rieng_tung_phien(client, k):
    lap_day(k, "P01", 30)
    k.execute("DELETE FROM dang_ky WHERE ma_sv = '22020001'")
    assert client.post("/api/dang-ky", json={"ma_phien": "P02"}, headers=sv()).status_code == 201


def test_6_toi_da_3_phien(client, k):
    k.execute("DELETE FROM dang_ky WHERE ma_sv = '22020001'")
    for p in ["P02", "P04", "P06"]:
        assert client.post("/api/dang-ky", json={"ma_phien": p}, headers=sv()).status_code == 201
    r = client.post("/api/dang-ky", json={"ma_phien": "P08"}, headers=sv())
    assert r.status_code == 409 and r.json()["detail"] == "QUA_SO_PHIEN"


def test_7_thieu_truong_422(client):
    assert client.post("/api/dang-ky", json={}, headers=sv()).status_code == 422


def test_8_chua_dang_nhap_401(client):
    assert client.post("/api/dang-ky", json={"ma_phien": "P02"}).status_code == 401


def test_9_huy_khi_khong_dang_ky_bao_khong_co(client, k):
    k.execute("DELETE FROM dang_ky WHERE ma_sv = '22020001'")
    r = client.delete("/api/dang-ky/P02", headers=sv())
    assert r.status_code == 404 and r.json()["detail"] == "KHONG_CO"


def test_10_huy_dung_han(client, k):
    k.execute("DELETE FROM dang_ky WHERE ma_sv = '22020001'")
    client.post("/api/dang-ky", json={"ma_phien": "P02"}, headers=sv())
    assert client.delete("/api/dang-ky/P02", headers=sv()).status_code == 200
