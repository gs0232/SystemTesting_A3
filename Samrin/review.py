"""TC009 / F9: submit a valid review and test two validation failures."""
import pytest
from playwright.sync_api import expect
from conftest import BASE

# Synthetic test feedback, explicitly identified as an automated test.
TEXT = 'Automated coursework test review using synthetic data.'

@pytest.mark.parametrize('scenario,name,text,expected', [
    ('valid', 'Test Reviewer', TEXT, 'success'),
    ('missing_name', '', TEXT, 'name'),
    ('short_review', 'Test Reviewer', 'Too short', 'review'),
])
def test_review(page, scenario, name, text, expected):
    page.goto(BASE + 'index.php?route=product/product&product_id=43')
    page.get_by_role('link', name='Reviews', exact=False).first.click()
    page.locator('#input-name').fill(name)
    page.locator('#input-review').fill(text)
    page.locator('input[name="rating"][value="5"]').check()
    page.locator('#button-review').click()
    if expected == 'success':
        # A moderation confirmation means submitted, not publicly published.
        expect(page.locator('#form-review .alert-success')).to_contain_text(
            'Thank you for your review')
    else:
        warning = page.locator('#form-review .alert-danger')
        expect(warning).to_be_visible()
        if expected == 'name':
            expect(warning).to_contain_text('Review Name must be between 3 and 25 characters')
        else:
            expect(warning).to_contain_text('Review Text must be between 25 and 1000 characters')
        expect(page.locator('#form-review .alert-success')).to_have_count(0)
