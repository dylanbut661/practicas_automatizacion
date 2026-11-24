"""Utilidad para guardar capturas de pantalla como evidencia de ejecucion."""
from pathlib import Path

SCREENSHOT_DIR = Path(__file__).resolve().parent.parent / "screenshots"


def take_screenshot(driver, name: str) -> Path:
    """Guarda una captura en screenshots/<name>.png y devuelve su ruta.

    Los nombres son deterministas (ej3_01_pagina_login, ...) para que el
    generador del informe PDF pueda localizarlas.
    """
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    path = SCREENSHOT_DIR / f"{name}.png"
    driver.save_screenshot(str(path))
    print(f"[captura] {path.name}")
    return path
