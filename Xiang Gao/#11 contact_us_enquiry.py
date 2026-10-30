from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.implicitly_wait(10)
driver.get("https://opencart.abstracta.us/index.php?route=information/contact")

input("If there is warning notice, " \
"please click 'Advanced' and then 'Proceed to opencart.abstracta.us (unsafe)' "
"and then press Enter to continue...")

name_blank = driver.find_element(By.ID, "input-name")
name_blank.send_keys("Frank G")

email_blank= driver.find_element(By.ID, "input-email")
email_blank.send_keys("frankgao666@outlook.com")

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
print("Result page containers found:", len(result))
assert len(result) == 1, (
    "fail: the expected result page was not found."
)
print("Pass: The expected result page container was found.")
message = driver.find_element(By.ID, "content").text
print("Actual page text:")
print(message)

print(
        "NOTE: Finding the result page does not prove "
        "that the enquiry email was delivered."
    )
print(
        "Record whether an explicit submission confirmation "
        "is visible on the page."
    )

input("Press Enter to close the browser:")
driver.quit()




