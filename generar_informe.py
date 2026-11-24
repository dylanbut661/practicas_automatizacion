"""Genera el informe PDF de la practica a partir de la ejecucion REAL de las pruebas.

Uso (despues de correr `pytest`):
    python generar_informe.py --git-url https://github.com/<usuario>/practicas_automatizacion \
                              --autor "Nombre Apellido"

Toma:
  - reports/resultados.xml  -> resultado, tiempo y mensaje de cada test (JUnit)
  - screenshots/*.png       -> capturas de pantalla como evidencia
  - tests/ y pages/         -> codigo relevante mostrado en el informe
Si falta alguna captura o resultado, el informe lo indica en lugar de inventarlo.
"""
import argparse
import re
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
from datetime import datetime
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image, KeepTogether, PageBreak, Paragraph, Preformatted,
    SimpleDocTemplate, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parent

EJERCICIOS = [
    {
        "num": 3,
        "titulo": "Ejercicio 3 - Inicio de sesión incorrecto",
        "test": "tests/test_ej3_login_incorrecto.py",
        "page": "pages/login_page.py",
        "test_id": "test_login_con_credenciales_invalidas",
        "escenario": (
            "Se abre la página /login de automationexercise.com, se ingresan un correo y "
            "una contraseña que no existen en el sistema y se envía el formulario. La "
            "prueba verifica que el sistema rechace el acceso mostrando el mensaje de "
            "error correspondiente y que el usuario permanezca en la página de login."
        ),
        "locators": [
            ("Título del formulario", "CSS Selector", ".login-form h2"),
            ("Campo correo", "CSS Selector", "input[data-qa='login-email']"),
            ("Campo contraseña", "Name", "password"),
            ("Botón Login", "XPath", "//button[@data-qa='login-button']"),
            ("Mensaje de error", "XPath", "//form[@action='/login']//p[contains(text(),'incorrect')]"),
        ],
        "asserts": [
            "La URL contiene /login al abrir la página (se cargó el login).",
            "El título del formulario es 'Login to your account'.",
            "El mensaje de error se muestra en pantalla (is_displayed).",
            "El texto del error es exactamente 'Your email or password is incorrect!'.",
            "El usuario sigue en /login después del intento fallido.",
            "No aparece el texto 'Logged in as' (no se inició sesión).",
        ],
        "capturas": [
            ("ej3_01_pagina_login", "Página de login antes de ingresar datos"),
            ("ej3_02_login_enviado", "Formulario con credenciales inválidas completado"),
            ("ej3_03_mensaje_error", "Mensaje de error mostrado por el sistema"),
        ],
    },
    {
        "num": 4,
        "titulo": "Ejercicio 4 - Búsqueda de productos",
        "test": "tests/test_ej4_busqueda_productos.py",
        "page": "pages/products_page.py",
        "test_id": "test_busqueda_de_producto",
        "escenario": (
            "Se abre el catálogo /products, se busca el producto 'Blue Top' con el "
            "buscador y se valida que la página de resultados corresponda a una búsqueda "
            "y que cada producto listado coincida con el criterio ingresado."
        ),
        "locators": [
            ("Título de sección", "CSS Selector", "h2.title.text-center"),
            ("Campo de búsqueda", "ID", "search_product"),
            ("Botón de búsqueda", "ID", "submit_search"),
            ("Nombres de producto", "XPath", "//div[contains(@class,'features_items')]//div[@class='productinfo text-center']/p"),
        ],
        "asserts": [
            "El título del catálogo es 'ALL PRODUCTS' antes de buscar.",
            "Tras buscar, el título cambia a 'SEARCHED PRODUCTS'.",
            "La URL contiene el parámetro 'search='.",
            "La búsqueda devuelve al menos un producto.",
            "Cada producto listado contiene el criterio 'Blue Top' en su nombre.",
        ],
        "capturas": [
            ("ej4_01_catalogo_productos", "Catálogo completo antes de buscar"),
            ("ej4_02_resultados_busqueda", "Resultados de la búsqueda 'Blue Top'"),
        ],
    },
    {
        "num": 6,
        "titulo": "Ejercicio 6 - Suscripción",
        "test": "tests/test_ej6_suscripcion.py",
        "page": "pages/home_page.py",
        "test_id": "test_suscripcion_con_correo_valido",
        "escenario": (
            "Se abre la página principal, se desplaza hasta el footer, se registra un "
            "correo único (generado con la hora actual) en la sección Subscription y se "
            "valida el mensaje de éxito."
        ),
        "locators": [
            ("Título de la sección", "XPath", "//div[@class='single-widget']/h2"),
            ("Campo correo", "ID", "susbscribe_email"),
            ("Botón de suscripción", "CSS Selector", "button#subscribe"),
            ("Alerta de éxito", "CSS Selector", "#success-subscribe .alert-success"),
        ],
        "asserts": [
            "La página principal carga (la URL pertenece a automationexercise.com).",
            "El título de la sección es 'SUBSCRIPTION'.",
            "La alerta de éxito se muestra en pantalla (is_displayed).",
            "El texto de la alerta es exactamente 'You have been successfully subscribed!'.",
        ],
        "capturas": [
            ("ej6_01_seccion_suscripcion", "Sección de suscripción en el footer"),
            ("ej6_02_suscripcion_exitosa", "Mensaje de suscripción exitosa"),
        ],
    },
]


