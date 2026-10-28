import os                                                       # for the file path to the assignment folder
import random                                                   # generates random numbers for unique emails

import pytest                                                   # the test framework that finds and runs test_ functions
from selenium import webdriver                                  # lets Python open and control a real Chrome browser
from selenium.webdriver.common.by import By                     # tells Selenium HOW to find an element (by ID, name, CSS...)
from selenium.webdriver.support.ui import WebDriverWait         # waits for something to happen instead of failing instantly
from selenium.webdriver.support import expected_conditions as EC  # the conditions that can be waited for (visible, clickable...)

SCREENSHOTS = os.path.expanduser("~/Documents/Systems Testing Project/system_testing 2/screenshots")  # the screenshots folder inside system_testing 2 for screenshots of test results

REGISTER_URL = "https://opencart.abstracta.us/index.php?route=account/register"  # the Register Account page
LOGOUT_URL = "https://opencart.abstracta.us/index.php?route=account/logout"      # visiting this logs the user out
PASSWORD = "Test12345!"                                         # a valid password used in every scenario (between 4 and 20 characters)


def unique_email():
    # Every registration needs an email nobody has used before, numbers between 1 and 9999999999999 are generated
    return f"conor.test{random.randint(1, 9999999999999)}@example.com"  # e.g. conor.test1999999999999@example.com


@pytest.fixture                                                 # runs before each test to set up a new browser window
def driver():
    browser = webdriver.Chrome()                                # open a new Chrome window from the selenium webdriver package
    browser.set_window_size(1280, 1000)                         # same window size every run so buttons do not move due to screen sizing
    yield browser                                               # hand the browser to the test; the test runs here
    browser.quit()                                              # after a test, regardless of outcome, the browser is closed


def fill_registration_form(driver, first, last, email, telephone, password, confirm):
    # The same six fields are filled in every scenario when creating an account
    wait = WebDriverWait(driver, 10)                            # wait up to 10 seconds to allow for lag
    wait.until(EC.visibility_of_element_located((By.ID, "input-firstname")))  # wait until the form has loaded and First Name is visible

    driver.find_element(By.ID, "input-firstname").send_keys(first)       # type into the First Name box (HTML id found by inspecting the website)
    driver.find_element(By.ID, "input-lastname").send_keys(last)         # type into the Last Name box
    driver.find_element(By.ID, "input-email").send_keys(email)           # type into the E-Mail box
    driver.find_element(By.ID, "input-telephone").send_keys(telephone)   # type into the Telephone box
    driver.find_element(By.ID, "input-password").send_keys(password)     # type into the Password box
    driver.find_element(By.ID, "input-confirm").send_keys(confirm)       # type into the Password Confirm box


def tick_privacy_policy(driver):
    checkbox = driver.find_element(By.NAME, "agree")            # the Privacy Policy checkbox has name="agree" instead of an "input-..." id like the other fields
    driver.execute_script("document.body.style.zoom='60%'")     # zoom out so the whole form, including the checkbox, is visible
    checkbox.click()                                            # tick the box


def click_continue(driver):
    button = driver.find_element(By.CSS_SELECTOR, "input[value='Continue']")  # the Continue button has no id or name, so it is found by its value
    driver.execute_script("document.body.style.zoom='60%'")     # zoom out so the Continue button is visible
    button.click()                                              # submit the form


# Scenario 1: registration with valid, correctly formatted details is completed and an account is created
def test_1_register_with_valid_details(driver):
    driver.get(REGISTER_URL)                                    # open the Register Account page

    fill_registration_form(driver, "Conor", "Hogan", unique_email(),  # all fields valid, email never used before
                           "0412345678", PASSWORD, PASSWORD)    # password and confirmation match
    tick_privacy_policy(driver)                                 # tick the Privacy Policy box (this also zooms the page out to 60%)
    driver.save_screenshot(os.path.join(SCREENSHOTS, "T001_1_valid_registration-filled-info.png"))  # screenshot of the completed form
    click_continue(driver)                                      # submit

    wait = WebDriverWait(driver, 15)                            # wait up to 15 seconds to allow for lag
    wait.until(EC.url_contains("account/success"))              # wait for the site to move to the success page
    message = driver.find_element(By.CSS_SELECTOR, "#content p").text  # read the first paragraph under the "Account" heading
    driver.save_screenshot(os.path.join(SCREENSHOTS, "T001_1_valid_registration-complete.png"))  # screenshot of the success page

    assert "Your new account has been successfully created!" in message  # PASS if the confirmation message is shown


