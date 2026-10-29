import os                                                       # for the file path to the assignment folder

import pytest                                                   # the test framework that finds and runs test_ functions
from selenium import webdriver                                  # lets Python open and control a real Chrome browser
from selenium.common.exceptions import StaleElementReferenceException  # raised when the page redraws an element we were just reading
from selenium.webdriver.common.by import By                     # tells Selenium HOW to find an element (by ID, name, CSS...)
from selenium.webdriver.support.ui import WebDriverWait         # waits for something to happen instead of failing instantly
from selenium.webdriver.support import expected_conditions as EC  # the conditions that can be waited for (visible, clickable...)

SCREENSHOTS = os.path.expanduser("/Users/sophiagwiggner/Uni/MGST_5/31282_System_Testing/A3/screenshots")  # the folder where the screenshots of the test results are saved
os.makedirs(SCREENSHOTS, exist_ok=True)                         # create that folder if it does not exist yet, so saving a screenshot cannot fail

PRODUCT_URL = "https://opencart.abstracta.us/index.php?route=product/product&product_id="  # a product id is added at the end, e.g. 40
CART_URL = "https://opencart.abstracta.us/index.php?route=checkout/cart"                   # the Shopping Cart page
IPHONE_ID = "40"                                                # product id of the iPhone (no options to choose)
MACBOOK_ID = "43"                                               # product id of the MacBook (no options to choose)


@pytest.fixture                                                 # runs before each test to set up a new browser window
def driver():
    browser = webdriver.Chrome()                                # open a new Chrome window from the selenium webdriver package
    browser.set_window_size(1280, 1000)                         # same window size every run so buttons do not move
    yield browser                                               # hand the browser to the test; the test runs here
    browser.quit()                                              # after a test, regardless of outcome, the browser is closed


def take_screenshot(driver, filename):
    driver.execute_script("document.body.style.zoom='60%'")     # zoom out so the whole cart table is in the screenshot
    driver.save_screenshot(os.path.join(SCREENSHOTS, filename))  # save the screenshot in the screenshots folder


def click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)  # scroll so the element is in the middle of the window
    element.click()                                             # click it


def add_product_to_cart(driver, product_id):
    # The cart can only be updated if it has products in it, so a product is added first (F4 before F5)
    driver.get(PRODUCT_URL + product_id)                        # open the product detail page
    wait = WebDriverWait(driver, 15)                            # wait up to 15 seconds to allow for lag
    button = wait.until(EC.visibility_of_element_located((By.ID, "button-cart")))  # wait for the Add to Cart button
    click(driver, button)                                       # click Add to Cart
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-success")))  # wait for the success message so the product is surely in the cart


def cart_summary(driver):
    # The small cart in the top bar shows text like "2 item(s) - $246.40"
    return driver.find_element(By.ID, "cart-total").get_attribute("textContent").strip()  # textContent also works if the text is hidden on a narrow window


def wait_for_cart_summary(driver, expected):
    # The top bar cart is redrawn a moment after the page loads, so wait until it shows the expected text
    WebDriverWait(driver, 15, ignored_exceptions=(StaleElementReferenceException,)).until(  # keep trying if the element is redrawn while reading it
        lambda d: expected in d.find_element(By.ID, "cart-total").get_attribute("textContent"))  # e.g. "2 item(s)"


def quantity_box(driver, product_name):
    # Finds the quantity box in the row of the cart table that belongs to one product
    return driver.find_element(By.XPATH, f"//div[@id='content']//tr[.//a[normalize-space()='{product_name}']]//input[starts-with(@name,'quantity')]")  # row with this product name, then its quantity box


def click_update(driver):
    button = driver.find_element(By.CSS_SELECTOR, "#content button[data-original-title='Update'], #content button[title='Update']")  # the blue refresh button has no id, only a tooltip text "Update" (#content skips the small cart in the top bar)
    click(driver, button)                                       # click Update


def click_remove(driver, product_name):
    button = driver.find_element(By.XPATH, f"//div[@id='content']//tr[.//a[normalize-space()='{product_name}']]//button[contains(@onclick,'cart.remove')]")  # the red Remove button in the row of this product
    click(driver, button)                                       # click Remove


