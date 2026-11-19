"""Hệ thống Ngày hội việc làm tích hợp AI — máy chủ API (FastAPI).

Chạy:  uvicorn app.main:app --reload       → giao diện http://localhost:8000 · tài liệu API /docs
"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import agent, config, db as csdl, llm, phan_tich, poster, rag, tu_dong
from . import dang_ky as dk

@asynccontextmanager
async def khoi_dong(_app):
    db = csdl.ket_noi()
    if db.execute("SELECT COUNT(*) FROM sinh_vien").fetchone()[0] == 0:   # lần chạy đầu: nạp dữ liệu mẫu
        csdl.nap_csv(db)
    db.close()
    yield


app = FastAPI(lifespan=khoi_dong, title="Ngày hội việc làm – AI", version="1.0.0",
              description="Đăng ký phiên · Hỏi đáp quy chế (RAG) · Trợ lý đăng ký (agent) · Thống kê · Cộng điểm · Poster")
app.add_middleware(CORSMiddleware, allow_origins=config.ALLOWED_ORIGINS,   # không dùng "*"
                   allow_methods=["GET", "POST", "DELETE"], allow_headers=["Content-Type", "X-Ma-SV", "X-Admin-Key"])


# ---------------- Phụ thuộc: kết nối CSDL, danh tính, quyền quản trị ----------------
def lay_db():
    db = csdl.ket_noi()
    try:
        yield db
    finally:
        db.close()


def nguoi_dung(x_ma_sv: str | None = Header(None), x_remote_user: str | None = Header(None),
               db=Depends(lay_db)) -> str:
    """demo: mã SV gửi trong tiêu đề X-Ma-SV (chỉ dùng khi học/thử nghiệm).
    header: hệ thống đứng sau cổng SSO của Nhà trường, cổng điền X-Remote-User."""
    ma = x_remote_user if config.AUTH_MODE == "header" else x_ma_sv
    if not ma:
        raise HTTPException(401, "CHUA_DANG_NHAP")
    if not db.execute("SELECT 1 FROM sinh_vien WHERE ma_sv = ?", (ma,)).fetchone():
        raise HTTPException(403, "KHONG_PHAI_SINH_VIEN")
    return ma


def quan_tri(x_admin_key: str | None = Header(None), x_remote_groups: str | None = Header(None)):
    if config.AUTH_MODE == "header" and x_remote_groups and config.ADMIN_GROUP in x_remote_groups.split(","):
        return True
    if config.ADMIN_KEY and x_admin_key == config.ADMIN_KEY:
        return True
    raise HTTPException(403, "CAN_QUYEN_QUAN_TRI")


def _loi(e: dk.LoiNghiepVu):
    raise HTTPException(e.ma, e.chi_tiet)


# ---------------- Mô hình dữ liệu yêu cầu ----------------
class YeuCauDangKy(BaseModel):
    ma_phien: str = Field(..., examples=["P05"])


class CauHoi(BaseModel):
    cau_hoi: str = Field(..., min_length=3, max_length=500)


class TinNhan(BaseModel):
    tin_nhan: str = Field(..., min_length=2, max_length=500)


class XacNhan(BaseModel):
    id: str
    dong_y: bool


# ---------------- Thông tin chung ----------------
@app.get("/api/trang-thai")
def trang_thai(db=Depends(lay_db)):
    return {"llm": "ollama" if llm.co_ollama() else "offline", "auth": config.AUTH_MODE,
            "mo_hinh_sinh": config.MO_HINH_SINH, "mo_hinh_nhung": config.MO_HINH_NHUNG,
            "so_sinh_vien": db.execute("SELECT COUNT(*) FROM sinh_vien").fetchone()[0]}


@app.get("/api/toi")
def toi(ma_sv: str = Depends(nguoi_dung), db=Depends(lay_db)):
    r = db.execute("SELECT * FROM sinh_vien WHERE ma_sv = ?", (ma_sv,)).fetchone()
    return dict(r)


# ---------------- Đăng ký (Buổi 3, 4) ----------------
@app.get("/api/phien")
def phien(x_ma_sv: str | None = Header(None), db=Depends(lay_db)):
    return dk.danh_sach_phien(db, x_ma_sv)


@app.get("/api/con-cho")
def con_cho(ma_phien: str, db=Depends(lay_db)):
    try:
        return {"ma_phien": ma_phien.upper(), "con_cho": dk.con_cho(db, ma_phien.upper())}
    except dk.LoiNghiepVu as e:
        _loi(e)


@app.post("/api/dang-ky", status_code=201)
def dang_ky(d: YeuCauDangKy, ma_sv: str = Depends(nguoi_dung), db=Depends(lay_db)):
    try:
        return dk.dang_ky(db, ma_sv, d.ma_phien)
    except dk.LoiNghiepVu as e:
        _loi(e)


@app.delete("/api/dang-ky/{ma_phien}")
def huy(ma_phien: str, ma_sv: str = Depends(nguoi_dung), db=Depends(lay_db)):
    try:
        return dk.huy(db, ma_sv, ma_phien)
    except dk.LoiNghiepVu as e:
        _loi(e)


# ---------------- Hỏi đáp quy chế – RAG (Buổi 1, 6) ----------------
@app.post("/api/hoi")
def hoi(c: CauHoi):
    return rag.hoi(c.cau_hoi)


# ---------------- Trợ lý đăng ký – agent (Buổi 7) ----------------
@app.post("/api/agent")
def tro_ly(t: TinNhan, ma_sv: str = Depends(nguoi_dung), db=Depends(lay_db)):
    return agent.tro_chuyen(db, ma_sv, t.tin_nhan)


@app.post("/api/agent/xac-nhan")
def tro_ly_xac_nhan(x: XacNhan, ma_sv: str = Depends(nguoi_dung), db=Depends(lay_db)):
    return agent.xac_nhan(db, ma_sv, x.id, x.dong_y)


# ---------------- Quản trị: thống kê, cộng điểm, poster (Buổi 8, 9, 10) ----------------
@app.get("/api/thong-ke", dependencies=[Depends(quan_tri)])
def thong_ke(db=Depends(lay_db)):
    phan_tich.ve_bieu_do(db)
    return {"ho_so": phan_tich.ho_so(db), "chi_so": phan_tich.chi_so(db), "theo_phien": phan_tich.theo_phien(db),
            "bieu_do": "/out/bieu_do_ty_le.png"}


@app.post("/api/cong-diem", dependencies=[Depends(quan_tri)])
def cong_diem(db=Depends(lay_db)):
    return tu_dong.chay(db)


@app.post("/api/poster", dependencies=[Depends(quan_tri)])
def tao_poster(seed: int = 48213):
    return poster.tao(seed)


@app.get("/out/{ten:path}")
def tep_ket_qua(ten: str):
    p = (config.OUT / ten).resolve()
    if config.OUT.resolve() not in p.parents or p.suffix not in {".png", ".csv", ".md"} or not p.exists():
        raise HTTPException(404)
    return FileResponse(p)


app.mount("/", StaticFiles(directory=config.GOC / "web", html=True), name="web")
