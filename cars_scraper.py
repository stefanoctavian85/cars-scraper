import time
import pandas as pd
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

website = "https://www.autovit.ro/autoturisme"
load_dotenv(dotenv_path=".env")
path = os.getenv("CHROMEDRIVER_PATH")

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
service = Service(path)

driver = webdriver.Chrome(service=service, options=options)
driver.get(website)

time.sleep(1)
accept_cookies_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
accept_cookies_button.click()

data_links = []
number = 0
page_number = 0

car_data_list = []

while True:
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2.e1n1d04s0.ooa-1kyyooz.er34gjf0")))
        cars_paragraphs = driver.find_elements(By.CSS_SELECTOR, "h2.e1n1d04s0.ooa-1kyyooz.er34gjf0")

        for car in cars_paragraphs:
            link = car.find_element(By.TAG_NAME, "a").get_attribute("href")
            number = number + 1
            print(str(number) + " " + link)
            data_links.append(link)

        try:
            next_page_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//li[@title="Next Page"]')))
            if "disabled" in next_page_button.get_attribute("class"):
                break

            driver.execute_script("arguments[0].click();", next_page_button)
            page_number = page_number + 1
            print("Page number" + str(page_number))
            time.sleep(2)
        except Exception as e:
            print("No more pages!")
            break
    except Exception as e:
        break

number = 0

for link in data_links:
    try:
        driver.get(link)
        car_info = {}

        try:
            image = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ooa-12np8kw.e142atj30")))
            image_link = image.find_element(By.TAG_NAME, "img").get_attribute("srcset")
            car_info["Imagine"] = image_link
        except Exception as e:
            print("Image not found!")

        technical_specs_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.accordion-item__toggle-button.ooa-9vqtkg")))
        technical_specs_button.click()

        pret = driver.find_element(By.CSS_SELECTOR, "h3.offer-price__number.evnmei44.ooa-1kdys7g.er34gjf0")
        moneda = driver.find_element(By.CSS_SELECTOR, "p.offer-price__currency.evnmei45.ooa-m6bn4u.er34gjf0")
        car_info["Pret"] = pret.text.strip() + moneda.text.strip()

        try:
            tags = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "p.eim4snj7.ooa-y26jp.er34gjf0")))
            details = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "p.eim4snj8.ooa-17xeqrd.er34gjf0")))

            pozitie = 0

            for tag in tags:
                eticheta = tag.text.strip()

                if eticheta == "VIN (serie sasiu)":
                    continue

                if pozitie < len(details):
                    car_info[eticheta] = details[pozitie].text.strip()
                    pozitie += 1

            print(f"Car number {number}")
            # for info in car_info:
            #     print(info + ": " + car_info[info])
            number += 1

            car_data_list.append(car_info)
        except Exception as e:
            print("No specification for this car")

    except Exception as e:
        print(e)

car_data_df = pd.DataFrame(car_data_list)
car_data_df = car_data_df.rename(columns={'Anul producției': 'Anul productiei'})
print(car_data_df)
columns = list(car_data_df.columns)
car_data_df.to_csv("raw/cars_full_dataset.csv", index=False, columns=columns)
