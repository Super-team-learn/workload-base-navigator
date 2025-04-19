from bs4 import BeautifulSoup
import requests
import undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
import json
from tqdm import tqdm
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless=new')


url = "https://transport.teletribe.ru/transport/schedule"

driver = uc.Chrome(options=options)
driver.get(url)
time.sleep(1)

for i in range(30):
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    time.sleep(0.5)
elements = driver.find_elements(By.CLASS_NAME, "ts-row ")
hrefs = []
stations = []

for elem in elements:
    t = elem.get_attribute('href')
    z = elem.text
    hrefs.append(t)
    stations.append(z)

info = []
for i in tqdm(range(441+431, len(hrefs))):
    try:
        driver.get(hrefs[i])
        time.sleep(0.01)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        stats = driver.find_elements(By.CLASS_NAME, 'd-inline')
        route = []
        for q in stats:
            route.append(q.text)
        info.append({'station': stations[i], 'route': route})
    except:
        pass

    with open('transport_routes.json', 'a' ,encoding='utf-8') as f:
        json.dump(info, f, indent=4, ensure_ascii=False)

driver.quit()