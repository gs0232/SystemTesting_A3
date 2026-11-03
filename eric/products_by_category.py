import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


# Const OpenCart homepage
BASE_URL = "https://opencart.abstracta.us/index.php?route=common/home"


# Set up a fresh browser instance for each test
@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1440,1000")

    browser = webdriver.Chrome(options=options)
    browser.get(BASE_URL)

    yield browser

    browser.quit()


# Test scenario 1: Browse products within a main category
def test_browse_main_category(driver):

    # wait for web page to load
    wait = WebDriverWait(driver, 10)

    # locate the desktops category in the navigation menu
    desktops_category = wait.until(
        EC.visibility_of_element_located(
            (By.LINK_TEXT, "Desktops")
        )
    )

    # move the mouse over the desktops category
    ActionChains(driver).move_to_element(
        desktops_category
    ).perform()

    # wait for the show all desktops button to appear
    show_all_desktops = wait.until(
        EC.element_to_be_clickable(
            (By.LINK_TEXT, "Show All Desktops")
        )
    )

    # click the show all desktops button
    show_all_desktops.click()

    # wait for desktops category page to load
    wait.until(
        EC.title_contains("Desktops")
    )

    # verify the desktops category page is displayed
    assert "Desktops" in driver.title


# Test scenario 2: Browse products within a subcategory
def test_browse_subcategory(driver):

    # wait for web page to load
    wait = WebDriverWait(driver, 10)

    # locate the components category in the navigation menu
    components_category = wait.until(
        EC.visibility_of_element_located(
            (By.LINK_TEXT, "Components")
        )
    )

    # move the mouse over the components category
    ActionChains(driver).move_to_element(
        components_category
    ).perform()

    # wait for the monitors subcategory to appear
    monitors_category = wait.until(
        EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Monitors"))
    )

    # click the monitors subcategory
    monitors_category.click()

    # wait for monitors category page to load
    wait.until(
        EC.title_contains("Monitors")
    )

    # verify the monitors category page is displayed
    assert "Monitors" in driver.title


# Test scenario 3: Navigate from desktops to laptops and notebooks
def test_navigate_between_categories(driver):

    # wait for web page to load
    wait = WebDriverWait(driver, 10)

    # locate the desktops category in the navigation menu
    desktops_category = wait.until(
        EC.visibility_of_element_located(
            (By.LINK_TEXT, "Desktops")
        )
    )

    # move the mouse over the desktops category
    ActionChains(driver).move_to_element(
        desktops_category
    ).perform()

    # wait for the show all desktops button to appear
    show_all_desktops = wait.until(
        EC.element_to_be_clickable(
            (By.LINK_TEXT, "Show All Desktops")
        )
    )

    # click the show all desktops button
    show_all_desktops.click()

    # wait for desktops category page to load
    wait.until(
        EC.title_contains("Desktops")
    )

    # locate the laptops and notebooks category in the navigation menu
    laptops_category = wait.until(
        EC.visibility_of_element_located(
            (By.LINK_TEXT, "Laptops & Notebooks")
        )
    )

    # move the mouse over the laptops and notebooks category
    ActionChains(driver).move_to_element(
        laptops_category
    ).perform()

    # wait for the show all laptops and notebooks button to appear
    show_all_laptops = wait.until(
        EC.element_to_be_clickable(
            (By.LINK_TEXT, "Show All Laptops & Notebooks")
        )
    )

    # click the show all laptops and notebooks button
    show_all_laptops.click()

    # wait for laptops and notebooks category page to load
    wait.until(
        EC.title_contains("Laptops & Notebooks")
    )

    # verify the laptops and notebooks category page is displayed
    assert "Laptops & Notebooks" in driver.title