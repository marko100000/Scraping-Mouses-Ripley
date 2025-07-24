from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Función para configurar y abrir el navegador
def configurar_navegador(chromedriver_path):
    options = Options()
    options.add_argument("--start-maximized")
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Función para cargar la página y hacer scroll para cargar más productos
def cargar_pagina(driver, url):
    driver.get(url)
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "catalog-product-details__name"))
        )
    except TimeoutException:
        print("No se pudo encontrar los productos en el tiempo esperado.")
    
    # Hacer scroll para cargar más productos
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(6):  # Realiza 6 desplazamientos hacia abajo
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Función para extraer los datos de los productos
def extraer_datos(driver):
    productos = driver.find_elements(By.CLASS_NAME, "catalog-product-item")
    data = []

    for producto in productos:
        try:
            nombre = producto.find_element(By.CLASS_NAME, "catalog-product-details__name").text
        except:
            nombre = None

        try:
            marca = producto.find_element(By.CLASS_NAME, "brand-logo").text
        except:
            marca = None

        try:
            precio_regular = producto.find_element(By.CLASS_NAME, "catalog-prices__list-price").text
            precio_regular = precio_regular.replace("S/", "").replace(",", "")
        except:
            precio_regular = None

        try:
            precio_oferta = producto.find_element(By.CLASS_NAME, "catalog-prices__offer-price").text
            precio_oferta = precio_oferta.replace("S/", "").replace(",", "")
        except:
            precio_oferta = None

        try:
            descuento = producto.find_element(By.CLASS_NAME, "catalog-product-details__discount-tag").text
            descuento = descuento.replace("-", "").replace("%", "")
        except:
            descuento = None

        data.append({
            "nombre": nombre,
            "marca": marca,
            "precio_regular": precio_regular,
            "precio_oferta": precio_oferta,
            "descuento": descuento
        })
    
    return data

# Función para procesar y limpiar los datos extraídos
def procesar_datos(data):
    if not data:
        return None

    df = pd.DataFrame(data)

    # Convertir precios y descuento a numérico
    df["precio_regular"] = pd.to_numeric(df["precio_regular"], errors="coerce")
    df["precio_oferta"] = pd.to_numeric(df["precio_oferta"], errors="coerce")
    df["descuento"] = pd.to_numeric(df["descuento"], errors="coerce")

    # Eliminar duplicados
    df = df.drop_duplicates()

    # Ordenar por mayor descuento
    df = df.sort_values(by="descuento", ascending=False)

    return df

# Función para hacer análisis de los datos
def analisis_datos(df):
    # Promedio de descuento por marca
    promedio_descuento = df.groupby("marca")["descuento"].mean().sort_values(ascending=False)
    print("\nPromedio de descuento por marca:")
    print(promedio_descuento)

    # Correlación entre precio regular y precio de oferta
    corr = df[["precio_regular", "precio_oferta"]].corr()
    print("\nCorrelación entre precio regular y precio de oferta:")
    print(corr)

    # Distribución de descuentos
    plt.figure(figsize=(10, 5))
    sns.histplot(df["descuento"].dropna(), bins=10, kde=True)
    plt.title("Distribución de descuentos")
    plt.xlabel("Descuento (%)")
    plt.ylabel("Cantidad de productos")
    plt.tight_layout()
    plt.show()

# Función para guardar los datos procesados en un archivo Excel
def guardar_excel(df, archivo="mouses_ripley.xlsx"):
    df.to_excel(archivo, index=False)
    print(f"\n Archivo Excel guardado correctamente como '{archivo}'.")
    os.startfile(archivo)

# Función principal
def main():
    chromedriver_path = "C:/Users/ASUS/Downloads/SeleniumDrivers/chromedriver-win64/chromedriver.exe"
    url = "https://simple.ripley.com.pe/tecnologia/computacion-gamer/mouse-gamer?s=mdco&type=catalog"
    
    # Paso 1: Configuración y apertura del navegador
    driver = configurar_navegador(chromedriver_path)
    
    # Paso 2: Cargar la página y hacer scroll para cargar más productos
    cargar_pagina(driver, url)
    
    # Paso 3: Extraer los datos de los productos
    data = extraer_datos(driver)
    
    # Paso 4: Cerrar el navegador
    driver.quit()

    # Paso 5: Procesar los datos extraídos
    df = procesar_datos(data)

    if df is not None:
        # Mostrar los top 5 con mayor descuento
        print("\nTop 5 productos con mayor descuento:")
        print(df.head())

        # Filtrar productos con oferta menor a 50
        baratos = df[df["precio_oferta"] < 50]
        print(f"\nProductos con precio oferta menor a 50 soles: {len(baratos)}")
        print(baratos[["nombre", "precio_oferta"]])

        # Análisis adicional
        analisis_datos(df)

        # Guardar los datos como Excel
        guardar_excel(df)
    else:
        print(" No se encontró ningún producto para procesar.")

# Ejecutar el script
if __name__ == "__main__":
    main()
