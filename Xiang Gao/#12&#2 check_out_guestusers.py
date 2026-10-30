from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

driver = webdriver.Chrome()
driver.implicitly_wait(20)
driver.get("https://opencart.abstracta.us/index.php?route=checkout/checkout")
input("Add an in-stock physical product to the cart and open Checkout. "
    "Do not log in. Press Enter when Guest Checkout is visible: ")

guest_option = driver.find_element(
    By.CSS_SELECTOR,
    "input[name='account'][value='guest']"
)
guest_option.click()
assert guest_option.is_selected() == True
print("PASS: Guest Checkout is selected.")
input("Review the selection. Press Enter to continue:")
continue_button = driver.find_element(By.ID, "button-account")
continue_button.click()
input("Check if the guest details appear. Press Enter to continue:")

fname_box = driver.find_element(By.ID, "input-payment-firstname")
fname_box.send_keys("Frank")
lname_box = driver.find_element(By.ID, "input-payment-lastname")
lname_box.send_keys("G")
email_box = driver.find_element(By.ID, "input-payment-email")
email_box.send_keys("frankg@example.com")
telephone_box = driver.find_element(By.ID, "input-payment-telephone")
telephone_box.send_keys("04123345617")
address1_box = driver.find_element(By.ID, "input-payment-address-1")
address1_box.send_keys("Test Street 789")
city_box = driver.find_element(By.ID, "input-payment-city")
city_box.send_keys("Sydney")
postcode_box = driver.find_element(By.ID, "input-payment-postcode")
postcode_box.send_keys("2004")
country_select = Select(driver.find_element(By.ID, "input-payment-country"))
country_select.select_by_visible_text("Australia")
state_select = Select(driver.find_element(By.ID, "input-payment-zone"))
state_select.select_by_visible_text("New South Wales")
continue_button = driver.find_element(By.ID, "button-guest")
driver.execute_script(
    "arguments[0].scrollIntoView({block: 'center'});",
    continue_button
)
input("Check that Continue is not covered. Press Enter to click: ")
continue_button.click()
input("Review the next checkout step. Press Enter to continue: ")

comment_box = driver.find_element(
    By.CSS_SELECTOR,
    "#collapse-shipping-method textarea[name='comment']"
)
comment_box.send_keys("This is a test for the comment box. Ignore it.")
assert comment_box.get_attribute("value") == (
    "This is a test for the comment box. Ignore it."
)
print("PASS: The order comment was entered correctly.")
input("Review the comment. Press Enter to continue: ")
continue_delivery_button = driver.find_element(By.ID, "button-shipping-method")
driver.execute_script(
    "arguments[0].scrollIntoView({block: 'center'});",
    continue_delivery_button
)
input("Check that Continue is not covered. Press Enter to click: ")
continue_delivery_button.click()

input("Press Enter to see the step 5")

payment_option = driver.find_element(
    By.CSS_SELECTOR,
    "#collapse-payment-method input[name='payment_method'][value='cod']"
)
payment_option.click()

assert payment_option.is_selected() == True
print("PASS: Cash On Delivery is selected.")

terms_checkbox = driver.find_element(
    By.CSS_SELECTOR,
    "#collapse-payment-method input[name='agree']"
)

if not terms_checkbox.is_selected():
    terms_checkbox.click()

assert terms_checkbox.is_selected() == True
print("PASS: Terms and Conditions are accepted.")

payment_continue = driver.find_element(
    By.ID, "button-payment-method"
)
driver.execute_script(
    "arguments[0].scrollIntoView({block: 'center'});",
    payment_continue
)
input(
    "Review the payment method and terms. "
    "Check that Continue is not covered. Press Enter to continue: "
)
payment_continue.click()

input(
    "Wait for Step 6: Confirm Order. Review the product, quantity "
    "and total. Press Enter to prepare order submission: "
)

confirm_button = driver.find_element(By.ID, "button-confirm")
assert confirm_button.is_displayed() == True
print("PASS: The Confirm Order button is visible.")
driver.execute_script(
    "arguments[0].scrollIntoView({block: 'center'});",
    confirm_button
)
input(
    "The next action will PLACE THE ORDER on the demo website. "
    "Check that Confirm Order is not covered. Press Enter to submit: "
)
confirm_button.click()

input("Wait for the order result page. Press Enter to check: ")

heading = driver.find_element(
    By.CSS_SELECTOR, "#content h1"
).text
print("Actual page heading:", heading)
print("Actual URL:", driver.current_url)
assert heading == "Your order has been placed!", (
    "FAIL: The expected order confirmation heading was not found."
)
print("PASS: The expected order confirmation heading was displayed.")
input("Save your result screenshot. Press Enter to close the browser: ")
driver.quit()






