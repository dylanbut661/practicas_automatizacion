"""Ejercicio 6 - Suscripcion.

Se registra un correo en la seccion de suscripcion del footer y se valida
el mensaje de exito.
"""
import time

import pytest

from pages.home_page import HomePage
from utils.screenshots import take_screenshot

MENSAJE_ESPERADO = "You have been successfully subscribed!"


@pytest.mark.ej6
def test_suscripcion_con_correo_valido(driver):
    home = HomePage(driver)
    email = f"qa.suscripcion.{int(time.time())}@ejemplo.com"

    # 1. Abrir la pagina principal y bajar al footer
    home.open_home()
    assert "automationexercise.com" in driver.current_url, \
        "No se cargo la pagina principal"
    home.go_to_footer()
    assert home.subscription_title().upper() == "SUBSCRIPTION", \
        "No se muestra la seccion de suscripcion"
    take_screenshot(driver, "ej6_01_seccion_suscripcion")

    # 2. Registrar el correo
    home.subscribe(email)

    # 3. Validar el mensaje de exito
    assert home.find(home.SUCCESS_ALERT).is_displayed(), \
        "No se muestra la alerta de exito"
    assert home.success_text() == MENSAJE_ESPERADO, \
        f"Mensaje inesperado: {home.success_text()!r}"
    take_screenshot(driver, "ej6_02_suscripcion_exitosa")
