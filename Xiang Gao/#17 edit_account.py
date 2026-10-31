from selenium import webdriver
from selenium.webdriver.common.by import By

scenario = input(
    "Choose a scenario:\n"
    "1 = Valid account update\n"
    "2 = Empty first name\n"
    "3 = Invalid email\n"
    "Enter your choice: "
).strip()

assert scenario in ("1", "2", "3"), (
    "Invalid choice. Please enter 1, 2 or 3."
)

print("Selected scenario:", scenario)

options = webdriver.ChromeOptions()
options.accept_insecure_certs = True

driver = webdriver.Chrome(options=options)
driver.maximize_window()
driver.implicitly_wait(20)

driver.get(
    "https://opencart.abstracta.us/index.php?route=account/login"
)

input(
    "Log in manually with your existing test account. "
    "Press Enter after login is complete: "
)

edit_url = (
    "https://opencart.abstracta.us/index.php?route=account/edit"
)

driver.get(edit_url)

input(
    "Check that the account details form is visible. "
    "Press Enter to continue: "
)

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

new_firstname = old_firstname
new_lastname = old_lastname
new_email = old_email
new_telephone = old_telephone


if scenario == "1":
    print("\nLeave a field blank to keep its original value.")

    entered_firstname = input("New first name: ").strip()
    entered_lastname = input("New last name: ").strip()
    entered_email = input("New email: ").strip()
    entered_telephone = input("New telephone: ").strip()

    if entered_firstname != "":
        new_firstname = entered_firstname

    if entered_lastname != "":
        new_lastname = entered_lastname

    if entered_email != "":
        new_email = entered_email

    if entered_telephone != "":
        new_telephone = entered_telephone

    changed = (
        new_firstname != old_firstname
        or new_lastname != old_lastname
        or new_email != old_email
        or new_telephone != old_telephone
    )

    assert changed == True, (
        "No changes were entered. Run again and change at least one field."
    )

elif scenario == "2":
    # Deliberately leave the first name empty.
    new_firstname = ""

else:
    # Deliberately enter an invalid email.
    new_email = "frank.example.com"


# Clear the web fields and enter the scenario values.
firstname_box.clear()

if new_firstname != "":
    firstname_box.send_keys(new_firstname)

lastname_box.clear()
lastname_box.send_keys(new_lastname)

email_box.clear()
email_box.send_keys(new_email)

telephone_box.clear()
telephone_box.send_keys(new_telephone)


# Verify the input values before submitting.
assert firstname_box.get_attribute("value") == new_firstname
assert lastname_box.get_attribute("value") == new_lastname
assert email_box.get_attribute("value") == new_email
assert telephone_box.get_attribute("value") == new_telephone

print("\nValues prepared for submission:")
print("First name:", repr(new_firstname))
print("Last name:", new_lastname)
print("Email:", new_email)
print("Telephone:", new_telephone)


# Find Continue and move it into view.
save_button = driver.find_element(
    By.CSS_SELECTOR,
    "#content form input[type='submit']"
)

driver.execute_script(
    "arguments[0].scrollIntoView({block: 'center'});",
    save_button
)

input(
    "Review the four fields and save an input screenshot. "
    "Check that Continue is not covered. Press Enter to save: "
)

save_button.click()

input(
    "Wait for the website to finish responding. "
    "Press Enter to inspect the result: "
)


if scenario == "1":
    # Print the actual result without assuming success.
    print("\nActual result page text:")
    print(driver.find_element(By.ID, "content").text)

else:
    # Locate the field that should be rejected.
    if scenario == "2":
        invalid_field = driver.find_element(
            By.ID,
            "input-firstname"
        )

        error_selector = "#input-firstname + .text-danger"

    else:
        invalid_field = driver.find_element(
            By.ID,
            "input-email"
        )

        error_selector = "#input-email + .text-danger"

    # Some invalid inputs are blocked by native browser validation.
    browser_message = driver.execute_script(
        "return arguments[0].validationMessage;",
        invalid_field
    )

    if browser_message != "":
        print("Actual browser validation:", browser_message)

        assert (browser_message != "") == True

    else:
        # Otherwise, check the website error beside the invalid field.
        error_message = driver.find_element(
            By.CSS_SELECTOR,
            error_selector
        )

        print("Actual website validation:", error_message.text)

        assert error_message.is_displayed() == True
        assert (error_message.text != "") == True

    assert invalid_field.is_displayed() == True

    print("PASS: Validation was found for the invalid field.")


input(
    "Save the result or validation screenshot BEFORE leaving this page. "
    "Press Enter to reopen account details: "
)


# Reopen the form and locate fresh elements.
driver.get(edit_url)

input(
    "Wait until the account details form is visible. "
    "Press Enter to check the saved values: "
)

saved_firstname = driver.find_element(
    By.ID,
    "input-firstname"
).get_attribute("value")

saved_lastname = driver.find_element(
    By.ID,
    "input-lastname"
).get_attribute("value")

saved_email = driver.find_element(
    By.ID,
    "input-email"
).get_attribute("value")

saved_telephone = driver.find_element(
    By.ID,
    "input-telephone"
).get_attribute("value")


print("\nActual saved account details:")
print("First name:", saved_firstname)
print("Last name:", saved_lastname)
print("Email:", saved_email)
print("Telephone:", saved_telephone)


# Valid updates should save the new values.
# Rejected updates should retain all original values.
if scenario == "1":
    expected_firstname = new_firstname
    expected_lastname = new_lastname
    expected_email = new_email
    expected_telephone = new_telephone

else:
    expected_firstname = old_firstname
    expected_lastname = old_lastname
    expected_email = old_email
    expected_telephone = old_telephone


# Check all four saved values.
assert saved_firstname == expected_firstname, (
    "FAIL: The saved first name does not match the expected value."
)
print("PASS: Saved first name matches.")

assert saved_lastname == expected_lastname, (
    "FAIL: The saved last name does not match the expected value."
)
print("PASS: Saved last name matches.")

assert saved_email == expected_email, (
    "FAIL: The saved email does not match the expected value."
)
print("PASS: Saved email matches.")

assert saved_telephone == expected_telephone, (
    "FAIL: The saved telephone does not match the expected value."
)
print("PASS: Saved telephone matches.")


if scenario == "1":
    print("\nPASS A1: The account update was saved correctly.")
    print("Use this email for your next login:", saved_email)

elif scenario == "2":
    print(
        "\nPASS A2: Empty first name was rejected "
        "and the original details were retained."
    )

else:
    print(
        "\nPASS A3: Invalid email was rejected "
        "and the original details were retained."
    )


input(
    "Save the saved-values page and terminal screenshots. "
    "Press Enter to close the browser: "
)

driver.quit()
