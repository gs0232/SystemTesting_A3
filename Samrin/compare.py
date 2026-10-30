"""TC008 / F8: compare products, reject duplicates, remove a product."""
import pytest
from playwright.sync_api import expect
from conftest import BASE

# These are OpenCart demo product IDs. Verify names if demo data changes.
PRODUCTS = [(43, 'MacBook'), (40, 'iPhone')]


def add_product(page, product_id):
    page.goto(BASE + f'index.php?route=product/product&product_id={product_id}')
    page.locator(f"""button[onclick="compare.add('{product_id}');"]""").click()
    expect(page.locator('.alert-success')).to_contain_text('Success')


@pytest.mark.parametrize('scenario', ['two_products', 'duplicate', 'remove'])
def test_compare(page, scenario):
    # All scenarios start by adding the same two distinct products.
    for product_id, _ in PRODUCTS:
        add_product(page, product_id)
    if scenario == 'duplicate':
        add_product(page, 43)  # A repeated product must not create a new column.
    page.goto(BASE + 'index.php?route=product/compare')
    table = page.locator('#content table')
    for _, name in PRODUCTS:
        expect(table.get_by_role('link', name=name, exact=True)).to_have_count(1)
    # Product Name row contains one label cell plus the product columns.
    expect(table.locator('tbody').first.locator('tr').first.locator('td')).to_have_count(3)
    if scenario == 'remove':
        table.get_by_role('link', name='Remove', exact=True).first.click()
        expect(page.locator('#content table').get_by_role(
            'link', name='MacBook', exact=True)).to_have_count(0)
        expect(page.locator('#content table').get_by_role(
            'link', name='iPhone', exact=True)).to_have_count(1)
