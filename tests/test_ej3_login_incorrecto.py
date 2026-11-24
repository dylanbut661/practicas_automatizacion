"""Ejercicio 3 - Inicio de sesion incorrecto.

Se intenta iniciar sesion con credenciales inexistentes y se valida que el
sistema muestre el mensaje de error y no permita el acceso.
"""
import pytest

from pages.login_page import LoginPage
from utils.screenshots import take_screenshot

EMAIL_INVALIDO = "usuario.inexistente.qa@correo-falso.com"
PASSWORD_INVALIDO = "ClaveIncorrecta#123"
MENSAJE_ESPERADO = "Your email or password is incorrect!"


@pytest.mark.ej3
def test_login_con_credenciales_invalidas(driver):
    login = LoginPage(driver)

    # 1. Abrir la pagina de login
    login.open_login()
    assert "/login" in driver.current_url, "No se cargo la pagina de login"
    assert login.heading_text() == "Login to your account", \
        "No se muestra el formulario de login"
    take_screenshot(driver, "ej3_01_pagina_login")

    # 2. Ingresar credenciales invalidas y enviar
    login.login(EMAIL_INVALIDO, PASSWORD_INVALIDO)
    take_screenshot(driver, "ej3_02_login_enviado")

    # 3. Validar el resultado
    assert login.error_is_displayed(), "No se muestra el mensaje de error"
    assert login.error_text() == MENSAJE_ESPERADO, \
        f"Mensaje inesperado: {login.error_text()!r}"
    assert "/login" in driver.current_url, \
        "El usuario no deberia salir de la pagina de login"
    assert not driver.find_elements("xpath", "//a[contains(text(),'Logged in as')]"), \
        "No deberia aparecer 'Logged in as' con credenciales invalidas"
    take_screenshot(driver, "ej3_03_mensaje_error")
