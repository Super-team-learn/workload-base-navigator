import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import time
import undetected_chromedriver


def setup_driver():
    """Настройка и возврат драйвера Selenium"""
    chrome_options = Options()
    #chrome_options.add_argument("--headless")  # Режим без браузера
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = undetected_chromedriver.Chrome(options=chrome_options)
    return driver


def download_images_with_selenium(url, save_folder='stations'):
    """
    Парсит страницу с помощью Selenium, находит все изображения и сохраняет их локально

    :param url: URL страницы для парсинга
    :param save_folder: папка для сохранения изображений
    """
    # Создаем папку для сохранения, если ее нет
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    driver = setup_driver()

    try:
        # Открываем страницу
        driver.get(url)

        # Ждем загрузки страницы (можно настроить по необходимости)
        time.sleep(3)

        # Получаем HTML после выполнения JavaScript
        page_source = driver.page_source

        # Парсим HTML с помощью BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Находим все теги img
        img_tags = soup.find_all('img')

        if not img_tags:
            print("На странице не найдено изображений.")
            return

        print(f"Найдено {len(img_tags)} изображений.")

        # Скачиваем каждое изображение
        for i, img in enumerate(img_tags, 1):
            # Получаем URL изображения
            img_url = img.get('src') or img.get('data-src')

            if not img_url:
                print(f"Изображение {i} не содержит атрибутов src/data-src, пропускаем.")
                continue

            # Собираем абсолютный URL, если он относительный
            img_url = urljoin(url, img_url)

            try:
                # Получаем содержимое изображения
                img_data = requests.get(img_url, stream=True).content

                # Извлекаем имя файла из URL
                img_name = os.path.join(save_folder, f"img_{i}.png")

                # Сохраняем изображение
                with open(img_name, 'wb') as f:
                    f.write(img_data)

                print(f"Сохранено изображение {i}: {img_name}")

            except Exception as e:
                print(f"Ошибка при загрузке изображения {img_url}: {e}")

    except Exception as e:
        print(f"Ошибка при обработке страницы: {e}")
    finally:
        driver.quit()


# Пример использования
if __name__ == "__main__":
    target_url = "https://yandex.ru/images/search?from=tabbar&text=фото%20остановок%20c%20людьми"  # Замените на нужный URL
    download_images_with_selenium(target_url)