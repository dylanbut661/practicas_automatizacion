"""Pagina principal / (seccion de suscripcion del footer, Ejercicio 6)."""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class HomePage(BasePage):
    # Localizadores (tipo indicado a la derecha)
    SUBSCRIPTION_TITLE = (By.XPATH, "//div[@class='single-widget']/h2")      # XPath
    EMAIL_INPUT = (By.ID, "susbscribe_email")                                # ID (el sitio lo escribe asi)
    SUBSCRIBE_BUTTON = (By.CSS_SELECTOR, "button#subscribe")                 # CSS Selector
    SUCCESS_ALERT = (By.CSS_SELECTOR, "#success-subscribe .alert-success")   # CSS Selector

    def open_home(self):
        self.open("/")

    def go_to_footer(self):
        self.scroll_to_bottom()
        self.remove_ads()

    def subscription_title(self) -> str:
        return self.text_of(self.SUBSCRIPTION_TITLE)

    def subscribe(self, email: str):
        self.type(self.EMAIL_INPUT, email)
        self.click(self.SUBSCRIBE_BUTTON)

    def success_text(self) -> str:
        return self.text_of(self.SUCCESS_ALERT)
