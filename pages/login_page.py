"""Pagina /login de automationexercise.com (Ejercicio 3)."""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    # Localizadores (tipo indicado a la derecha)
    LOGIN_HEADING = (By.CSS_SELECTOR, ".login-form h2")                      # CSS Selector
    EMAIL_INPUT = (By.CSS_SELECTOR, "input[data-qa='login-email']")          # CSS Selector
    PASSWORD_INPUT = (By.NAME, "password")                                   # Name
    LOGIN_BUTTON = (By.XPATH, "//button[@data-qa='login-button']")           # XPath
    ERROR_MESSAGE = (                                                        # XPath
        By.XPATH, "//form[@action='/login']//p[contains(text(),'incorrect')]"
    )

    def open_login(self):
        self.open("/login")

    def login(self, email: str, password: str):
        self.type(self.EMAIL_INPUT, email)
        self.type(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def heading_text(self) -> str:
        return self.text_of(self.LOGIN_HEADING)

    def error_text(self) -> str:
        return self.text_of(self.ERROR_MESSAGE)

    def error_is_displayed(self) -> bool:
        return self.find(self.ERROR_MESSAGE).is_displayed()
