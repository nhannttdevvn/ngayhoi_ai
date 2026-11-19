"""In 3 đoạn tìm được cho một câu hỏi — bước đầu tiên khi gỡ lỗi RAG."""
import sys

import _goc  # noqa: F401
from app import rag

if __name__ == "__main__":
    for diem, d in rag.tim(sys.argv[1]):
        print(f"{diem:.3f}  {d['nguon']}")
    print(f"Ngưỡng ({rag.che_do()}): {rag.nguong()}")
