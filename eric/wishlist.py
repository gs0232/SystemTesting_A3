import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Const OpenCart homepage
BASE_URL = "https://opencart.abstracta.us/index.php?route=common/home"


# Set up a fresh browser instance for each test
@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1440,1000")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    browser = webdriver.Chrome(options=options)
    browser.get(BASE_URL)
    yield browser
    browser.quit()


# Log in using the test customer account
def login(driver):
    email = "ericburakowskitest@gmail.com"
    password = "password123"

    wait = WebDriverWait(driver, 10)

    # open the login page
    driver.get(
        "https://opencart.abstracta.us/index.php?route=account/login"
    )

    # locate the email and password fields
    wait.until(
        EC.visibility_of_element_located((By.ID, "input-email"))
    ).send_keys(email)
    driver.find_element(By.ID, "input-password").send_keys(password)

    # click the login button
    driver.find_element(
        By.CSS_SELECTOR, "input[type='submit'][value='Login']"
    ).click()

    # wait for the account page to load
    wait.until(EC.url_contains("route=account/account"))


# Search for a product and open its product page
def open_product(driver, product_name):
    wait = WebDriverWait(driver, 10)

    # locate the search bar
    search_bar = wait.until(
        EC.visibility_of_element_located((By.NAME, "search"))
    )
    search_bar.clear()
    search_bar.send_keys(product_name)

    # click the search button
    driver.find_element(
        By.CSS_SELECTOR, "button.btn-default.btn-lg"
    ).click()

    # wait for the search results to load
    product_links = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div.product-thumb h4 a")
        )
    )

    # open the product whose name matches the requested product
    matching_products = [
        link for link in product_links
        if product_name.lower() in link.text.strip().lower()
    ]

    if not matching_products:
        pytest.fail(f"Could not find a product matching '{product_name}'.")

    matching_products[0].click()

    # wait for the Add to Wish List button to appear
    wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "button[onclick*='wishlist.add']")
        )
    )


# Add the currently open product to the wishlist
def add_current_product_to_wishlist(driver):
    wait = WebDriverWait(driver, 10)

    # locate and click the Add to Wish List button
    wishlist_button = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[onclick*='wishlist.add']")
        )
    )
    wishlist_button.click()

    # wait for the website to respond to the wishlist request
    wait.until(
        lambda browser: (
            browser.find_elements(By.CSS_SELECTOR, ".alert-success")
            or "route=account/login" in browser.current_url
        )
    )


# Retrieve product names from the wishlist table
def get_wishlist_product_names(driver):
    wait = WebDriverWait(driver, 10)

    # open the wishlist page
    driver.get(
        "https://opencart.abstracta.us/index.php?route=account/wishlist"
    )

    # wait for the wishlist table or empty-wishlist message
    wait.until(
        lambda browser: (
            browser.find_elements(By.CSS_SELECTOR, "#content table tbody tr")
            or browser.find_elements(By.CSS_SELECTOR, "#content p")
        )
    )

    # retrieve the product names from the wishlist
    rows = driver.find_elements(
        By.CSS_SELECTOR, "#content table tbody tr"
    )
    return [
        row.find_element(By.CSS_SELECTOR, "td:nth-child(2) a").text.strip()
        for row in rows
    ]


# Test scenario 1: Add a product to the wishlist while logged in
def test_add_product_to_wishlist_while_logged_in(driver):
    login(driver)

    # search for MacBook and open its product page
    open_product(driver, "MacBook")

    # add MacBook to the wishlist
    add_current_product_to_wishlist(driver)

    # verify MacBook appears in the wishlist
    wishlist_products = get_wishlist_product_names(driver)
    assert any("MacBook" in name for name in wishlist_products)


# Test scenario 2: Attempt to add a product to the wishlist while logged out
def test_add_product_to_wishlist_while_logged_out(driver):
    # ensure the user is logged out
    driver.get(
        "https://opencart.abstracta.us/index.php?route=account/logout"
    )
    driver.get(BASE_URL)

    # search for iPhone and open its product page
    open_product(driver, "iPhone")

    # attempt to add iPhone to the wishlist
    add_current_product_to_wishlist(driver)

    # verify the website either requests login or confirms the wishlist action
    login_requested = "route=account/login" in driver.current_url
    success_message = driver.find_elements(
        By.CSS_SELECTOR, ".alert-success"
    )
    assert login_requested or success_message, (
        "The website neither requested login nor displayed a wishlist success message."
    )


# Test scenario 3: Add multiple products to the wishlist
def test_add_multiple_products_to_wishlist(driver):
    login(driver)

    # add each product to the wishlist
    products_to_add = ["MacBook", "iPhone", "Canon EOS 5D"]

    for product_name in products_to_add:
        # search for the product and open its product page
        open_product(driver, product_name)

        # add the product to the wishlist
        add_current_product_to_wishlist(driver)

    # verify all products appear in the wishlist
    wishlist_products = get_wishlist_product_names(driver)

    for product_name in products_to_add:
        assert any(
            product_name.lower() in name.lower()
            for name in wishlist_products
        ), f"{product_name} was not found in the wishlist."

    # verify each product appears only once
    for product_name in products_to_add:
        matching_names = [
            name for name in wishlist_products
            if product_name.lower() in name.lower()
        ]
        assert len(matching_names) == 1, (
            f"{product_name} appears {len(matching_names)} times in the wishlist."
        )
