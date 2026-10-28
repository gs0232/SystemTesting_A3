import os                                                       # for the file path to the assignment folder
import random                                                   # generates random numbers for unique emails

import pytest                                                   # the test framework that finds and runs test_ functions
from selenium import webdriver                                  # lets Python open and control a real Chrome browser
from selenium.webdriver.common.by import By                     # tells Selenium HOW to find an element (by ID, name, CSS...)
from selenium.webdriver.support.ui import WebDriverWait         # waits for something to happen instead of failing instantly
from selenium.webdriver.support import expected_conditions as EC  # the conditions that can be waited for (visible, clickable...)

SCREENSHOTS = os.path.expanduser("~/Documents/Systems Testing Project/system_testing 2/screenshots")  # the screenshots folder inside system_testing 2 for screenshots of test results

LOGIN_URL = "https://opencart.abstracta.us/index.php?route=account/login"        # the Login page
REGISTER_URL = "https://opencart.abstracta.us/index.php?route=account/register"  # the Register Account page
LOGOUT_URL = "https://opencart.abstracta.us/index.php?route=account/logout"      # visiting this logs the user out
PASSWORD = "Test12345!"                                         # the correct password for the test account
WRONG_PASSWORD = "WrongPassword1"                               # a password that does not belong to the account


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
    # Login can only be tested with an account that exists, so one is registered first (F1 before F2)
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
    return email                                                # every login test that needs a real account receives this email


def fill_login_form(driver, email, password):
    # The same two fields are filled in every login scenario
    wait = WebDriverWait(driver, 10)                            # wait up to 10 seconds to allow for lag
    wait.until(EC.visibility_of_element_located((By.ID, "input-email")))  # wait until the form has loaded and the email field is visible

    driver.find_element(By.ID, "input-email").send_keys(email)           # type into the E-Mail box using its HTML id
    driver.find_element(By.ID, "input-password").send_keys(password)     # type into the Password box using its HTML id


def click_login(driver):
    login = driver.find_element(By.CSS_SELECTOR, "input[value='Login']")  # the Login button has no id or name, so it is found by its value
    driver.execute_script("document.body.style.zoom='60%'")     # zoom out so the Login button is visible
    login.click()                                               # click the Login button


# Test 1: logging in with the correct email and password takes the user to the "My Account" page
def test_1_login_with_valid_credentials(driver, registered_email):
    driver.get(LOGIN_URL)                                       # open the Login page

    fill_login_form(driver, registered_email, PASSWORD)         # correct email and correct password
    driver.save_screenshot(os.path.join(SCREENSHOTS, "T002_1_valid_login-filled-info.png"))  # screenshot of the completed form
    click_login(driver)                                         # submit

    wait = WebDriverWait(driver, 15)                            # wait up to 15 seconds to allow for lag
    wait.until(EC.url_contains("account/account"))              # wait for the site to move to the My Account page
    headings = [h.text for h in driver.find_elements(By.CSS_SELECTOR, "#content h2")]  # section headings on the page
    driver.save_screenshot(os.path.join(SCREENSHOTS, "T002_1_valid_login-complete.png"))  # screenshot of the My Account page

    assert "My Account" in headings                             # PASS if the My Account section is shown


# Test 2: correct email but wrong password should result in a warning
def test_2_login_with_wrong_password(driver, registered_email):
    driver.get(LOGIN_URL)                                       # open the Login page

    fill_login_form(driver, registered_email, WRONG_PASSWORD)   # right email, wrong password
    click_login(driver)                                         # submit

    wait = WebDriverWait(driver, 15)                            # wait up to 15 seconds to allow for lag
    warning = wait.until(EC.visibility_of_element_located(      # wait for the warning to appear at the top of the page
        (By.CSS_SELECTOR, ".alert-danger"))).text               # read its text
    driver.save_screenshot(os.path.join(SCREENSHOTS, "T002_2_wrong_password.png"))  # screenshot of the warning

    assert "No match for E-Mail Address and/or Password." in warning  # login is refused due to the wrong password
    assert "account/login" in driver.current_url                # still on the Login page, not logged in


# Test 3: both fields left empty should result in a warning
def test_3_login_with_empty_fields(driver):
    driver.get(LOGIN_URL)                                       # open the Login page

    fill_login_form(driver, "", "")                             # nothing typed in either box
    click_login(driver)                                         # submit

    wait = WebDriverWait(driver, 15)                            # wait up to 15 seconds to allow for lag
    warning = wait.until(EC.visibility_of_element_located(      # wait for the red warning at the top of the page
        (By.CSS_SELECTOR, ".alert-danger"))).text               # read its text
    driver.save_screenshot(os.path.join(SCREENSHOTS, "T002_3_empty_fields.png"))  # screenshot of the warning

    assert "No match for E-Mail Address and/or Password." in warning  # login is refused
    assert "account/login" in driver.current_url                # still on the Login page