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
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = undetected_chromedriver.Chrome(options=chrome_options)
    return driver


def download_images_with_selenium(url, save_folder='stations'):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    driver = setup_driver()

    try:
        driver.get(url)
        time.sleep(3)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        img_tags = soup.find_all('img')


        for i, img in enumerate(img_tags, 1):
            img_url = img.get('src') or img.get('data-src')

            img_url = urljoin(url, img_url)

            try:
                img_data = requests.get(img_url, stream=True).content
                img_name = os.path.join(save_folder, f"img_{i}.png")

                with open(img_name, 'wb') as f:
                    f.write(img_data)

            except Exception as e:
                print(f"Ошибка при загрузке изображения {img_url}: {e}")

    except Exception as e:
        print(f"Ошибка при обработке страницы: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    target_url = "https://yandex.ru/images/search?from=tabbar&text=фото%20остановок%20c%20людьми"
    download_images_with_selenium(target_url)
