import aiohttp
import os
import re
from lxml import html
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Настройки для User-Agent
HEADERS = {"User-Agent": UserAgent().random}

# Функция очистки цены
def clean_price(price_text: str):
    numbers = re.findall(r"\d+", price_text.replace(" ", ""))  # Удаляем пробелы и ищем цифры
    return int("".join(numbers)) if numbers else None

# Функция для получения цены с помощью lxml
async def fetch_price_lxml(url: str, xpath: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as response:
            page_content = await response.text()
            tree = html.fromstring(page_content)
            price = tree.xpath(xpath)
            if price:
                return clean_price(price[0].strip())
            return None

def fetch_price_selenium(url: str, xpath: str):
    options = Options()
    options.add_argument("--headless")  # Запуск браузера в фоновом режиме
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")

    driver_path = "chromedriver.exe"
    if not os.path.exists(driver_path):
        raise FileNotFoundError(f"Chromedriver не найден по пути: {driver_path}")

    # Создание драйвера с указанным драйвером
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

    time.sleep(5)  # Ждём, пока страница полностью загрузится

    try:
        element = driver.find_element(By.XPATH, xpath)
        price = element.text.strip()
        driver.quit()
        return clean_price(price)
    except Exception as e:
        driver.quit()
        print(f"Ошибка при парсинге с Selenium: {e}")
        return None

# Основная функция для получения цены товара
async def get_product_price(url: str, xpath: str):
    price = await fetch_price_lxml(url, xpath)

    if price is None:
        print("Цена не найдена через lxml. Пробуем Selenium...")
        price = fetch_price_selenium(url, xpath)

    return price