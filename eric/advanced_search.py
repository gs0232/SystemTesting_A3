import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# Const OpenCart homepage
BASE_URL = "https://opencart.abstracta.us/index.php?route=common/home"

# Set up a fresh browswer instance for each test
@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1440,1000")

    browser = webdriver.Chrome(options=options)
    browser.get(BASE_URL)

    yield browser

    browser.quit()

# Retrieve the product names from search results
def get_product_names(driver):
    products = driver.find_elements(
        By.CSS_SELECTOR, "div.product-thumb h4 a"
    )

    return [product.text.strip() for product in products]

# Test scenario 1: Seach for product using keyword
def test_search_product_keyword(driver):

    # wait for web page to load
    wait = WebDriverWait(driver, 10)

    # locate teh search bar
    search_bar = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "search")
        )
    )

    # Enter the keyword "MacBook" in the search bar and search for it
    search_bar.send_keys("MacBook")
    search_button = driver.find_element(
        By.CSS_SELECTOR, "#search button"
    )
    search_button.click()

    # wait for the search results to load
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.product-thumb h4 a")
        )
    )

    # get the product names and check they all match the expected result
    product_names = get_product_names(driver)

    expected_products = [
        "MacBook",
        "MacBook Air",
        "MacBook Pro"
    ]

    assert set(product_names) == set(expected_products), (
        f"Expected {expected_products}, but found {product_names}"
    )

    assert len(product_names) == 3

# Test scenario 2: Filter search results by category
def test_filter_search_by_category(driver):

    # wait for web page to load
    wait = WebDriverWait(driver, 10)

    # locate search bar and enter keyword "Pro"
    search_bar = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "search")
        )
    )

    search_bar.send_keys("Pro")

    # click the first search button
    driver.find_element(
        By.CSS_SELECTOR, "#search button"
    ).click()

    # wait for dropdown to load
    category_dropdown = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "category_id")
        )
    )

    # select the laptop and notebooks category
    Select(category_dropdown).select_by_visible_text(
        "Laptops & Notebooks"
    )

    # click the second search button
    driver.find_element(
        By.ID, "button-search"
    ).click()

    # wait for filtered search results
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.product-thumb h4 a")
        )
    )

    # get the product names and verify only the macbook pro is displayed
    product_names = get_product_names(driver)

    expected_products = ["MacBook Pro"]

    assert product_names == expected_products, (
        f"Expected {expected_products}, but found {product_names}"
    )

# Test scenario 3: sort search results by price descending
def test_sort_search_by_price_descending(driver):

    # wait for web page to load
    wait = WebDriverWait(driver, 10)

    # get the search bar
    search_bar = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "search")
        )
    )

    # enter the keyword macbook and search
    search_bar.send_keys("MacBook")

    driver.find_element(
        By.CSS_SELECTOR, "#search button"
    ).click()

    # wait for results to load
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.product-thumb h4 a")
        )
    )

    # locate the sort dropdown
    sort_dropdown = wait.until(
        EC.element_to_be_clickable(
            (By.ID, "input-sort")
        )
    )

    # select "Price (High > Low)"
    Select(sort_dropdown).select_by_visible_text(
        "Price (High > Low)"
    )

    # wait for products to appear and then verify they are in the correct order
    expected_order = [
        "MacBook Pro",
        "MacBook Air",
        "MacBook"
    ]

    wait.until(
        lambda d: get_product_names(d) == expected_order
    )

    actual_order = get_product_names(driver)

    # verify sorting order
    assert actual_order == expected_order, (
        f"Expected order {expected_order}, "
        f"but found {actual_order}"
    )