def leer_resultados() -> dict:
    """Devuelve {nombre_test: (estado, segundos, detalle)} desde el XML de JUnit."""
    xml = ROOT / "reports" / "resultados.xml"
    resultados = {}
    if not xml.exists():
        return resultados
    for case in ET.parse(xml).getroot().iter("testcase"):
        fallo = case.find("failure")
        error = case.find("error")
        omitido = case.find("skipped")
        if fallo is not None or error is not None:
            nodo = fallo if fallo is not None else error
            estado, detalle = "FALLÓ", (nodo.get("message") or "")[:300]
        elif omitido is not None:
            estado, detalle = "OMITIDO", ""
        else:
            estado, detalle = "APROBADO", ""
        resultados[case.get("name")] = (estado, float(case.get("time", 0)), detalle)
    return resultados


def bloque_locators(page_file: str) -> str:
    """Extrae el bloque de localizadores de la clase (hasta el primer 'def')."""
    texto = (ROOT / page_file).read_text(encoding="utf-8")
    inicio = texto.index("class ")
    fin = texto.index("    def ", inicio)
    return texto[inicio:fin].rstrip()


def imagen_escalada(path: Path, ancho_max=16 * cm, alto_max=9 * cm) -> Image:
    w, h = PILImage.open(path).size
    escala = min(ancho_max / w, alto_max / h)
    return Image(str(path), width=w * escala, height=h * escala)


