"""RAG (Buổi 6): cắt theo Điều, có trích dẫn, từ chối câu ngoài phạm vi."""
from app import config, rag


def test_cat_moi_dieu_mot_doan():
    doan = rag.cat_doan((config.DATA / "quy_che.md").read_text(encoding="utf-8"))
    assert len(doan) == 10 and doan[3]["nguon"].startswith("Điều 4.")


def test_tra_loi_co_trich_dan(client):
    r = client.post("/api/hoi", json={"cau_hoi": "Muốn hủy đăng ký thì hạn chót là khi nào?"}).json()
    assert "[Điều 4]" in r["tra_loi"] and "24 giờ" in r["tra_loi"]


def test_cau_ngoai_pham_vi_bi_tu_choi(client):
    r = client.post("/api/hoi", json={"cau_hoi": "Ngày hội có phát đồ ăn trưa không?"}).json()
    assert r["tra_loi"] == rag.TU_CHOI and r["lop_tu_choi"] == 1


def test_recall_at_3_toi_thieu_8_tren_10():
    import json
    vang = json.loads((config.DATA / "cau_hoi_vang.json").read_text(encoding="utf-8"))
    dung = sum(any(d["nguon"].startswith(c["dieu"] + ".") for _, d in rag.tim(c["hoi"])) for c in vang)
    assert dung >= 8
