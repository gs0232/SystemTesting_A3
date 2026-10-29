import os                                                       # for the file path to the assignment folder

import pytest                                                   # the test framework that finds and runs test_ functions
from selenium import webdriver                                  # lets Python open and control a real Chrome browser
from selenium.common.exceptions import StaleElementReferenceException  # raised when the page redraws an element we were just reading
from selenium.webdriver.common.by import By                     # tells Selenium HOW to find an element (by ID, name, CSS...)
from selenium.webdriver.support.ui import WebDriverWait         # waits for something to happen instead of failing instantly
from selenium.webdriver.support import expected_conditions as EC  # the conditions that can be waited for (visible, clickable...)

SCREENSHOTS = os.path.expanduser("/Users/sophiagwiggner/Uni/MGST_5/31282_System_Testing/A3/screenshots")  # the folder where the screenshots of the test results are saved
os.makedirs(SCREENSHOTS, exist_ok=True)                         # create that folder if it does not exist yet, so saving a screenshot cannot fail

HOME_URL = "https://opencart.abstracta.us/"                                                  # the home page (shows the featured products)
IPHONE_URL = "https://opencart.abstracta.us/index.php?route=product/product&product_id=40"   # product detail page of the iPhone (no options to choose)
CINEMA_URL = "https://opencart.abstracta.us/index.php?route=product/product&product_id=42"   # product detail page of the Apple Cinema 30" (many required options)
CART_URL = "https://opencart.abstracta.us/index.php?route=checkout/cart"                     # the Shopping Cart page


@pytest.fixture                                                 # runs before each test to set up a new browser window
def driver():
    browser = webdriver.Chrome()                                # open a new Chrome window from the selenium webdriver package
    browser.set_window_size(1280, 1000)                         # same window size every run so buttons do not move
    yield browser                                               # hand the browser to the test; the test runs here
    browser.quit()                                              # after a test, regardless of outcome, the browser is closed


def take_screenshot(driver, filename):
    driver.execute_script("document.body.style.zoom='60%'")     # zoom out so the whole page, including the alert and the cart, is in the screenshot
    driver.save_screenshot(os.path.join(SCREENSHOTS, filename))  # save the screenshot in the screenshots folder


def cart_summary(driver):
    # The small cart in the top bar shows text like "2 item(s) - $246.40"
    return driver.find_element(By.ID, "cart-total").get_attribute("textContent").strip()  # textContent also works if the text is hidden on a narrow window


def wait_for_cart_summary(driver, expected):
    # The top bar cart is redrawn a moment after the success message, so wait until it shows the expected text
    WebDriverWait(driver, 15, ignored_exceptions=(StaleElementReferenceException,)).until(  # keep trying if the element is redrawn while reading it
        lambda d: expected in d.find_element(By.ID, "cart-total").get_attribute("textContent"))  # e.g. "2 item(s)"


def click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)  # scroll so the element is in the middle of the window
    element.click()                                             # click it


def click_add_to_cart(driver):
    button = driver.find_element(By.ID, "button-cart")          # the Add to Cart button on the product detail page has the id "button-cart"
    click(driver, button)                                       # click the Add to Cart button


# Scenario 1: adding a product with a quantity of 2 from the product detail page puts it in the cart
def test_1_add_product_from_detail_page(driver):
    driver.get(IPHONE_URL)                                      # open the iPhone detail page

    wait = WebDriverWait(driver, 15)                            # wait up to 15 seconds to allow for lag
    wait.until(EC.visibility_of_element_located((By.ID, "input-quantity")))  # wait until the page has loaded and the Qty box is visible
    quantity = driver.find_element(By.ID, "input-quantity")     # the Qty box
    quantity.clear()                                            # remove the default quantity of 1
    quantity.send_keys("2")                                     # type a quantity of 2
    take_screenshot(driver, "T004_1_detail_page-filled-info.png")  # screenshot of the product page with the quantity entered
    click_add_to_cart(driver)                                   # submit

    message = wait.until(EC.visibility_of_element_located(      # wait for the green success message to appear at the top of the page
        (By.CSS_SELECTOR, ".alert-success"))).text              # read its text
    wait_for_cart_summary(driver, "2 item(s)")                  # wait until the cart in the top bar counts 2 items
    take_screenshot(driver, "T004_1_added_to_cart_1.png")         # screenshot of the success message and the updated cart

    driver.get(CART_URL)                                        # open the Shopping Cart page to check what is really in the cart
    cart_quantity = wait.until(EC.visibility_of_element_located(  # wait for the quantity box of the product in the cart
        (By.CSS_SELECTOR, "#content input[name^='quantity']"))).get_attribute("value")  # read the number inside it
    take_screenshot(driver, "T004_1_added_to_cart_2.png")

    assert "You have added" in message and "iPhone" in message  # PASS if the success message names the iPhone
    assert cart_quantity == "2"                                 # the cart holds 2 of them


# Scenario 2: adding a product straight from its preview (the product box on the home page) puts it in the cart
def test_2_add_product_from_product_preview(driver):
    driver.get(HOME_URL)                                        # open the home page with the featured products

    wait = WebDriverWait(driver, 15)                            # wait up to 15 seconds to allow for lag
    button = wait.until(EC.visibility_of_element_located(       # wait for the Add to Cart button of the MacBook box (product id 43)
        (By.CSS_SELECTOR, "button[onclick*=\"cart.add('43'\"]")))  # the button has no id, so it is found by the product id inside its onclick
    take_screenshot(driver, "T004_2_home_page-before-adding.png")  # screenshot before adding, the cart is still empty
    click(driver, button)                                       # click Add to Cart on the product box

    message = wait.until(EC.visibility_of_element_located(      # wait for the green success message
        (By.CSS_SELECTOR, ".alert-success"))).text              # read its text
    wait_for_cart_summary(driver, "1 item(s)")                  # wait until the cart in the top bar counts 1 item
    take_screenshot(driver, "T004_2_added_from_preview.png")    # screenshot of the success message and the updated cart

    assert "You have added" in message and "MacBook" in message  # PASS if the success message names the MacBook
    assert "1 item(s)" in cart_summary(driver)                  # the cart holds exactly 1 item


# Scenario 3: adding a product that has required options without choosing any should result in errors and an empty cart
def test_3_add_product_without_required_options(driver):
    driver.get(CINEMA_URL)                                      # open the Apple Cinema 30" detail page (it has many required options)

    wait = WebDriverWait(driver, 15)                            # wait up to 15 seconds to allow for lag
    wait.until(EC.visibility_of_element_located((By.ID, "button-cart")))  # wait until the page has loaded
    click_add_to_cart(driver)                                   # submit without choosing a radio button, checkbox, text, date etc.

    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".text-danger")))  # wait for the first red error message under an option

    errors = []                                                 # empty list to collect the error messages found
    all_error_messages = driver.find_elements(By.CSS_SELECTOR, ".text-danger")  # find ALL red messages under the option fields
    for error_message in all_error_messages:                    # go through each red message one at a time
        if error_message.text:                                  # skip any that have no text inside
            errors.append(error_message.text)                   # add the message text to the list

    take_screenshot(driver, "T004_3_required_options.png")      # screenshot of the red error messages

    assert len(errors) > 0                                      # at least one option is reported as missing
    assert all("required" in error for error in errors)         # every message says that the option is required, e.g. "Radio required!"
    assert "0 item(s)" in cart_summary(driver)                  # nothing was added, the cart is still empty
