"""支持 `python -m scholar_skill_pack` 调用。"""
from .cli import main
import sys

if __name__ == "__main__":
    sys.exit(main() or 0)
