import os                                                       # for the file path to the assignment folder
import random                                                   # generates random numbers for unique emails

import pytest                                                   # the test framework that finds and runs test_ functions
from selenium import webdriver                                  # lets Python open and control a real Chrome browser
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException  # errors we expect and handle while waiting
from selenium.webdriver.common.by import By                     # tells Selenium HOW to find an element (by ID, name, CSS...)
from selenium.webdriver.support.ui import Select, WebDriverWait  # Select works with drop-down lists; WebDriverWait waits instead of failing instantly
from selenium.webdriver.support import expected_conditions as EC  # the conditions that can be waited for (visible, clickable...)

SCREENSHOTS = os.path.expanduser("/Users/sophiagwiggner/Uni/MGST_5/31282_System_Testing/A3/screenshots")  # the folder where the screenshots of the test results are saved
os.makedirs(SCREENSHOTS, exist_ok=True)                         # create that folder if it does not exist yet, so saving a screenshot cannot fail

REGISTER_URL = "https://opencart.abstracta.us/index.php?route=account/register"  # the Register Account page
LOGIN_URL = "https://opencart.abstracta.us/index.php?route=account/login"        # the Login page
CHECKOUT_URL = "https://opencart.abstracta.us/index.php?route=checkout/checkout"  # the Checkout page
IPHONE_URL = "https://opencart.abstracta.us/index.php?route=product/product&product_id=40"  # product detail page of the iPhone (no options to choose)
PASSWORD = "Test12345!"                                         # the password of the test account


def unique_email():
    # A new email for the test account, numbers between 1 and 9999999999999 are generated
    return f"sophia.test{random.randint(1, 9999999999999)}@example.com"  # e.g. sophia.test1999999999999@example.com


@pytest.fixture                                                 # runs before each test to set up a new browser window
def driver():
    browser = webdriver.Chrome()                                # open a new Chrome window from the selenium webdriver package
    browser.set_window_size(1280, 1000)                         # same window size every run so buttons do not move
    yield browser                                               # hand the browser to the test; the test runs here
    browser.quit()                                              # after a test, regardless of outcome, the browser is closed


@pytest.fixture                                                 # runs before each test, so every test gets its own new account
def registered_email():
    # Checkout: Registered User needs an account that exists, so one is registered first (F1 before F6)
    # Every test gets a new account, because the first checkout saves an address to the account and the next test must start without one
    email = unique_email()                                      # a new email nobody has used
    browser = webdriver.Chrome()                                # a separate window just for creating the account
    browser.set_window_size(1280, 1000)                         # same window size as the tests
    browser.get(REGISTER_URL)                                   # open the Register Account page
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "input-firstname")))  # wait for the form
    browser.find_element(By.ID, "input-firstname").send_keys("Sophia")     # valid first name
    browser.find_element(By.ID, "input-lastname").send_keys("Gwiggner")    # valid last name
    browser.find_element(By.ID, "input-email").send_keys(email)            # the new email
    browser.find_element(By.ID, "input-telephone").send_keys("0412345678") # valid telephone number
    browser.find_element(By.ID, "input-password").send_keys(PASSWORD)      # the password
    browser.find_element(By.ID, "input-confirm").send_keys(PASSWORD)       # the same password again
    agree = browser.find_element(By.NAME, "agree")              # the Privacy Policy checkbox
    browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", agree)  # scroll so the checkbox is visible
    agree.click()                                               # tick the Privacy Policy box
    browser.find_element(By.CSS_SELECTOR, "input[value='Continue']").click()  # create the account
    WebDriverWait(browser, 15).until(EC.url_contains("account/success"))      # make sure the account was created
    browser.quit()                                              # close the separate window
    return email                                                # the test receives this email


def take_screenshot(driver, filename):
    driver.execute_script("document.body.style.zoom='60%'")     # zoom out so the whole checkout page is in the screenshot
    driver.save_screenshot(os.path.join(SCREENSHOTS, filename))  # save the screenshot in the screenshots folder


def click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)  # scroll so the element is in the middle of the window
    element.click()                                             # click it


def log_in(driver, email):
    # Logs in on the Login page like in F2
    driver.get(LOGIN_URL)                                       # open the Login page
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "input-email")))  # wait until the form has loaded
    driver.find_element(By.ID, "input-email").send_keys(email)  # type into the E-Mail box
    driver.find_element(By.ID, "input-password").send_keys(PASSWORD)  # type into the Password box
    click(driver, driver.find_element(By.CSS_SELECTOR, "input[value='Login']"))  # click the Login button (found by its value, it has no id)
    WebDriverWait(driver, 15).until(EC.url_contains("account/account"))  # wait for the My Account page, so the user is surely logged in


