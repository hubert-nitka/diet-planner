import time
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import LOGIN_SITE, DIET_SITE, IMGS_FOLDER_WSL, IMGS_FOLDER_WIN
from src.utils import log, clean_img_name

def scrape_diet_dishes(email, password):
    """
    Gathers complete diet plan from the portal and saves data to json file
    """

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  #uncomment to run without window

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    wait = WebDriverWait(driver, 15)

    try:

        os.makedirs(IMGS_FOLDER_WSL, exist_ok=True)

        log("Logging in...")

        driver.get(LOGIN_SITE)

        wait.until(EC.presence_of_element_located((By.NAME, "email")))

        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CLASS_NAME, "submit").click()

        time.sleep(3)

        log("Logged in")
        log("Gathering diet plan...")

        driver.get(DIET_SITE)

        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "ul.skewed-menu > li.skewed-menu__item")
            )
        )

        dish_type_items = driver.find_elements(
            By.CSS_SELECTOR, "ul.skewed-menu > li.skewed-menu__item"
        )

        log(f"Found {len(dish_type_items)} dish types")

        all_dishes = {}

        for i in range(len(dish_type_items)):
            dish_type_items = driver.find_elements(
                By.CSS_SELECTOR, "ul.skewed-menu > li.skewed-menu__item"
            )

            item = dish_type_items[i]

            button = item.find_element(By.TAG_NAME, "button")
            driver.execute_script("arguments[0].click();", button)
            time.sleep(1.5)

            dish_type = item.find_element(
                                By.CSS_SELECTOR,
                                "span[class*='skewed-menu__label']"
                                ).text.strip()
            
            log(f"Processing dish type: {dish_type}")

            # wait to load more than one dish cards
            wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "div[class*='card']")
                )
            )

            # optional scroll for React lazy-load
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)

            cards = driver.find_elements(
                By.CSS_SELECTOR,
                "div[class*='card']"
            )

            log(f"Found {len(cards)} dish cards")

            dishes = []

            log(f"Karty HTML (pierwsze 3):")
            for card in cards[:3]:
                log(card.get_attribute("outerHTML")[:300])

            for card in cards:

                try:
                    # click dish card and wait to load all dish info
                    header_button = card.find_element(By.CSS_SELECTOR, "button[class*='header']")
                    driver.execute_script("arguments[0].click();", header_button)
                    time.sleep(0.5)

                    # dish name
                    dish_name = card.find_element(By.CSS_SELECTOR, "span[class*='name']").text.strip()

                    # macros
                    dish_macros = card.find_elements(By.CSS_SELECTOR, "span[class*='recipes-v2__macros-element--value']")
                    dish_kcal = dish_macros[0].text.strip()
                    dish_carbs = dish_macros[1].text.replace("g","").strip()
                    dish_proteins = dish_macros[2].text.replace("g","").strip()
                    dish_fats = dish_macros[3].text.replace("g","").strip()
                    
                    # preview image
                    
                    img_element = card.find_element(By.CSS_SELECTOR, "img[class*='recipes-v2__preview-image']")
                    img_url = img_element.get_attribute("src")

                    log(f"Found IMG URL: {img_url}")

                    img_name = clean_img_name(dish_name) + ".png"
                    img_path_wsl = os.path.join(IMGS_FOLDER_WSL, img_name)
                    img_path_win = f"{IMGS_FOLDER_WIN}\\{img_name}"

                    response = requests.get(img_url, stream=True)

                    if response.status_code == 200:
                        with open(img_path_wsl, "wb") as file:
                            for chunk in response.iter_content(1024):
                                file.write(chunk)
                        log(f"IMG {img_name} saved successfuly [{img_path_wsl}]")
                    else:
                        log(f"Error saving IMG [{img_name}]")
                    
                    # prep time and difficulty

                    dish_stats = card.find_element(By.CSS_SELECTOR, "div[class*='recipes-v2__stats']").text.split('\n')
                    dish_prep_time = dish_stats[0].strip()
                    dish_difficulty = dish_stats[1].strip()

                    # ingredients

                    ingredient_elements = card.find_elements(By.CSS_SELECTOR, "li[class*='ingredients-list__item']")
                    dish_ingredients = []

                    for element in ingredient_elements:
                        full_text = element.text.split('\n')
                        ingredient_name = full_text[0].strip()
                        ingredient_amount_full = full_text[1].split(' ')
                        ingredient_amount = float(ingredient_amount_full[0].replace(',', '.'))
                        ingredient_unit = ingredient_amount_full[1].strip()
                        dish_ingredients.append(
                            {
                                'ingredient_name': ingredient_name,
                                'ingredient_amount': ingredient_amount,
                                'ingredient_unit': ingredient_unit
                            }
                        )
                    
                    # instructions

                    instruction_elements = card.find_elements(By.CSS_SELECTOR, "div.instructions li")
                    dish_instructions = '\n'.join([f"{i+1}) {el.text.strip()}" for i, el in enumerate(instruction_elements)])

                    dish_data = {
                        'name': dish_name,
                        'kcal': dish_kcal,
                        'carbs': dish_carbs,
                        'proteins': dish_proteins,
                        'fats': dish_fats,
                        'prep_time': dish_prep_time,
                        'difficulty': dish_difficulty,
                        'ingredients': dish_ingredients,
                        'instructions': dish_instructions,
                        'img_path': img_path_win
                    }

                    dishes.append(dish_data)

                except Exception as e:
                    log(f"Dish error: {e}", level="ERROR")

            log(f"Saved {len(dishes)} dishes")

            all_dishes[dish_type] = dishes

        return all_dishes

    finally:
        driver.quit()
