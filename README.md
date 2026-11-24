# Práctica 2 - Selenium WebDriver con Python

Automatización sobre <https://automationexercise.com>. Ejercicios resueltos: **3** (login incorrecto), **4** (búsqueda de productos) y **6** (suscripción).

## Estructura

```
practicas_automatizacion/
├── conftest.py              # fixture del driver + captura automática si un test falla
├── pytest.ini               # opciones: reportes JUnit y HTML
├── requirements.txt
├── generar_informe.py       # genera el PDF con código, capturas y resultados reales
├── pages/                   # Page Objects (localizadores y acciones)
│   ├── base_page.py
│   ├── login_page.py
│   ├── products_page.py
│   └── home_page.py
├── tests/                   # un archivo por ejercicio (aquí están los asserts)
│   ├── test_ej3_login_incorrecto.py
│   ├── test_ej4_busqueda_productos.py
│   └── test_ej6_suscripcion.py
├── utils/screenshots.py
├── screenshots/             # evidencias (se generan al ejecutar)
└── reports/                 # resultados.xml y reporte.html (se generan al ejecutar)
```

## Ejecución

Requiere Python 3.10+ y Google Chrome (Selenium Manager descarga el driver solo).

```bash
pip install -r requirements.txt
pytest                         # un solo ejercicio: pytest -m ej3
python generar_informe.py --git-url https://github.com/<usuario>/practicas_automatizacion --autor "Tu Nombre"
```

Sin ventana de navegador: `HEADLESS=1 pytest` (Linux/Mac) o `set HEADLESS=1 && pytest` (Windows).

## Localizadores usados

| Tipo | Ejemplos |
|---|---|
| ID | `search_product`, `submit_search`, `susbscribe_email` |
| Name | `password` |
| XPath | `//button[@data-qa='login-button']`, `//div[@class='single-widget']/h2` |
| CSS Selector | `input[data-qa='login-email']`, `#success-subscribe .alert-success` |

## Asserts por ejercicio

- **Ej. 3:** 6 (URL de login, título, error visible, texto exacto del error, permanece en /login, no hay sesión iniciada).
- **Ej. 4:** 5 (título antes/después, parámetro `search=` en la URL, hay resultados, cada resultado coincide con el criterio).
- **Ej. 6:** 4 (página principal, título SUBSCRIPTION, alerta visible, texto exacto del éxito).

## Evidencias

Cada ejercicio guarda capturas en `screenshots/` (`ej3_*`, `ej4_*`, `ej6_*`). Si un test falla se guarda además `FALLO_<test>.png`.
