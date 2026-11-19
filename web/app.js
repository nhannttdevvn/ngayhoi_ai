// Giao diện Ngày hội việc làm — JavaScript thuần, không phụ thuộc thư viện ngoài.
const $ = (s) => document.querySelector(s);
const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html !== undefined) e.innerHTML = html; return e; };
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const THONG_BAO = {
  DA_DANG_KY: "Bạn đã đăng ký phiên này.", HET_CHO: "Phiên đã hết chỗ.", QUA_SO_PHIEN: "Bạn đã đăng ký đủ 3 phiên (Điều 3).",
  KHONG_CO_PHIEN: "Không có phiên này.", QUA_HAN_HUY: "Đã quá hạn hủy (chậm nhất 24 giờ trước giờ bắt đầu — Điều 4).",
  KHONG_CO: "Bạn chưa đăng ký phiên này.", CHUA_DANG_NHAP: "Vui lòng đăng nhập.", KHONG_PHAI_SINH_VIEN: "Mã sinh viên không có trong danh sách.",
  CAN_QUYEN_QUAN_TRI: "Khóa quản trị không đúng.",
};
let maSV = "";
try { maSV = localStorage.getItem("ma_sv") || ""; } catch (e) { /* trình duyệt chặn lưu trữ: bỏ qua */ }

async function api(path, opt = {}) {
  const headers = { "Content-Type": "application/json", ...(opt.headers || {}) };
  if (maSV) headers["X-Ma-SV"] = maSV;
  const r = await fetch(path, { ...opt, headers });
  const body = await r.json().catch(() => ({}));
  if (!r.ok) throw { ma: r.status, chi_tiet: body.detail };
  return body;
}
const loiText = (e) => THONG_BAO[e.chi_tiet] || (Array.isArray(e.chi_tiet) ? "Dữ liệu chưa hợp lệ (422)." : `Lỗi ${e.ma}: ${e.chi_tiet}`);

// ---------- Tab ----------
document.querySelectorAll(".tabs button").forEach((b) => b.onclick = () => {
  document.querySelectorAll(".tabs button").forEach((x) => x.classList.toggle("on", x === b));
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("on", t.id === "tab-" + b.dataset.tab));
});

// ---------- Đăng nhập (chế độ demo) ----------
async function hienNguoi() {
  if (!maSV) { $("#dang-nhap").classList.remove("hidden"); $("#nguoi").classList.add("hidden"); return; }
  try {
    const t = await api("/api/toi");
    $("#nguoi").innerHTML = `<b>${esc(t.ho_ten)}</b> · ${esc(t.ma_sv)} · ${esc(t.lop)} <button class="phu" id="thoat">Đăng xuất</button>`;
    $("#nguoi").classList.remove("hidden"); $("#dang-nhap").classList.add("hidden");
    $("#thoat").onclick = () => { maSV = ""; try { localStorage.removeItem("ma_sv"); } catch (e) {} hienNguoi(); taiPhien(); };
  } catch (e) { maSV = ""; alert(loiText(e)); hienNguoi(); }
}
$("#dang-nhap").onsubmit = (ev) => { ev.preventDefault(); maSV = $("#ma-sv").value.trim();
  try { localStorage.setItem("ma_sv", maSV); } catch (e) {} hienNguoi().then(taiPhien); };

// ---------- Đăng ký phiên ----------
async function taiPhien() {
  const ds = await api("/api/phien");
  const g = $("#ds-phien"); g.innerHTML = "";
  ds.forEach((p) => {
    const da = p.suc_chua - p.con_cho, pct = Math.round((da / p.suc_chua) * 100);
    const c = el("div", "card");
    const tag = p.da_dang_ky ? `<span class="tag ok">Đã đăng ký ✓</span>` : p.con_cho <= 0 ? `<span class="tag het">Hết chỗ</span>` : `<span class="tag">Còn ${p.con_cho}/${p.suc_chua} chỗ</span>`;
    c.innerHTML = `<div class="row" style="margin:0"><span class="ma">${esc(p.ma_phien)} · ${esc(p.gio_bat_dau.slice(11, 16))}</span>${tag}</div>
      <div class="cd">${esc(p.chu_de)}</div><div class="meta">${esc(p.doanh_nghiep)} · ${esc(p.linh_vuc)} · ${esc(p.phong)}</div>
      <div class="bar" aria-label="Đã đăng ký ${da}/${p.suc_chua}"><i style="width:${pct}%"></i></div>`;
    const row = el("div", "row");
    const b = el("button", p.da_dang_ky ? "phu" : "", p.da_dang_ky ? "Hủy đăng ký" : "Đăng ký");
    b.disabled = !maSV || (!p.da_dang_ky && p.con_cho <= 0);
    b.onclick = () => p.da_dang_ky ? huy(p.ma_phien) : dangKy(p.ma_phien);
    row.append(el("span", "meta", `${da} đã đăng ký`), b); c.append(row); g.append(c);
  });
}
function tb(msg, ok) { const n = $("#tb-phien"); n.textContent = msg; n.className = "note " + (ok ? "ok" : "loi"); }
async function dangKy(ma) {
  try { await api("/api/dang-ky", { method: "POST", body: JSON.stringify({ ma_phien: ma }) }); tb(`Đăng ký thành công phiên ${ma}.`, true); }
  catch (e) { tb(loiText(e), false); }
  taiPhien();
}
async function huy(ma) {
  if (!confirm(`Hủy đăng ký phiên ${ma}?`)) return;
  try { await api(`/api/dang-ky/${ma}`, { method: "DELETE" }); tb(`Đã hủy phiên ${ma}.`, true); } catch (e) { tb(loiText(e), false); }
  taiPhien();
}

