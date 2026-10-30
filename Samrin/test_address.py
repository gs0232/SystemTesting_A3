"""TC007 / F7: add an address with valid data or missing required fields."""
import os
import pytest
from playwright.sync_api import expect
from conftest import BASE

@pytest.mark.parametrize('scenario', ['valid', 'missing_firstname', 'missing_city'])
def test_address(page, scenario):
    # Use a disposable account from the registration tester, never a real account.
    email, password = os.getenv('TEST_EMAIL'), os.getenv('TEST_PASSWORD')
    if not email or not password:
        pytest.skip('BLOCKED: set TEST_EMAIL and TEST_PASSWORD for a test account')
    page.goto(BASE + 'index.php?route=account/login')
    if os.getenv('MANUAL_LOGIN') == '1':
        page.pause()
    else:
        page.locator('#input-email').fill(email)
        page.locator('#input-password').fill(password)
        page.get_by_role('button', name='Login', exact=True).click()
    expect(page).to_have_url(__import__('re').compile(r'route=account/account'))
    page.goto(BASE + 'index.php?route=account/address/add')
    # All addresses below are fictional test data.
    values = {'firstname': 'Test', 'lastname': 'Reviewer', 'address-1':
              '123 Test Street', 'city': 'Sydney', 'postcode': '2000'}
    if scenario == 'missing_firstname':
        values['firstname'] = ''
    if scenario == 'missing_city':
        values['city'] = ''
    for key, value in values.items():
        page.locator('#input-' + key).fill(value)
    page.locator('#input-country').select_option(label='Australia')
    page.locator('#input-zone').select_option(label='New South Wales')
    page.get_by_role('button', name='Continue', exact=True).click()
    if scenario == 'valid':
        expect(page.locator('.alert-success')).to_contain_text('successfully added')
        expect(page.locator('#content')).to_contain_text('123 Test Street')
        expect(page.locator('#content')).to_contain_text('Sydney')
    else:
        message = ('First Name must be between 1 and 32 characters!'
                   if scenario == 'missing_firstname' else
                   'City must be between 2 and 128 characters!')
        expect(page.locator('.text-danger').filter(has_text=message)).to_be_visible()
        expect(page.locator('#content .alert-success')).to_have_count(0)