# Scenario 1: changing the quantity of a product in the cart from 1 to 2 updates the cart
def test_1_update_quantity(driver):
    add_product_to_cart(driver, IPHONE_ID)                      # put 1 iPhone in the cart (F4)
    driver.get(CART_URL)                                        # open the Shopping Cart page

    wait = WebDriverWait(driver, 15)                            # wait up to 15 seconds to allow for lag
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#content input[name^='quantity']")))  # wait until the cart table has loaded
    box = quantity_box(driver, "iPhone")                        # the quantity box of the iPhone
    box.clear()                                                 # remove the old quantity of 1
    box.send_keys("2")                                          # type the new quantity of 2
    take_screenshot(driver, "T005_1_update_quantity-filled-info.png")  # screenshot of the cart with the new quantity typed in
    click_update(driver)                                        # submit

    message = wait.until(EC.visibility_of_element_located(      # wait for the green success message (the page reloads first)
        (By.CSS_SELECTOR, ".alert-success"))).text              # read its text
    new_quantity = quantity_box(driver, "iPhone").get_attribute("value")  # read the quantity again from the reloaded page
    wait_for_cart_summary(driver, "2 item(s)")                  # wait until the cart in the top bar counts 2 items
    take_screenshot(driver, "T005_1_update_quantity-complete.png")  # screenshot of the updated cart

    assert "You have modified your shopping cart" in message    # PASS if the cart reports the change
    assert new_quantity == "2"                                  # the cart now holds 2 iPhones


# Scenario 2: removing the only product from the cart leaves an empty cart
def test_2_remove_product(driver):
    add_product_to_cart(driver, IPHONE_ID)                      # put 1 iPhone in the cart (F4)
    driver.get(CART_URL)                                        # open the Shopping Cart page

    wait = WebDriverWait(driver, 15)                            # wait up to 15 seconds to allow for lag
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#content input[name^='quantity']")))  # wait until the cart table has loaded
    take_screenshot(driver, "T005_2_remove_product-before.png")  # screenshot of the cart before removing
    click_remove(driver, "iPhone")                              # click the red Remove button of the iPhone

    wait.until(EC.text_to_be_present_in_element(                # wait until the page shows the empty cart message
        (By.ID, "content"), "Your shopping cart is empty!"))
    message = driver.find_element(By.ID, "content").text        # read the text of the page content
    take_screenshot(driver, "T005_2_remove_product-complete.png")  # screenshot of the empty cart

    assert "Your shopping cart is empty!" in message            # PASS if the cart is empty
    assert len(driver.find_elements(By.CSS_SELECTOR, "#content input[name^='quantity']")) == 0  # no product rows are left


# Scenario 3: changing the quantity of one product must not change the other product in the cart
def test_3_update_one_of_two_products(driver):
    add_product_to_cart(driver, IPHONE_ID)                      # put 1 iPhone in the cart (F4)
    add_product_to_cart(driver, MACBOOK_ID)                     # put 1 MacBook in the cart as well (F4)
    driver.get(CART_URL)                                        # open the Shopping Cart page

    wait = WebDriverWait(driver, 15)                            # wait up to 15 seconds to allow for lag
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#content input[name^='quantity']")))  # wait until the cart table has loaded
    box = quantity_box(driver, "iPhone")                        # the quantity box of the iPhone only
    box.clear()                                                 # remove the old quantity of 1
    box.send_keys("3")                                          # type the new quantity of 3
    take_screenshot(driver, "T005_3_update_one-filled-info.png")  # screenshot of the cart with the new quantity typed in
    click_update(driver)                                        # submit

    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-success")))  # wait for the success message (the page reloads first)
    iphone_quantity = quantity_box(driver, "iPhone").get_attribute("value")    # quantities read again from the reloaded page
    macbook_quantity = quantity_box(driver, "MacBook").get_attribute("value")
    wait_for_cart_summary(driver, "4 item(s)")                  # 3 iPhones + 1 MacBook = 4 items in the top bar
    take_screenshot(driver, "T005_3_update_one-complete.png")   # screenshot of the updated cart

    assert iphone_quantity == "3"                               # the iPhone was changed
    assert macbook_quantity == "1"                              # the MacBook stayed the same