def add_iphone_to_cart(driver):
    # Something has to be in the cart to check out (F4 before F6)
    driver.get(IPHONE_URL)                                      # open the iPhone detail page
    wait = WebDriverWait(driver, 15)                            # wait up to 15 seconds to allow for lag
    click(driver, wait.until(EC.visibility_of_element_located((By.ID, "button-cart"))))  # click Add to Cart
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-success")))   # wait for the success message so the iPhone is surely in the cart


def fill_billing_address(driver, first, last, address, city, postcode):
    # Step 2 of the checkout: the billing details of a logged in user without a saved address are a form
    wait = WebDriverWait(driver, 15, ignored_exceptions=(StaleElementReferenceException,))  # wait up to 15 seconds, ignore elements being redrawn
    wait.until(EC.visibility_of_element_located((By.ID, "input-payment-firstname")))  # wait until the form has loaded

    driver.find_element(By.ID, "input-payment-firstname").send_keys(first)    # type into the First Name box
    driver.find_element(By.ID, "input-payment-lastname").send_keys(last)      # type into the Last Name box
    driver.find_element(By.ID, "input-payment-address-1").send_keys(address)  # type into the Address 1 box
    driver.find_element(By.ID, "input-payment-city").send_keys(city)          # type into the City box
    driver.find_element(By.ID, "input-payment-postcode").send_keys(postcode)  # type into the Post Code box

    wait.until(lambda d: d.find_element(By.ID, "input-payment-country").is_enabled())  # the site locks the country list while it loads the regions, so wait until it is unlocked
    wait.until(lambda d: len(Select(d.find_element(By.ID, "input-payment-zone")).options) > 1)  # and until the first region list has been loaded
    Select(driver.find_element(By.ID, "input-payment-country")).select_by_visible_text("Australia")  # choose the country from the drop-down list
    wait.until(lambda d: any(option.text == "New South Wales"   # the regions are loaded after the country is chosen, so wait until the region list contains it
                             for option in Select(d.find_element(By.ID, "input-payment-zone")).options))
    Select(driver.find_element(By.ID, "input-payment-zone")).select_by_visible_text("New South Wales")  # choose the region from the drop-down list


def click_billing_continue(driver):
    click(driver, driver.find_element(By.ID, "button-payment-address"))  # the Continue button of the billing details step has the id "button-payment-address"


