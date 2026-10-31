from selenium import webdriver
from selenium.webdriver.common.by import By

scenario = input(
    "Choose a scenario to test:\n"
    "1 = Valid enquiry\n"
    "2 = Empty name\n"
    "3 = Invalid email\n"
    "Enter your choice:"
).strip()

assert scenario in ("1", "2", "3"), "Invalid choice, please enter 1, 2, or 3."

test_name = "Frank G"
test_email = "frankg@example.com"

if scenario == "2":
    test_name = ""
if scenario == "3":
    test_email = "invalid-email.com"
print("Scenario:", scenario)
print("Test name:", test_name)
print("Test email:", test_email)

driver = webdriver.Chrome()
driver.implicitly_wait(10)
driver.get("https://opencart.abstracta.us/index.php?route=information/contact")

input("If there is warning notice, " \
"please click 'Advanced' and then 'Proceed to opencart.abstracta.us (unsafe)' "
"and then press Enter to continue...")

name_blank = driver.find_element(By.ID, "input-name")
name_blank.clear()
if test_name != "":
    name_blank.send_keys(test_name)

email_blank= driver.find_element(By.ID, "input-email")
email_blank.clear()
email_blank.send_keys(test_email)

enquiry_blank = driver.find_element(By.ID, "input-enquiry")
enquiry_blank.send_keys("Hello,this is an enquiry test")
input("Please review the form. Press Enter to continue:")

submit_button = driver.find_element(By.CSS_SELECTOR, "input.btn.btn-primary")
driver.execute_script(
    "arguments[0].scrollIntoView({block: 'center'});",
    submit_button
)

input("Check that Submit is not covered. Press Enter to submit: ")
submit_button.click()
input("Wait for the result. Press Enter to check it:")

result = driver.find_elements(By.ID, "common-success")
if scenario == "1":
    print("Result page found:", len(result))
    assert len(result) == 1, "Expected success message not found."
    print("Pass: Valid enquiry submitted successfully.")
    message = driver.find_element(By.ID, "content").text
    print("Success message:", message)
    print("Note: This dose not prove that the enquiry email was delivered."
    )
    print("Record whether an explicit submission comfirmation is visible."
    )
else:
    if scenario == "2":
        error_message = driver.find_element(
            By.CSS_SELECTOR,
            "#input-name + .text-danger"
        )
    else:
        error_message = driver.find_element(
            By.CSS_SELECTOR,
            "#input-email + .text-danger"
        )
    print("Error message found:", error_message.text)

    assert error_message.is_displayed() == True
    assert (error_message.text != "") == True
    result = driver.find_elements(By.ID, "common-success")
    assert len(result) == 0, "Unexpected success message found."
    print("Pass: Validation error message displayed correctly.")

input("Take a screenshot for your records. Press Enter to continue:")
driver.quit()



