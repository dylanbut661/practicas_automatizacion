"""Clase base con acciones comunes reutilizadas por todas las paginas."""
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://automationexercise.com"

# Anuncios de Google que el sitio inyecta y que pueden tapar botones.
_REMOVE_ADS_JS = """
document.querySelectorAll(
  'ins.adsbygoogle, iframe[id^="aswift"], iframe[id^="google_ads"], '
  + 'iframe[src*="googlesyndication"], iframe[src*="doubleclick"]'
).forEach(e => e.remove());
document.body.style.overflow = 'auto';
"""


class BasePage:
    def __init__(self, driver, timeout: int = 15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # ---------- navegacion ----------
    def open(self, path: str = ""):
        self.driver.get(BASE_URL + path)
        self.accept_consent()
        self.remove_ads()

    def accept_consent(self):
        """Cierra el banner de consentimiento de cookies si aparece."""
        try:
            WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.fc-cta-consent"))
            ).click()
        except TimeoutException:
            pass

    def remove_ads(self):
        self.driver.execute_script(_REMOVE_ADS_JS)

    # ---------- acciones ----------
    def find(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator):
        return self.driver.find_elements(*locator)

    def click(self, locator):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        try:
            element.click()
        except ElementClickInterceptedException:
            # Si un anuncio tapa el elemento, se limpia y se hace click por JS.
            self.remove_ads()
            self.driver.execute_script("arguments[0].click();", element)

    def type(self, locator, text: str):
        element = self.find(locator)
        element.clear()
        element.send_keys(text)

    def text_of(self, locator) -> str:
        return self.find(locator).text.strip()

    def scroll_to_bottom(self):
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )
