"""Pagina /products de automationexercise.com (Ejercicio 4)."""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class ProductsPage(BasePage):
    # Localizadores (tipo indicado a la derecha)
    PAGE_TITLE = (By.CSS_SELECTOR, "h2.title.text-center")                   # CSS Selector
    SEARCH_INPUT = (By.ID, "search_product")                                 # ID
    SEARCH_BUTTON = (By.ID, "submit_search")                                 # ID
    PRODUCT_NAMES = (                                                        # XPath
        By.XPATH, "//div[contains(@class,'features_items')]"
                  "//div[@class='productinfo text-center']/p"
    )

    def open_products(self):
        self.open("/products")

    def title_text(self) -> str:
        return self.text_of(self.PAGE_TITLE)

    def search(self, term: str):
        self.type(self.SEARCH_INPUT, term)
        self.click(self.SEARCH_BUTTON)

    def result_names(self) -> list[str]:
        self.find(self.PRODUCT_NAMES)  # espera a que haya al menos un resultado
        # .text de un elemento oculto vuelve vacio; textContent siempre trae el nombre.
        return [
            el.get_attribute("textContent").strip()
            for el in self.find_all(self.PRODUCT_NAMES)
        ]
