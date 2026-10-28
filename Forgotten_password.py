import os                                                       # for the file path to the assignment folder
import random                                                   # generates random numbers for unique emails

import pytest                                                   # the test framework that finds and runs test_ functions
from selenium import webdriver                                  # lets Python open and control a real Chrome browser
from selenium.webdriver.common.by import By                     # tells Selenium HOW to find an element (by ID, name, CSS...)
from selenium.webdriver.support.ui import WebDriverWait         # waits for something to happen instead of failing instantly
from selenium.webdriver.support import expected_conditions as EC  # the conditions that can be waited for (visible, clickable...)

SCREENSHOTS = os.path.expanduser("~/Documents/Systems Testing Project/system_testing 2/screenshots")  # the screenshots folder inside system_testing 2 for screenshots of test results

FORGOTTEN_URL = "https://opencart.abstracta.us/index.php?route=account/forgotten"  # the Forgotten Password page
REGISTER_URL = "https://opencart.abstracta.us/index.php?route=account/register"    # the Register Account page
LOGOUT_URL = "https://opencart.abstracta.us/index.php?route=account/logout"        # visiting this logs the user out
PASSWORD = "Test12345!"                                         # the password for the test account
UNKNOWN_EMAIL = "no.account.here@example.com"                   # a correctly formatted email that has never been registered


def unique_email():
    # A new email for the test account, numbers between 1 and 9999999999999 are generated
    return f"conor.test{random.randint(1, 9999999999999)}@example.com"  # e.g. conor.test1999999999999@example.com


@pytest.fixture                                                 # runs before each test to set up a new browser window
def driver():
    browser = webdriver.Chrome()                                # open a new Chrome window from the selenium webdriver package
    browser.set_window_size(1280, 1000)                         # same window size every run so buttons do not move
    yield browser                                               # hand the browser to the test; the test runs here
    browser.quit()                                              # after a test, regardless of outcome, the browser is closed


@pytest.fixture(scope="session")                                # runs once per test run, so every test in this file shares one registered account
def registered_email():
    # A reset link can only be sent to an account that exists, so one is registered first (F1 before F3)
    email = unique_email()                                      # a new email nobody has used
    browser = webdriver.Chrome()                                # a separate window just for creating the account
    browser.get(REGISTER_URL)                                   # open the Register Account page
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "input-firstname")))  # wait for the form
    browser.find_element(By.ID, "input-firstname").send_keys("Conor")      # valid first name
    browser.find_element(By.ID, "input-lastname").send_keys("Hogan")       # valid last name
    browser.find_element(By.ID, "input-email").send_keys(email)            # the new email
    browser.find_element(By.ID, "input-telephone").send_keys("0412345678") # valid telephone number
    browser.find_element(By.ID, "input-password").send_keys(PASSWORD)      # the password
    browser.find_element(By.ID, "input-confirm").send_keys(PASSWORD)       # the same password again
    browser.find_element(By.NAME, "agree").click()              # tick the Privacy Policy box
    browser.find_element(By.CSS_SELECTOR, "input[value='Continue']").click()  # create the account
    WebDriverWait(browser, 15).until(EC.url_contains("account/success"))      # make sure the account was created
    browser.get(LOGOUT_URL)                                     # log out so the tests start as a logged out visitor
    browser.quit()                                              # close the separate window
    return email                                                # every test that needs a real account receives this email


def fill_forgotten_form(driver, email):
    # The Forgotten Password form only has one field, the email address
    wait = WebDriverWait(driver, 10)                            # wait up to 10 seconds to allow for lag
    wait.until(EC.visibility_of_element_located((By.ID, "input-email")))  # wait until the form has loaded and the email field is visible

    driver.find_element(By.ID, "input-email").send_keys(email)  # type into the E-Mail Address box using its HTML id


def click_continue(driver):
    button = driver.find_element(By.CSS_SELECTOR, "input[value='Continue']")  # the Continue button has no id or name, so it is found by its value
    driver.execute_script("document.body.style.zoom='60%'")     # zoom out so the Continue button is visible
    button.click()                                              # submit the form


# Test 1: a registered email is entered, a reset link is sent and the user is taken back to the Login page
def test_1_reset_with_registered_email(driver, registered_email):
    driver.get(FORGOTTEN_URL)                                   # open the Forgotten Password page

    fill_forgotten_form(driver, registered_email)               # email that belongs to an account
    driver.save_screenshot(os.path.join(SCREENSHOTS, "T003_1_registered_email-filled-info.png"))  # screenshot of the completed form
    click_continue(driver)                                      # submit

    wait = WebDriverWait(driver, 15)                            # wait up to 15 seconds to allow for lag
    wait.until(EC.url_contains("account/login"))                # the site sends the user back to the Login page
    message = wait.until(EC.visibility_of_element_located(      # wait for the green success box at the top of the page
        (By.CSS_SELECTOR, ".alert-success"))).text              # read its text
    driver.save_screenshot(os.path.join(SCREENSHOTS, "T003_1_registered_email-complete.png"))  # screenshot of the confirmation

    assert "An email with a confirmation link has been sent your email address." in message  # PASS if the reset link was sent (wording copied exactly from the site)


# Test 2: an email that has no account is entered, which should result in a warning
def test_2_reset_with_unknown_email(driver):
    driver.get(FORGOTTEN_URL)                                   # open the Forgotten Password page

    fill_forgotten_form(driver, UNKNOWN_EMAIL)                  # email that was never registered
    click_continue(driver)                                      # submit

    wait = WebDriverWait(driver, 15)                            # wait up to 15 seconds to allow for lag
    warning = wait.until(EC.visibility_of_element_located(      # wait for the warning to appear at the top of the page
        (By.CSS_SELECTOR, ".alert-danger"))).text               # read its text
    driver.save_screenshot(os.path.join(SCREENSHOTS, "T003_2_unknown_email.png"))  # screenshot of the warning

    assert "The E-Mail Address was not found in our records" in warning  # no reset link for an unknown email
    assert "account/forgotten" in driver.current_url            # still on the Forgotten Password page


# Test 3: the email field is left empty, which should result in a warning
def test_3_reset_with_empty_email(driver):
    driver.get(FORGOTTEN_URL)                                   # open the Forgotten Password page

    fill_forgotten_form(driver, "")                             # nothing typed in the box
    click_continue(driver)                                      # submit

    wait = WebDriverWait(driver, 15)                            # wait up to 15 seconds to allow for lag
    warning = wait.until(EC.visibility_of_element_located(      # wait for the red warning at the top of the page
        (By.CSS_SELECTOR, ".alert-danger"))).text               # read its text
    driver.save_screenshot(os.path.join(SCREENSHOTS, "T003_3_empty_email.png"))  # screenshot of the warning

    assert "The E-Mail Address was not found in our records" in warning  # the request is refused
    assert "account/forgotten" in driver.current_url            # still on the Forgotten Password page