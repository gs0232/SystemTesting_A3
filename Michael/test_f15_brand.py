import os
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "https://opencart.abstracta.us/"
SCREENSHOT_FOLDER = "screenshots"


@pytest.fixture(scope="module")
def driver():
    browser = webdriver.Safari()
    browser.set_window_size(1280, 1000)

    yield browser

    browser.quit()


def take_screenshot(driver, filename):
    os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)

    driver.save_screenshot(
        os.path.join(SCREENSHOT_FOLDER, filename)
    )


def open_home_page(driver):
    driver.get(BASE_URL)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.LINK_TEXT, "Brands")
        )
    )


def open_brands_page(driver):
    """
    Navigate from the OpenCart home page to the Brands page.
    """
    open_home_page(driver)

    wait = WebDriverWait(driver, 15)

    brands_link = wait.until(
        EC.element_to_be_clickable(
            (By.LINK_TEXT, "Brands")
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        brands_link
    )

    brands_link.click()

    wait.until(
        EC.url_contains("route=product/manufacturer")
    )

    wait.until(
        EC.presence_of_element_located(
            (By.LINK_TEXT, "Apple")
        )
    )


def get_product_names(driver):
    """
    Return the names of products displayed
    on the selected brand page.
    """
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".product-thumb")
        )
    )

    products = driver.find_elements(
        By.CSS_SELECTOR,
        ".product-thumb h4 a"
    )

    return [product.text for product in products]


def test_f15_scenario_1_open_brands_page(driver):
    open_brands_page(driver)

    page_text = driver.page_source

    assert "Find Your Favorite Brand" in page_text

    assert "Apple" in page_text
    assert "Canon" in page_text
    assert "Sony" in page_text

    take_screenshot(
        driver,
        "f15_scenario1_brands_page.png"
    )


def test_f15_scenario_2_browse_apple_products(driver):
    open_brands_page(driver)

    apple_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.LINK_TEXT, "Apple")
        )
    )

    apple_link.click()

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//h2[normalize-space()='Apple']"
            )
        )
    )

    products = get_product_names(driver)

    assert "MacBook" in products
    assert "iPhone" in products
    assert "iMac" in products

    assert len(products) == 10

    take_screenshot(
        driver,
        "f15_scenario2_apple.png"
    )


def test_f15_scenario_3_browse_canon_products(driver):
    open_brands_page(driver)

    canon_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.LINK_TEXT, "Canon")
        )
    )

    canon_link.click()

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//h2[normalize-space()='Canon']"
            )
        )
    )

    products = get_product_names(driver)

    assert "Canon EOS 5D" in products

    assert len(products) == 1

    take_screenshot(
        driver,
        "f15_scenario3_canon.png"
    )