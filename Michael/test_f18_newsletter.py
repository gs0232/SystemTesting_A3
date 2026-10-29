import os
import random
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


REGISTER_URL = "https://opencart.abstracta.us/index.php?route=account/register"
LOGIN_URL = "https://opencart.abstracta.us/index.php?route=account/login"
LOGOUT_URL = "https://opencart.abstracta.us/index.php?route=account/logout"
NEWSLETTER_URL = "https://opencart.abstracta.us/index.php?route=account/newsletter"

PASSWORD = "Test12345!"
SCREENSHOT_FOLDER = "screenshots"


def unique_email():
    return f"michael.test{random.randint(1, 9999999999999)}@example.com"


@pytest.fixture(scope="module")
def driver():
    browser = webdriver.Safari()
    browser.set_window_size(1280, 1000)

    yield browser

    browser.quit()


@pytest.fixture(scope="module")
def registered_email(driver):
    """
    Create one new account that can be reused
    for the newsletter subscription tests.
    """

    email = unique_email()

    driver.get(REGISTER_URL)

    wait = WebDriverWait(driver, 15)

    wait.until(
        EC.visibility_of_element_located(
            (By.ID, "input-firstname")
        )
    )

    email_field = driver.find_element(
        By.ID, "input-email"
    )

    password_field = driver.find_element(
        By.ID, "input-password"
    )

    confirm_field = driver.find_element(
        By.ID, "input-confirm"
    )

    type_exactly(
        driver,
        email_field,
        email
    )

    type_exactly(
        driver,
        password_field,
        PASSWORD
    )

    type_exactly(
        driver,
        confirm_field,
        PASSWORD
    )

    driver.find_element(
        By.ID, "input-firstname"
    ).send_keys("Michael")

    driver.find_element(
        By.ID, "input-lastname"
    ).send_keys("Richmond")

    driver.find_element(
        By.ID, "input-telephone"
    ).send_keys("0412345678")

    privacy = driver.find_element(
        By.NAME, "agree"
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        privacy
    )

    privacy.click()

    continue_button = driver.find_element(
        By.CSS_SELECTOR,
        "input[value='Continue']"
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        continue_button
    )

    continue_button.click()

    wait.until(
        EC.url_contains("account/success")
    )

    driver.get(LOGOUT_URL)

    return email

def type_exactly(driver, element, text):
    """
    Type text into a field and verify Safari entered it correctly.
    If Safari drops characters, set the exact value directly.
    """
    element.clear()
    element.send_keys(text)

    if element.get_attribute("value") != text:
        driver.execute_script(
            """
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
            arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
            """,
            element,
            text
        )

    assert element.get_attribute("value") == text


def login(driver, email):
    """
    Ensure the test account is logged in.
    If the user is already logged in, keep the current session.
    Otherwise log in using the registered account.
    """

    wait = WebDriverWait(driver, 15)

    driver.get(NEWSLETTER_URL)

    wait.until(
        lambda d:
        "account/newsletter" in d.current_url
        or "account/login" in d.current_url
    )

    if "account/newsletter" in driver.current_url:
        return

    email_field = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "input-email")
        )
    )

    password_field = driver.find_element(
        By.ID,
        "input-password"
    )

    type_exactly(
        driver,
        email_field,
        email
    )

    type_exactly(
        driver,
        password_field,
        PASSWORD
    )

    login_button = driver.find_element(
        By.CSS_SELECTOR,
        "input[value='Login']"
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        login_button
    )

    login_button.click()

    wait.until(
        EC.url_contains(
            "account/account"
        )
    )


def set_newsletter(driver, value):
    """
    Set newsletter preference.

    value = "1" means Subscribe
    value = "0" means Unsubscribe
    """

    driver.get(NEWSLETTER_URL)

    wait = WebDriverWait(driver, 15)

    radio = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                f"input[name='newsletter'][value='{value}']"
            )
        )
    )

    if not radio.is_selected():
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            radio
        )
        radio.click()

    continue_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "input[value='Continue']"
            )
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        continue_button
    )

    continue_button.click()

    wait.until(
        lambda d: "account/newsletter"
        not in d.current_url
    )

    driver.get(NEWSLETTER_URL)

    saved_radio = wait.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                f"input[name='newsletter'][value='{value}']"
            )
        )
    )

    return saved_radio.is_selected()


def take_screenshot(driver, filename):
    os.makedirs(
        SCREENSHOT_FOLDER,
        exist_ok=True
    )

    driver.save_screenshot(
        os.path.join(
            SCREENSHOT_FOLDER,
            filename
        )
    )


def test_f18_scenario_1_subscribe(
    driver,
    registered_email
):
    login(
        driver,
        registered_email
    )

    saved = set_newsletter(
        driver,
        "1"
    )

    assert saved is True

    take_screenshot(
        driver,
        "f18_scenario1_subscribed.png"
    )


def test_f18_scenario_2_unsubscribe(
    driver,
    registered_email
):
    login(
        driver,
        registered_email
    )

    saved = set_newsletter(
        driver,
        "0"
    )

    assert saved is True

    take_screenshot(
        driver,
        "f18_scenario2_unsubscribed.png"
    )


def test_f18_scenario_3_logged_out_access(
    driver
):
    driver.get(LOGOUT_URL)

    driver.get(NEWSLETTER_URL)

    WebDriverWait(
        driver,
        15
    ).until(
        EC.url_contains(
            "account/login"
        )
    )

    assert "account/login" in driver.current_url

    take_screenshot(
        driver,
        "f18_scenario3_login_required.png"
    )