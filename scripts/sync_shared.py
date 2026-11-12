"""Copia `shared/` del raíz dentro de cada demo (azd empaqueta solo la carpeta del servicio).

Uso:  python scripts/sync_shared.py          # copia
      python scripts/sync_shared.py --check  # falla si alguna copia está desactualizada
"""

import filecmp
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "shared"


def destinos() -> list[Path]:
    return [p.parent / "shared" for p in sorted((RAIZ / "demos").glob("*/src/*/main.py"))]


def iguales(a: Path, b: Path) -> bool:
    if not b.exists():
        return False
    cmp = filecmp.dircmp(a, b, ignore=["__pycache__"])
    if cmp.left_only or cmp.right_only or cmp.diff_files:
        return False
    return True


def main() -> int:
    check = "--check" in sys.argv
    mal = 0
    for d in destinos():
        if check:
            if not iguales(ORIGEN, d):
                print(f"DESACTUALIZADO: {d.relative_to(RAIZ)}")
                mal += 1
        else:
            if d.exists():
                shutil.rmtree(d)
            shutil.copytree(ORIGEN, d, ignore=shutil.ignore_patterns("__pycache__"))
            print(f"OK {d.relative_to(RAIZ)}")
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