def finish_checkout_steps(driver):
    # Steps 3 to 6: delivery details, delivery method, payment method and confirming the order
    wait = WebDriverWait(driver, 20)                            # wait up to 20 seconds, every step is loaded from the server

    try:                                                        # Step 3 (Delivery Details) only appears if the site asks for it, so it is optional
        WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.ID, "button-shipping-address"))).click()  # the saved address is already selected, just continue
    except TimeoutException:                                    # no Step 3 was shown
        pass                                                    # nothing to do, go on with the next step

    click(driver, wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#collapse-shipping-method input[name='shipping_method']"))))  # Step 4: Delivery Method, choose the first delivery method in the list (clicking one that is already selected changes nothing)
    click(driver, wait.until(EC.element_to_be_clickable((By.ID, "button-shipping-method"))))  # click Continue
    click(driver, wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#collapse-payment-method input[name='payment_method']"))))  # Step 5: Payment Method, no method is selected by default, so choose the first one in the list
    click(driver, wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#collapse-payment-method input[name='agree']"))))  # tick the Terms & Conditions box
    take_screenshot(driver, "T006_1_payment_step.png")            # screenshot of the payment method step
    click(driver, wait.until(EC.element_to_be_clickable((By.ID, "button-payment-method"))))   # click Continue
    click(driver, wait.until(EC.element_to_be_clickable((By.ID, "button-confirm"))))          # Step 6: Confirm Order, click the Confirm Order button


# Scenario 1: a logged in user checks out the cart with a new billing address and the order is placed
def test_1_checkout_as_logged_in_user(driver, registered_email):
    log_in(driver, registered_email)                            # log in with the registered account (F2)
    add_iphone_to_cart(driver)                                  # put an iPhone in the cart (F4)
    driver.get(CHECKOUT_URL)                                    # open the Checkout page

    fill_billing_address(driver, "Sophia", "Gwiggner", "1 Test Street", "Sydney", "2000")  # valid billing details
    take_screenshot(driver, "T006_1_billing-filled-info.png")   # screenshot of the completed billing form
    click_billing_continue(driver)                              # submit the billing details
    finish_checkout_steps(driver)                               # delivery, payment and confirm

    wait = WebDriverWait(driver, 30)                            # wait up to 30 seconds, placing the order takes a moment
    wait.until(EC.url_contains("checkout/success"))             # wait for the site to move to the order success page
    heading = driver.find_element(By.CSS_SELECTOR, "#content h1").text  # read the heading of the success page
    take_screenshot(driver, "T006_1_checkout-complete.png")     # screenshot of the order success page

    assert "Your order has been placed!" in heading             # PASS if the order confirmation is shown


# Scenario 2: a logged out user who opens the checkout must log in first, then Step 1 (Checkout Options) is skipped
def test_2_checkout_logged_out_requires_login(driver, registered_email):
    add_iphone_to_cart(driver)                                  # put an iPhone in the cart as a logged out visitor (F4)
    driver.get(CHECKOUT_URL)                                    # open the Checkout page

    wait = WebDriverWait(driver, 20)                            # wait up to 20 seconds to allow for lag
    wait.until(EC.visibility_of_element_located((By.ID, "button-login")))  # Step 1: wait until the login form (Returning Customer) is shown
    driver.find_element(By.ID, "input-email").send_keys(registered_email)  # type into the E-Mail box of the checkout login form
    driver.find_element(By.ID, "input-password").send_keys(PASSWORD)       # type into the Password box
    take_screenshot(driver, "T006_2_checkout_login-filled-info.png")  # screenshot of the login form on the checkout page
    login_button = driver.find_element(By.ID, "button-login")   # the Login button of the checkout login form
    click(driver, login_button)                                 # submit
    wait.until(EC.staleness_of(login_button))                   # wait until the old page is gone, which means the page reloaded after logging in

    wait.until(EC.visibility_of_element_located((By.ID, "input-payment-firstname")))  # wait for the billing form
    titles = [t.text for t in driver.find_elements(By.CSS_SELECTOR, "#accordion .panel-title")]  # the titles of all checkout steps
    take_screenshot(driver, "T006_2_checkout_login-complete.png")  # screenshot of the checkout page after logging in

    assert "checkout/checkout" in driver.current_url            # still on the Checkout page
    assert driver.find_elements(By.ID, "button-login") == []    # the login form is no longer shown, the user is logged in
    assert any("Billing Details" in t for t in titles)          # the checkout continues with the billing details


# Scenario 3: billing details left empty should result in errors and the checkout does not continue
def test_3_checkout_with_empty_billing_details(driver, registered_email):
    log_in(driver, registered_email)                            # log in with the registered account (F2)
    add_iphone_to_cart(driver)                                  # put an iPhone in the cart (F4)
    driver.get(CHECKOUT_URL)                                    # open the Checkout page

    wait = WebDriverWait(driver, 20)                            # wait up to 20 seconds to allow for lag
    wait.until(EC.visibility_of_element_located((By.ID, "input-payment-firstname")))  # wait until the billing form has loaded
    click_billing_continue(driver)                              # submit the billing form without filling in anything

    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#collapse-payment-address .text-danger")))  # wait for the first red error message under a field

    errors = []                                                 # empty list to collect the error messages found
    all_error_messages = driver.find_elements(By.CSS_SELECTOR, "#collapse-payment-address .text-danger")  # find ALL red messages under the form fields
    for error_message in all_error_messages:                    # go through each red message one at a time
        if error_message.text:                                  # skip any that have no text inside
            errors.append(error_message.text)                   # add the message text to the list

    take_screenshot(driver, "T006_3_empty_billing_details.png")  # screenshot of the error messages

    required_fields = ["firstname", "lastname", "address-1", "city", "postcode", "zone"]  # the required fields of the billing form (country already has a default value)
    fields_without_error = []                                   # empty list to collect the fields that show no red message
    for field in required_fields:                               # go through each required field one at a time
        message = driver.find_elements(By.CSS_SELECTOR, f"#input-payment-{field} + .text-danger")  # the red message is placed directly after its field
        if not message or not message[0].text:                  # no message found, or an empty one
            fields_without_error.append(field)                  # remember this field

    assert fields_without_error == []                           # every required field shows a red error message
    assert "First Name must be between 1 and 32 characters!" in errors  # the empty first name is rejected
    assert "Last Name must be between 1 and 32 characters!" in errors   # the empty last name is rejected
    assert "checkout/success" not in driver.current_url                 # no order was placed
    assert not any(e.is_displayed() for e in driver.find_elements(By.ID, "button-shipping-method"))  # the checkout did not move on to the delivery method
