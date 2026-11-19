"""Poster Ngày hội (Buổi 10): nền tạo lại được + lớp chữ đặt bằng mã, đúng từng dấu.

- Nền: nếu có tệp nền do mô hình ảnh sinh (data/poster/nen.png, đã ghi sổ tài sản) thì dùng tệp đó;
  nếu không, sinh nền trừu tượng bằng thuật toán có SEED (tạo lại được) để thay thế.
- Chữ, mã QR: lấy NGUYÊN VĂN từ data/poster/noi_dung.json, vẽ trên lớp riêng (chu.png) — không để mô hình vẽ chữ.
- Kiểm tra: tương phản WCAG (≥ 4,5:1), đối chiếu thông tin bắt buộc trong brief, alt text → kiem_tra.md.
- Sổ tài sản: mỗi lần tạo nền ghi một dòng vào so_tai_san.csv.
"""
import csv
import json
import os
from datetime import date
from pathlib import Path

import numpy as np
import qrcode
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import config

W, H = 1080, 1350
MAU_DAI = (124, 20, 5)        # #7c1405 — dải nền đặc sau chữ
MAU_CHU = (255, 255, 255)
MAU_NHAN = (255, 201, 71)
FONT = os.getenv("FONT_PATH", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
FONT_DAM = os.getenv("FONT_BOLD_PATH", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
THU_MUC = config.OUT / "poster"

from pathlib import Path
from PIL import ImageFont
import platform

def tim_font(dam=False):
    system = platform.system()

    if system == "Darwin":  # macOS
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
            if dam else
            "/System/Library/Fonts/Supplemental/Arial.ttf",

            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        ]

    elif system == "Linux":
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            if dam else
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]

    else:
        candidates = [
            "C:/Windows/Fonts/arialbd.ttf"
            if dam else
            "C:/Windows/Fonts/arial.ttf"
        ]

    for path in candidates:
        if Path(path).is_file():
            return path

    raise FileNotFoundError(
        "Không tìm thấy font phù hợp trên hệ thống."
    )


FONT = tim_font(False)
FONT_DAM = tim_font(True)

def _f(cd, dam=False):
    return ImageFont.truetype(
        FONT_DAM if dam else FONT,
        cd
    )


