"""Mỗi lần chạy test dùng một cơ sở dữ liệu tạm và chế độ offline — không đụng dữ liệu thật, không cần Ollama."""
import os
import sys
import tempfile
from pathlib import Path

_tmp = tempfile.mkdtemp()
os.environ["DB_PATH"] = os.path.join(_tmp, "test.db")
os.environ["OUT_DIR"] = _tmp
os.environ["LLM_MODE"] = "offline"
os.environ["ADMIN_KEY"] = "khoa-test"
os.environ["THOI_DIEM"] = "2026-11-10T09:00:00"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import db as csdl  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def k():
    c = csdl.ket_noi()
    csdl.nap_csv(c)
    c.execute("DELETE FROM da_cong")
    yield c
    c.close()


@pytest.fixture()
def client(k):
    with TestClient(app) as c:
        yield c


def sv(ma="22020001"):
    return {"X-Ma-SV": ma}