def construir(args):
    base = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=base["Heading1"], fontSize=18, spaceAfter=8)
    h2 = ParagraphStyle("h2", parent=base["Heading2"], fontSize=13, spaceBefore=10, spaceAfter=4)
    normal = ParagraphStyle("n", parent=base["BodyText"], fontSize=10, leading=14)
    code = ParagraphStyle("c", fontName="Courier", fontSize=6.8, leading=8.2,
                          backColor=colors.HexColor("#F3F4F6"), borderPadding=4)
    caption = ParagraphStyle("cap", parent=normal, fontSize=8.5, textColor=colors.HexColor("#555555"),
                             alignment=1, spaceAfter=8)
    cell = ParagraphStyle("cell", parent=normal, fontSize=8.5, leading=11)

    resultados = leer_resultados()
    historia = []

    # ---- Portada ----
    historia += [
        Paragraph("Práctica 2 - Selenium WebDriver", h1),
        Paragraph("Automatización de pruebas con Python sobre https://automationexercise.com", normal),
        Spacer(1, 8),
        Paragraph(f"<b>Autor:</b> {escape(args.autor)}", normal),
        Paragraph(f"<b>Fecha de generación:</b> {datetime.now():%d/%m/%Y %H:%M}", normal),
        Paragraph(f"<b>Repositorio Git (proyecto practicas automatizacion):</b> {escape(args.git_url)}", normal),
        Spacer(1, 8),
        Paragraph(
            "Se resolvieron únicamente tres ejercicios: <b>3</b> (Inicio de sesión incorrecto), "
            "<b>4</b> (Búsqueda de productos) y <b>6</b> (Suscripción). El proyecto usa Selenium "
            "WebDriver con Python, pytest y el patrón Page Object.", normal),
    ]

    # ---- Resumen ----
    filas = [["Ejercicio", "Asserts", "Capturas", "Resultado", "Tiempo"]]
    for ej in EJERCICIOS:
        est, seg, _ = resultados.get(ej["test_id"], ("SIN EJECUTAR", 0, ""))
        n_caps = sum((ROOT / "screenshots" / f"{c}.png").exists() for c, _ in ej["capturas"])
        filas.append([f"Ej. {ej['num']}", str(len(ej["asserts"])),
                      f"{n_caps}/{len(ej['capturas'])}", est, f"{seg:.1f} s" if seg else "-"])
    tabla = Table(filas, hAlign="LEFT", colWidths=[2.5 * cm, 2.5 * cm, 2.5 * cm, 3.5 * cm, 2.5 * cm])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9CA3AF")),
    ]))
    historia += [Paragraph("Resumen de resultados", h2), tabla]

    # ---- Un bloque por ejercicio ----
    for ej in EJERCICIOS:
        historia += [PageBreak(), Paragraph(ej["titulo"], h1)]

        historia += [Paragraph("Escenario", h2), Paragraph(ej["escenario"], normal)]

        filas = [["Elemento", "Tipo", "Localizador"]] + [
            [Paragraph(a, cell), Paragraph(b, cell), Paragraph(c.replace("&", "&amp;").replace("<", "&lt;"), cell)]
            for a, b, c in ej["locators"]
        ]
        t = Table(filas, colWidths=[3.8 * cm, 2.6 * cm, 10.4 * cm], hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9CA3AF")),
            ("FONTSIZE", (0, 0), (-1, 0), 8.5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        historia += [Paragraph("Localizadores utilizados", h2), t]

        historia += [Paragraph("Código relevante - localizadores (Page Object)", h2),
                     Preformatted(bloque_locators(ej["page"]), code)]
        historia += [Paragraph("Código relevante - prueba", h2),
                     Preformatted((ROOT / ej["test"]).read_text(encoding="utf-8").strip(), code)]

        historia += [Paragraph("Asserts implementados", h2)]
        for a in ej["asserts"]:
            historia.append(Paragraph(f"• {a}", normal))

        historia += [Paragraph("Capturas de pantalla de la ejecución", h2)]
        for nombre, desc in ej["capturas"]:
            ruta = ROOT / "screenshots" / f"{nombre}.png"
            if ruta.exists():
                historia.append(KeepTogether([imagen_escalada(ruta),
                                              Paragraph(f"{nombre}.png - {desc}", caption)]))
            else:
                historia.append(Paragraph(
                    f"<b>[Captura no disponible: {nombre}.png]</b> - ejecute las pruebas "
                    f"y vuelva a generar el informe.", normal))

        est, seg, detalle = resultados.get(ej["test_id"], ("SIN EJECUTAR", 0, ""))
        historia += [Paragraph("Resultado obtenido", h2),
                     Paragraph(f"Estado: <b>{est}</b>" + (f" - duración {seg:.1f} s" if seg else ""), normal)]
        if detalle:
            historia.append(Paragraph(f"Detalle: {escape(detalle)}", normal))
        if est == "SIN EJECUTAR":
            historia.append(Paragraph(
                "No hay resultados en reports/resultados.xml. Ejecute <font name='Courier'>pytest</font> primero.", normal))

    # ---- Cómo ejecutar ----
    historia += [PageBreak(), Paragraph("Cómo ejecutar el proyecto", h1),
                 Preformatted(
                     "pip install -r requirements.txt\n"
                     "pytest                      # navegador visible\n"
                     "HEADLESS=1 pytest           # sin interfaz grafica (Linux/Mac)\n"
                     "python generar_informe.py --git-url <URL> --autor \"<Nombre>\"", code)]

    SimpleDocTemplate(str(ROOT / args.salida), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                      topMargin=2 * cm, bottomMargin=2 * cm,
                      title="Práctica 2 - Selenium WebDriver").build(historia)
    print(f"Informe generado: {ROOT / args.salida}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--git-url", default="https://github.com/<usuario>/practicas_automatizacion")
    p.add_argument("--autor", default="<Nombre del estudiante>")
    p.add_argument("--salida", default="Informe_Practica2_Selenium.pdf")
    construir(p.parse_args())
