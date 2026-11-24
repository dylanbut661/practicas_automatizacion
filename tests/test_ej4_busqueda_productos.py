"""Ejercicio 4 - Busqueda de productos.

Se busca un producto por nombre y se valida que todos los resultados
correspondan al criterio de busqueda.
"""
import pytest

from pages.products_page import ProductsPage
from utils.screenshots import take_screenshot

CRITERIO = "Blue Top"


@pytest.mark.ej4
def test_busqueda_de_producto(driver):
    products = ProductsPage(driver)

    # 1. Abrir el catalogo
    products.open_products()
    assert products.title_text().upper() == "ALL PRODUCTS", \
        "No se cargo el catalogo de productos"
    take_screenshot(driver, "ej4_01_catalogo_productos")

    # 2. Buscar el producto
    products.search(CRITERIO)

    # 3. Validar los resultados
    assert products.title_text().upper() == "SEARCHED PRODUCTS", \
        "No se muestra la seccion 'Searched Products'"
    assert "search=" in driver.current_url, "La URL no refleja la busqueda"

    nombres = products.result_names()
    print(f"[resultados] {nombres}")
    assert len(nombres) >= 1, "La busqueda no devolvio productos"
    for nombre in nombres:
        assert CRITERIO.lower() in nombre.lower(), \
            f"El producto {nombre!r} no corresponde al criterio {CRITERIO!r}"
    take_screenshot(driver, "ej4_02_resultados_busqueda")