def sinh_nen(seed: int) -> Image.Image:
    """Nền trừu tượng tông đỏ – vàng: dải ánh sáng, khối kiến trúc mờ, đốm sáng. Cùng seed → cùng ảnh."""
    r = np.random.default_rng(seed)
    y = np.linspace(0, 1, H)[:, None]; x = np.linspace(0, 1, W)[None, :]
    nen = np.zeros((H, W, 3))
    tren, duoi = np.array([214, 88, 38]), np.array([92, 12, 6])
    nen += tren * (1 - y[..., None]) + duoi * y[..., None]
    cx, cy = r.uniform(0.55, 0.85), r.uniform(0.08, 0.2)
    nen += (np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / 0.05)[..., None]) * np.array([255, 196, 90]) * 0.6
    img = Image.fromarray(np.clip(nen, 0, 255).astype("uint8"))
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(7):                                      # khung cửa kính / cột hội trường
        x0 = int(W * (0.06 + i * 0.135)); top = int(H * r.uniform(0.04, 0.12))
        d.rectangle([x0, top, x0 + int(W * 0.09), int(H * 0.56)], fill=(255, 230, 180, int(r.uniform(18, 40))))
    for _ in range(14):                                     # bóng người mờ, không có khuôn mặt
        bx = int(r.uniform(0.05, 0.95) * W); by = int(H * r.uniform(0.42, 0.53)); s = int(r.uniform(18, 30))
        d.ellipse([bx - s // 2, by - s * 3, bx + s // 2, by - s * 2], fill=(60, 10, 5, 110))
        d.rounded_rectangle([bx - s, by - s * 2, bx + s, by + s], radius=s // 2, fill=(60, 10, 5, 110))
    for _ in range(40):                                     # đốm sáng
        bx, by = r.uniform(0, W), r.uniform(0, H * 0.5); s = r.uniform(6, 26)
        d.ellipse([bx - s, by - s, bx + s, by + s], fill=(255, 220, 140, int(r.uniform(30, 80))))
    return img.filter(ImageFilter.GaussianBlur(3))


def _do_sang(c):
    def k(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = c
    return 0.2126 * k(r) + 0.7152 * k(g) + 0.0722 * k(b)


def tuong_phan(c1, c2) -> float:
    a, b = sorted([_do_sang(c1), _do_sang(c2)], reverse=True)
    return round((a + 0.05) / (b + 0.05), 1)


def _xuong_dong(d, s, f, rong):
    tu, dong, kq = s.split(), "", []
    for w in tu:
        thu = (dong + " " + w).strip()
        if d.textlength(thu, font=f) <= rong:
            dong = thu
        else:
            kq.append(dong); dong = w
    return kq + [dong]


def lop_chu(nd: dict) -> Image.Image:
    lop = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lop)
    y0 = int(H * 0.55)
    d.rectangle([0, y0, W, H], fill=MAU_DAI + (255,))
    d.rectangle([0, y0, W, y0 + 10], fill=MAU_NHAN + (255,))
    y = y0 + 50
    for dong in _xuong_dong(d, nd["tieu_de"], _f(76, True), W - 120):
        d.text((60, y), dong, font=_f(76, True), fill=MAU_CHU); y += 88
    for dong in _xuong_dong(d, nd["phu_de"], _f(32), W - 120):
        d.text((60, y), dong, font=_f(32), fill=MAU_NHAN); y += 42
    y += 24
    d.text((60, y), nd["thoi_gian"], font=_f(38, True), fill=MAU_CHU); y += 56
    d.text((60, y), nd["dia_diem"], font=_f(34), fill=MAU_CHU); y += 70
    qr = qrcode.make(nd["url_dang_ky"]).convert("RGB").resize((200, 200))
    lop.paste(qr, (W - 260, H - 260))
    for dong in _xuong_dong(d, nd["loi_keu_goi"], _f(34, True), W - 400):
        d.text((60, y), dong, font=_f(34, True), fill=MAU_NHAN); y += 46
    d.text((60, H - 60), nd["don_vi"], font=_f(22), fill=(240, 220, 210))
    return lop


def tao(seed: int = 48213) -> dict:
    THU_MUC.mkdir(parents=True, exist_ok=True)
    nd = json.loads((config.DATA / "poster" / "noi_dung.json").read_text(encoding="utf-8"))
    tep_nen_ai = config.DATA / "poster" / "nen.png"
    if tep_nen_ai.exists():
        nen = Image.open(tep_nen_ai).convert("RGB").resize((W, H)); nguon_nen = "data/poster/nen.png (ảnh do mô hình sinh, xem sổ)"
    else:
        nen = sinh_nen(seed); nguon_nen = f"thuật toán sinh_nen, seed={seed}"
    ten_nen = THU_MUC / f"nen_{seed}.png"; nen.save(ten_nen)
    chu = lop_chu(nd); chu.save(THU_MUC / "chu.png")
    poster = Image.alpha_composite(nen.convert("RGBA"), chu).convert("RGB"); poster.save(THU_MUC / "poster.png")

    so = THU_MUC / "so_tai_san.csv"; moi = not so.exists()
    with open(so, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if moi:
            w.writerow(["tep", "cong_cu", "mo_hinh", "seed", "kich_thuoc", "prompt", "phu_dinh", "ngay", "quyen", "nhan_ai"])
        w.writerow([ten_nen.name, "app/poster.py" if "seed" in nguon_nen else "(ghi công cụ sinh ảnh)",
                    "sinh_nen v1" if "seed" in nguon_nen else "(ghi mô hình + phiên bản)", seed, f"{W}x{H}",
                    "data/poster/prompts/nen_v1.txt", "data/poster/prompts/phu_dinh.txt", date.today().isoformat(),
                    "Nhà trường sở hữu (nền do mã nguồn nội bộ tạo)", "không" if "seed" in nguon_nen else "có"])

    tp = {"chữ trắng / dải đỏ": tuong_phan(MAU_CHU, MAU_DAI), "chữ vàng / dải đỏ": tuong_phan(MAU_NHAN, MAU_DAI)}
    brief = (config.DATA / "poster" / "brief.md").read_text(encoding="utf-8")
    bat_buoc = {"Tên sự kiện": nd["tieu_de"], "Ngày": "13/11/2026", "Giờ": "8:00 – 16:30", "Địa điểm": nd["dia_diem"]}
    doi_chieu = {k: (v in json.dumps(nd, ensure_ascii=False)) for k, v in bat_buoc.items()}
    alt = (f"Poster {nd['tieu_de']}, {nd['thoi_gian']}, tại {nd['dia_diem']}; "
           f"{nd['loi_keu_goi'].lower()} bằng mã QR ở góc phải dưới.")
    kt = ["# Kiểm tra poster", f"Nền: {nguon_nen}", "", "## 1. Thu nhỏ 25%",
          "Mở poster_25.png: đọc được tên sự kiện, ngày, giờ (người kiểm ghi kết quả).", "",
          "## 2. Tương phản (WCAG, yêu cầu ≥ 4,5 : 1)"] + [f"- {k}: {v} : 1 {'✓' if v >= 4.5 else '✗'}" for k, v in tp.items()] + [
          "", "## 3. Đối chiếu thông tin bắt buộc trong brief"] + [f"- {k}: {'✓' if ok else '✗'}" for k, ok in doi_chieu.items()] + [
          "", "## Alt text", alt, "", "## Lỗi bạn khác tìm thấy (đổi chéo)", "- [ ] Chữ lạ trong nền · [ ] Người giống người thật · [ ] Thiếu thông tin · [ ] Logo méo"]
    (THU_MUC / "kiem_tra.md").write_text("\n".join(kt), encoding="utf-8")
    poster.resize((W // 4, H // 4)).save(THU_MUC / "poster_25.png")
    return {"poster": "out/poster/poster.png", "nen": f"out/poster/{ten_nen.name}",
            "tuong_phan": tp, "doi_chieu": doi_chieu, "alt": alt, "brief_co_cam_chu_trong_nen": "chữ trong ảnh nền" in brief}
