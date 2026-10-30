from selenium import webdriver
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
options.accept_insecure_certs = True

driver = webdriver.Chrome(options=options)
driver.maximize_window()
driver.implicitly_wait(20)

driver.get(
    "https://opencart.abstracta.us/index.php?route=account/login"
)
input(
    "Log in manually with your dedicated test account. "
    "Press Enter after login is complete: "
)
driver.get(
    "https://opencart.abstracta.us/index.php?route=account/edit"
)
input("Wait for the account details form. Press Enter to continue: ")

firstname_box = driver.find_element(By.ID, "input-firstname")
lastname_box = driver.find_element(By.ID, "input-lastname")
email_box = driver.find_element(By.ID, "input-email")
telephone_box = driver.find_element(By.ID, "input-telephone")

old_firstname = firstname_box.get_attribute("value")
old_lastname = lastname_box.get_attribute("value")
old_email = email_box.get_attribute("value")
old_telephone = telephone_box.get_attribute("value")

print("\nOriginal account details:")
print("First name:", old_firstname)
print("Last name:", old_lastname)
print("Email:", old_email)
print("Telephone:", old_telephone)
print("\nLeave a field blank to keep its original value.")

new_firstname = input("New first name: ").strip()
new_lastname = input("New last name: ").strip()
new_email = input("New email: ").strip()
new_telephone = input("New telephone: ").strip()

if new_firstname == "":
    new_firstname = old_firstname

if new_lastname == "":
    new_lastname = old_lastname

if new_email == "":
    new_email = old_email

if new_telephone == "":
    new_telephone = old_telephone

changed = (
    new_firstname != old_firstname
    or new_lastname != old_lastname
    or new_email != old_email
    or new_telephone != old_telephone
)

assert changed == True, "No changes were entered. Test stopped."

firstname_box.clear()
firstname_box.send_keys(new_firstname)

lastname_box.clear()
lastname_box.send_keys(new_lastname)

email_box.clear()
email_box.send_keys(new_email)

telephone_box.clear()
telephone_box.send_keys(new_telephone)

print("\nExpected account details:")
print("First name:", new_firstname)
print("Last name:", new_lastname)
print("Email:", new_email)
print("Telephone:", new_telephone)

save_button = driver.find_element(
    By.CSS_SELECTOR,
    "#content form input[type='submit']"
)

driver.execute_script(
    "arguments[0].scrollIntoView({block: 'center'});",
    save_button
)
input(
    "Review all four fields. Check that Continue is not covered. "
    "Press Enter to SAVE the changes: "
)
save_button.click()

input("Wait for the result page. Press Enter to inspect the result: ")
print("\nActual page text:")
print(driver.find_element(By.TAG_NAME, "body").text)

input(
    "Review any success or validation messages. "
    "Press Enter to reopen the account details and verify saving: "
)

driver.get(
    "https://opencart.abstracta.us/index.php?route=account/edit"
)

saved_firstname = driver.find_element(
    By.ID, "input-firstname"
).get_attribute("value")

saved_lastname = driver.find_element(
    By.ID, "input-lastname"
).get_attribute("value")

saved_email = driver.find_element(
    By.ID, "input-email"
).get_attribute("value")

saved_telephone = driver.find_element(
    By.ID, "input-telephone"
).get_attribute("value")

print("\nSaved account details:")
print("First name:", saved_firstname)
print("Last name:", saved_lastname)
print("Email:", saved_email)
print("Telephone:", saved_telephone)

assert saved_firstname == new_firstname, (
    "FAIL: The saved first name does not match."
)
print("PASS: First name matches.")

assert saved_lastname == new_lastname, (
    "FAIL: The saved last name does not match."
)
print("PASS: Last name matches.")

assert saved_email == new_email, (
    "FAIL: The saved email does not match."
)
print("PASS: Email matches.")

assert saved_telephone == new_telephone, (
    "FAIL: The saved telephone does not match."
)
print("PASS: Telephone matches.")

print("\nPASS: All four saved values match the expected values.")
print("Use the saved email for your next login:", saved_email)

input("Save your screenshots. Press Enter to close the browser: ")
driver.quit()