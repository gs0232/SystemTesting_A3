import os
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "https://opencart.abstracta.us/"
SCREENSHOT_FOLDER = "screenshots"
PRICE_SELECTOR = ".product-thumb .price"


@pytest.fixture(scope="module")
def driver():
    browser = webdriver.Safari()
    browser.set_window_size(1280, 1000)

    yield browser

    browser.quit()


def reset_home_page(driver):
    """
    Start each scenario on the OpenCart home page.
    """
    driver.get(BASE_URL)

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, PRICE_SELECTOR)
        )
    )

def reset_to_usd(driver):
    """
    Ensure the website starts in US Dollars before each scenario.
    """
    reset_home_page(driver)

    current_price = get_product_price(driver)

    if "$" not in current_price:
        select_currency(driver, "USD", "$")


def get_product_price(driver):
    """
    Return the displayed price of the first featured product.
    """
    price = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, PRICE_SELECTOR)
        )
    )

    return price.text


def select_currency(driver, currency_code, expected_symbol):
    """
    Select a currency and wait until the page has updated
    to display the new currency symbol.
    """
    wait = WebDriverWait(driver, 10)

    currency_menu = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#form-currency .dropdown-toggle")
        )
    )
    currency_menu.click()

    currency_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                f"#form-currency button[name='{currency_code}']"
            )
        )
    )
    currency_button.click()

    wait.until(
        lambda d: expected_symbol
        in d.find_element(By.CSS_SELECTOR, PRICE_SELECTOR).text
    )

    return get_product_price(driver)


def take_screenshot(driver, filename):
    os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)

    driver.save_screenshot(
        os.path.join(SCREENSHOT_FOLDER, filename)
    )


def test_f14_scenario_1_switch_to_euro(driver):
    reset_to_usd(driver)

    original_price = get_product_price(driver)

    euro_price = select_currency(
        driver,
        "EUR",
        "€"
    )

    assert "€" in euro_price
    assert euro_price != original_price

    take_screenshot(
        driver,
        "f14_scenario1_euro.png"
    )


def test_f14_scenario_2_switch_to_pound(driver):
    reset_to_usd(driver)

    original_price = get_product_price(driver)

    pound_price = select_currency(
        driver,
        "GBP",
        "£"
    )

    assert "£" in pound_price
    assert pound_price != original_price

    take_screenshot(
        driver,
        "f14_scenario2_pound.png"
    )


def test_f14_scenario_3_switch_back_to_usd(driver):
    reset_to_usd(driver)

    euro_price = select_currency(
        driver,
        "EUR",
        "€"
    )

    assert "€" in euro_price

    usd_price = select_currency(
        driver,
        "USD",
        "$"
    )

    assert "$" in usd_price
    assert usd_price != euro_price

    take_screenshot(
        driver,
        "f14_scenario3_usd.png"
    )