# Scenario 2: registering with an email that already has an account should result in a warning
def test_2_register_with_existing_email(driver):
    email = unique_email()                                      # one email used twice in this test

    # create an account with this email so that it already exists
    driver.get(REGISTER_URL)                                    # open the Register Account page
    fill_registration_form(driver, "Conor", "Hogan", email, "0412345678", PASSWORD, PASSWORD)  # valid details
    tick_privacy_policy(driver)                                 # tick the Privacy Policy box
    click_continue(driver)                                      # submit
    WebDriverWait(driver, 15).until(EC.url_contains("account/success"))  # make sure the first account was created
    driver.get(LOGOUT_URL)                                      # log out, so the next attempt is made as a new visitor

    # try to register again with the same email as above but different personal details
    driver.get(REGISTER_URL)                                    # open the Register Account page again
    fill_registration_form(driver, "Sofia", "Gwiggner", email, "0400999888", PASSWORD, PASSWORD)  # same email, different details
    tick_privacy_policy(driver)                                 # tick the Privacy Policy box
    click_continue(driver)                                      # submit

    wait = WebDriverWait(driver, 15)                            # wait up to 15 seconds to allow for lag
    warning = wait.until(EC.visibility_of_element_located(      # wait for the red warning to appear at the top of the page
        (By.CSS_SELECTOR, ".alert-danger"))).text               # and read its text
    driver.save_screenshot(os.path.join(SCREENSHOTS, "T001_2_existing_email.png"))  # screenshot of the warning

    assert "E-Mail Address is already registered!" in warning  # the duplicate email is rejected
    assert "account/register" in driver.current_url             # still on the form, no second account created


# Scenario 3: empty first name, passwords that do not match and the policy not ticked should result in errors
def test_3_register_with_invalid_details(driver):
    driver.get(REGISTER_URL)                                    # open the Register Account page

    fill_registration_form(driver, "", "Hogan", unique_email(),  # first name left empty
                           "0400123456", PASSWORD, "NotTheSame123")  # confirmation does not match the password
    # the Privacy Policy box is deliberately NOT ticked
    click_continue(driver)                                      # submit

    wait = WebDriverWait(driver, 15)                            # wait up to 15 seconds to allow for lag
    warning = wait.until(EC.visibility_of_element_located(      # wait for the red warning at the top of the page
        (By.CSS_SELECTOR, ".alert-danger"))).text               # read the text (Privacy Policy message)

    errors = []                                                 # empty list to collect the error messages found
    all_error_messages = driver.find_elements(By.CSS_SELECTOR, ".text-danger")  # find ALL red messages under the form fields
    for error_message in all_error_messages:                    # go through each red message one at a time
        if error_message.text:                                  # skip any that have no text inside
            errors.append(error_message.text)                   # add the message text to the list

    driver.execute_script("document.body.style.zoom='60%'")     # the page reloads at full size after Continue, so zoom out again so every error is in the screenshot
    driver.save_screenshot(os.path.join(SCREENSHOTS, "T001_3_invalid_details.png"))  # screenshot of the warning and errors

    assert "You must agree to the Privacy Policy!" in warning   # the Privacy Policy warning is shown
    assert "First Name must be between 1 and 32 characters!" in errors       # the empty first name is rejected
    assert "Password confirmation does not match password!" in errors        # the mismatched passwords are rejected
    assert "account/register" in driver.current_url             # still on the form, no account created