// ---------- Hỏi đáp quy chế ----------
const GOI_Y_HOI = ["Muốn hủy đăng ký thì hạn chót là khi nào?", "Có được quay video lúc phỏng vấn không?", "Tham gia được cộng mấy điểm rèn luyện?", "Ngày hội có phát đồ ăn trưa không?"];
GOI_Y_HOI.forEach((q) => { const b = el("button", "", esc(q)); b.type = "button"; b.onclick = () => { $("#cau-hoi").value = q; hoi(); }; $("#goi-y-hoi").append(b); });
async function hoi() {
  const q = $("#cau-hoi").value.trim(); if (!q) return;
  const box = el("div", "ans", `<div class="q">${esc(q)}</div><div>Đang tìm…</div>`); $("#kq-hoi").prepend(box);
  try {
    const r = await api("/api/hoi", { method: "POST", body: JSON.stringify({ cau_hoi: q }) });
    const src = r.nguon.map((n) => `<span>${esc(n.nguon)} · ${n.diem.toFixed(2)}</span>`).join("");
    const lop = r.lop_tu_choi ? ` · từ chối ở lớp ${r.lop_tu_choi} (điểm cao nhất < ngưỡng ${r.nguong})` : "";
    box.innerHTML = `<div class="q">${esc(q)}</div><div>${esc(r.tra_loi)}</div>
      <div class="src">Đoạn tìm được: ${src}<br>Chế độ: ${esc(r.che_do)} · ngưỡng ${r.nguong}${lop}</div>`;
  } catch (e) { box.lastChild.textContent = loiText(e); }
}
$("#f-hoi").onsubmit = (ev) => { ev.preventDefault(); hoi(); };

// ---------- Trợ lý đăng ký (agent) ----------
const GOI_Y_AGENT = ["Có phiên nào về dữ liệu không?", "P01 hay P03 còn nhiều chỗ hơn?", "Đăng ký giúp mình phiên P05", "Đăng ký cho bạn 22020002 vào P01"];
GOI_Y_AGENT.forEach((q) => { const b = el("button", "", esc(q)); b.type = "button"; b.onclick = () => { $("#tin-nhan").value = q; guiAgent(); }; $("#goi-y-agent").append(b); });
function themMsg(cls, html) { const m = el("div", "msg " + cls, html); $("#hoi-thoai").append(m); $("#hoi-thoai").scrollTop = 1e9; return m; }
async function guiAgent() {
  const t = $("#tin-nhan").value.trim(); if (!t) return;
  if (!maSV) { alert("Vui lòng đăng nhập."); return; }
  themMsg("u", esc(t)); $("#tin-nhan").value = "";
  try {
    const r = await api("/api/agent", { method: "POST", body: JSON.stringify({ tin_nhan: t }) });
    r.vet.forEach((v) => $("#hoi-thoai").append(el("div", "trace", `[${esc(v.cong_cu)}] ${esc(JSON.stringify(v.tham_so))} → ${esc(JSON.stringify(v.ket_qua))}`)));
    themMsg("a", esc(r.tra_loi));
    if (r.hanh_dong_cho) {
      const hd = r.hanh_dong_cho;
      const c = el("div", "confirm", `<b>Cần bạn xác nhận thao tác ghi:</b> ${esc(hd.cau_xac_nhan)}<div class="acts"></div>`);
      const ok = el("button", "", "Xác nhận"), no = el("button", "phu", "Từ chối");
      const xn = async (dongY) => { ok.disabled = no.disabled = true;
        const k = await api("/api/agent/xac-nhan", { method: "POST", body: JSON.stringify({ id: hd.id, dong_y: dongY }) });
        $("#hoi-thoai").append(el("div", "trace", `[dang_ky] ${esc(JSON.stringify({ ma_phien: hd.ma_phien }))} → ${esc(JSON.stringify(k))}`));
        themMsg("a", k.ma === 201 ? `Đã đăng ký phiên ${esc(hd.ma_phien)}.` : k.loi === "NGUOI_DUNG_TU_CHOI" ? "Đã hủy thao tác, không có gì được ghi." : loiText({ chi_tiet: k.loi, ma: k.ma }));
        taiPhien(); };
      ok.onclick = () => xn(true); no.onclick = () => xn(false);
      c.querySelector(".acts").append(ok, no); $("#hoi-thoai").append(c); $("#hoi-thoai").scrollTop = 1e9;
    }
  } catch (e) { themMsg("a", esc(loiText(e))); }
}
$("#f-agent").onsubmit = (ev) => { ev.preventDefault(); guiAgent(); };

