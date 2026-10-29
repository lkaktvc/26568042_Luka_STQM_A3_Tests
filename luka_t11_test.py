# By Luka Katovcic
# STQM Assessment 3 Test Case T11 -> Product Comparison

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setting constant values for the page URLs
HOME_URL = "https://opencart.abstracta.us/"
PRODUCT_LIST_URL = "https://opencart.abstracta.us/index.php?route=product/category&path=20&limit=100"
COMPARISON_URL = "https://opencart.abstracta.us/index.php?route=product/compare"

# Element locators for the product listing page
COMPARE_BUTTONS = (By.CSS_SELECTOR, ".product-thumb button[onclick^='compare.add']")
PRODUCTS_ON_LIST = (By.CSS_SELECTOR, ".product-thumb h4 a")
SUCCESS_ALERT = (By.CSS_SELECTOR, ".alert-success")
COMPARE_TOTAL = (By.ID, "compare-total")

# Element locators for the product comparison page
COMPARE_HEADING = (By.CSS_SELECTOR, "#content h1")
COMPARE_PAGE_NAMES = (By.CSS_SELECTOR, "#content table.table-bordered tbody td a strong")
COMPARE_REMOVE_BUTTONS = (By.CSS_SELECTOR, "#content table.table-bordered a.btn-danger[href*='remove=']")

# ----- HELPER FUNCTIONS START -----
# Opening the main product listing page that has every item available to see on it
def open_product_list(driver, wait):
    driver.get(PRODUCT_LIST_URL)
    wait.until(EC.presence_of_all_elements_located(COMPARE_BUTTONS))

# Clicking the comparison button on the desired product & getting the item's name
def add_to_comparison_list(driver, wait, i):
    names = driver.find_elements(*PRODUCTS_ON_LIST)
    product_buttons = driver.find_elements(*COMPARE_BUTTONS)
    product_name = names[i].text

    product_buttons[i].click()

    # Wait for success alert to show up after adding product to product comparison list
    wait.until(EC.text_to_be_present_in_element(SUCCESS_ALERT, product_name))
    return product_name

# Open the product comparison page and load everything on it
def go_to_comparison_page(driver, wait):
    driver.get(COMPARISON_URL)
    wait.until(EC.presence_of_element_located(COMPARE_HEADING))

# Find product names on the Product Comparison page
def comparison_page_names(driver):
    return [product.text for product in driver.find_elements(*COMPARE_PAGE_NAMES)]

# Find the number of products on the Comparison page
def comparison_page_count(driver):
    return len(driver.find_elements(*COMPARE_REMOVE_BUTTONS))

# Find the header text on the PRODUCT_LIST_URL 
def comparison_header_text(driver):
    return driver.find_element(*COMPARE_TOTAL).text.strip()

# Wait until the comparison page shows the desired number of products
def wait_for_comparison_page_count(wait, expected_value):
    def matches(driver):
        return comparison_page_count(driver) == expected_value

    wait.until(matches)

# Using setup() to create the driver
def setup():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.implicitly_wait(0)
    return driver

# Using teardown() to end the test
def teardown(driver):
    driver.quit()
# ----- HELPER FUNCTIONS END -----

# Test Scenario 1 -> Add one item to the Product Comparison list
def test_t11_scenario1():
    driver = setup()
    wait = WebDriverWait(driver, 10)
    try:
        open_product_list(driver, wait)
        added_product = add_to_comparison_list(driver, wait, 0)

        # Check for counter update
        assert "(1)" in comparison_header_text(driver)

        # See if the comparison page lists the correct product 
        go_to_comparison_page(driver, wait)
        assert comparison_page_count(driver) == 1
        assert comparison_page_names(driver) == [added_product]
    finally:
        teardown(driver)

# Test Scenario 2 -> Add two products and remove one
def test_t11_scenario2():
    driver = setup()
    wait = WebDriverWait(driver, 10)
    try:
        open_product_list(driver, wait)
        first_added_product = add_to_comparison_list(driver, wait, 0)
        second_added_product = add_to_comparison_list(driver, wait, 1)

        # Check for counter update
        assert "(2)" in comparison_header_text(driver)

        go_to_comparison_page(driver, wait)
        assert comparison_page_count(driver) == 2

        # Remove the first product
        driver.find_elements(*COMPARE_REMOVE_BUTTONS)[0].click()
        wait_for_comparison_page_count(wait, 1)

        # Ensure the removed product is gone and the other one is still there
        remaining_products = comparison_page_names(driver)
        assert first_added_product not in remaining_products
        assert second_added_product in remaining_products
    finally:
        teardown(driver)

# Test Scenario 3 -> Adding five products to the product comparison list
def test_t11_scenario3():
    driver = setup()
    wait = WebDriverWait(driver, 10)
    try:
        open_product_list(driver, wait)
        added_products = []
        for i in range(5):
            added_products.append(add_to_comparison_list(driver, wait, i))

        # Check if counter has updated correctly
        assert "(5)" in comparison_header_text(driver)

        go_to_comparison_page(driver, wait)
        assert comparison_page_count(driver) == 5
        shown_products = comparison_page_names(driver)

        # Check every product added is shown
        for product in added_products:
            assert product in shown_products
    finally:
        teardown(driver)