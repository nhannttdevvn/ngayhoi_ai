"""Đánh giá RAG: Recall@3 trên 10 câu hỏi vàng + đo điểm câu ngoài phạm vi để chọn ngưỡng."""
import json

import _goc  # noqa: F401
from app import config, rag

if __name__ == "__main__":
    vang = json.loads((config.DATA / "cau_hoi_vang.json").read_text(encoding="utf-8"))
    ngoai = json.loads((config.DATA / "cau_hoi_ngoai.json").read_text(encoding="utf-8"))
    dung, diem_trong = 0, []
    for c in vang:
        kq = rag.tim(c["hoi"])
        ok = any(d["nguon"].startswith(c["dieu"] + ".") for _, d in kq)
        dung += ok; diem_trong.append(kq[0][0])
        print("✓" if ok else "✕", f"{kq[0][0]:.3f}", c["hoi"], "→", kq[0][1]["nguon"][:8])
    print(f"Recall@3: {dung}/{len(vang)}")
    diem_ngoai = [rag.tim(q)[0][0] for q in ngoai]
    for q, s in zip(ngoai, diem_ngoai):
        print(f"  ngoài phạm vi {s:.3f}  {q}")
    lo, hi = max(diem_ngoai), min(diem_trong)
    print(f"Trong phạm vi: {min(diem_trong):.3f}–{max(diem_trong):.3f} · Ngoài phạm vi: {min(diem_ngoai):.3f}–{max(diem_ngoai):.3f}")
    if lo < hi:
        print(f"Khoảng trống {lo:.3f}–{hi:.3f} → gợi ý ngưỡng {(lo + hi) / 2:.2f} (đang dùng {rag.nguong()})")
    else:
        print("Hai nhóm chồng lấn → đặt ngưỡng thấp hơn nhóm trong phạm vi, dựa thêm vào quy tắc lối ra (lớp 2)")