// ---------- Quản trị ----------
const khoa = () => ({ "X-Admin-Key": $("#khoa").value });
$("#b-thong-ke").onclick = async () => {
  try {
    const r = await api("/api/thong-ke", { headers: khoa() });
    const kp = Object.entries(r.chi_so).map(([k, v]) => `<div class="kpi"><div class="v">${v.gia_tri.toFixed(1)}%</div><b>${esc(k)}</b><div class="d">${esc(v.dinh_nghia)}</div></div>`).join("");
    const hs = Object.entries(r.ho_so).map(([k, v]) => `<tr><td>${esc(k)}</td><td>${v.length}</td><td>${esc(v.map((x) => Object.values(x).join("·")).join("; "))}</td></tr>`).join("");
    $("#kq-qt").innerHTML = `<div class="kpis">${kp}</div><div class="two"><div class="box"><b>Hồ sơ dữ liệu (4 phép kiểm)</b>
      <table><tr><th>Phép kiểm</th><th>Số dòng</th><th>Chi tiết</th></tr>${hs}</table></div>
      <div class="box"><img class="full" src="${r.bieu_do}?t=${Date.now()}" alt="Biểu đồ tỷ lệ lượt đăng ký có quét mã theo phiên"></div></div>`;
  } catch (e) { $("#kq-qt").innerHTML = `<p class="note loi">${esc(loiText(e))}</p>`; }
};
$("#b-cong-diem").onclick = async () => {
  try {
    const r = await api("/api/cong-diem", { method: "POST", headers: khoa() });
    const nl = r.ngoai_le.map((x) => `<tr><td>${esc(x.ma_sv)}</td><td>${esc(x.ma_phien)}</td><td>${esc(x.ly_do)}</td></tr>`).join("");
    $("#kq-qt").innerHTML = `<div class="kpis"><div class="kpi"><div class="v">${r.du_dieu_kien}</div><b>Đủ điều kiện (Điều 6)</b></div>
      <div class="kpi"><div class="v">${r.cong_moi}</div><b>Cộng mới lần này</b><div class="d">Chạy lại không cộng hai lần</div></div>
      <div class="kpi"><div class="v">${r.ngoai_le.length}</div><b>Ngoại lệ chờ duyệt</b></div></div>
      <div class="two"><div class="box"><b>Hàng đợi ngoại lệ</b><table><tr><th>Mã SV</th><th>Phiên</th><th>Lý do</th></tr>${nl}</table></div>
      <div class="box"><b>Nhật ký</b><div class="trace">${esc(r.nhat_ky)}</div><p class="meta">Tệp: out/cong_diem.csv · out/ngoai_le.csv · out/nhat_ky_cong_diem.txt</p></div></div>`;
  } catch (e) { $("#kq-qt").innerHTML = `<p class="note loi">${esc(loiText(e))}</p>`; }
};
$("#b-poster").onclick = async () => {
  try {
    const r = await api("/api/poster", { method: "POST", headers: khoa() });
    const tp = Object.entries(r.tuong_phan).map(([k, v]) => `<li>${esc(k)}: ${v} : 1 ${v >= 4.5 ? "✓" : "✗"}</li>`).join("");
    const dc = Object.entries(r.doi_chieu).map(([k, v]) => `<li>${esc(k)}: ${v ? "✓" : "✗"}</li>`).join("");
    $("#kq-qt").innerHTML = `<div class="two"><div class="box"><img class="full" src="/${r.poster}?t=${Date.now()}" alt="${esc(r.alt)}"></div>
      <div class="box"><b>Ba phép kiểm</b><p>Tương phản (≥ 4,5 : 1):</p><ul>${tp}</ul><p>Đối chiếu brief:</p><ul>${dc}</ul>
      <p><b>Alt text:</b> ${esc(r.alt)}</p><p class="meta">Lớp nền: ${esc(r.nen)} · lớp chữ: out/poster/chu.png · sổ: out/poster/so_tai_san.csv</p></div></div>`;
  } catch (e) { $("#kq-qt").innerHTML = `<p class="note loi">${esc(loiText(e))}</p>`; }
};

// ---------- Khởi động ----------
api("/api/trang-thai").then((t) => { $("#che-do").textContent = `Mô hình: ${t.llm === "ollama" ? "Ollama · " + t.mo_hinh_sinh : "offline (không dùng LLM)"}`; });
hienNguoi().then(taiPhien);
