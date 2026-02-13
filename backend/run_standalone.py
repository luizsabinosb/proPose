#!/usr/bin/env python3
"""
Launcher standalone do backend - usado pelo executável PyInstaller.
Não modifica a lógica do core; apenas inicia o uvicorn.
"""
import sys
import os
from pathlib import Path

# Path raiz: no PyInstaller é _MEIPASS; em dev é parent de backend
if getattr(sys, "frozen", False):
    _root = Path(sys._MEIPASS)
else:
    _root = Path(__file__).resolve().parent.parent

# backend/app é o pacote app; precisa de backend no path
sys.path.insert(0, str(_root / "backend"))
sys.path.insert(0, str(_root))
os.chdir(str(_root))

if __name__ == "__main__":
    import uvicorn
    from app.main import app
    uvicorn.run(app, host="0.0.0.0", port=8000)
