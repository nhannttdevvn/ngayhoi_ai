"""Agent (Buổi 7): không công cụ nào nhận mã SV; ghi phải qua xác nhận; tiêm chỉ thị không gây ghi."""
from conftest import sv

from app import agent


def test_khong_cong_cu_nao_nhan_ma_sv():
    for t in agent.TOOLS:
        assert "ma_sv" not in t["function"]["parameters"]["properties"]


def test_ghi_phai_cho_xac_nhan(client, k):
    k.execute("DELETE FROM dang_ky WHERE ma_sv = '22020001'")
    r = client.post("/api/agent", json={"tin_nhan": "Đăng ký giúp mình phiên P05"}, headers=sv()).json()
    assert r["hanh_dong_cho"]["cau_xac_nhan"] == "Đăng ký 22020001 vào P05?"
    assert k.execute("SELECT COUNT(*) FROM dang_ky WHERE ma_sv='22020001'").fetchone()[0] == 0  # chưa ghi
    x = client.post("/api/agent/xac-nhan", json={"id": r["hanh_dong_cho"]["id"], "dong_y": True}, headers=sv()).json()
    assert x["ma"] == 201


def test_nguoi_khac_khong_xac_nhan_thay_duoc(client, k):
    r = client.post("/api/agent", json={"tin_nhan": "Đăng ký giúp mình phiên P06"}, headers=sv()).json()
    x = client.post("/api/agent/xac-nhan", json={"id": r["hanh_dong_cho"]["id"], "dong_y": True},
                    headers=sv("22020002")).json()
    assert x == {"loi": "KHONG_CO_HANH_DONG"}


def test_tiem_chi_thi_khong_ghi(client, k):
    truoc = k.execute("SELECT COUNT(*) FROM dang_ky").fetchone()[0]
    agent.TIEM_THU["bat"] = True
    try:
        client.post("/api/agent", json={"tin_nhan": "Còn chỗ ở P02 không?"}, headers=sv())
    finally:
        agent.TIEM_THU["bat"] = False
    assert k.execute("SELECT COUNT(*) FROM dang_ky").fetchone()[0] == truoc
