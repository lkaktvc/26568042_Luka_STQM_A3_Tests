# By Luka Katovcic
# STQM Assessment 3 Test Case T10 -> Remove from Cart

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# setting constant values for page URLS
HOME_URL = "https://opencart.abstracta.us/"
CART_URL = "https://opencart.abstracta.us/index.php?route=checkout/cart"

# Element locators for home page
ADD_TO_CART_BUTTONS = (By.CSS_SELECTOR, ".product-thumb button[onclick^='cart.add']")
CART_SUCCESS_ALERT = (By.CSS_SELECTOR, ".alert-success")

# Element locators for cart page
CART_ROW = (By.CSS_SELECTOR, "#content form table tbody tr")
CART_ITEMS = (By.CSS_SELECTOR, "#content form table tbody tr td.text-left a")
CART_REMOVE_BUTTONS = (By.CSS_SELECTOR, "#content form button[onclick^='cart.remove']")
CART_EMPTY_MSG = (By.CSS_SELECTOR, "#content p")
CART_PAGE_HEADING = (By.CSS_SELECTOR, "#content h1")

# Element locators for the cart total header and the dropdown menu (this is on every page)
HEADER_CART_BUTTON = (By.CSS_SELECTOR, "#cart > button")
CART_TOTAL = (By.ID, "cart-total")
DROPDOWN_ITEM_ROW = (By.CSS_SELECTOR, "#cart .dropdown-menu table.table-striped tr")
DROPDOWN_REMOVE_BUTTONS = (By.CSS_SELECTOR, "#cart .dropdown-menu button[onclick^='cart.remove']")
DROPDOWN_EMPTY = (By.CSS_SELECTOR, "#cart .dropdown-menu p.text-center")

# ----- HELPER FUNCTIONS START -----
# Open home page and click 'Add to Cart' button on given product
def add_product_from_home_page(driver, wait, i):
    driver.get(HOME_URL)

    # Wait for all buttons to load on the page, then click them
    wait.until(EC.element_to_be_clickable(ADD_TO_CART_BUTTONS))
    btns = driver.find_elements(*ADD_TO_CART_BUTTONS)
    btns[i].click()

    # Wait for the success alert to pop up
    wait.until(EC.visibility_of_element_located(CART_SUCCESS_ALERT))

# Open cart page and load it
def go_to_cart_page(driver, wait):
    driver.get(CART_URL)
    wait.until(EC.presence_of_element_located(CART_PAGE_HEADING))

# Find number of items on cart page by finding the number of remove buttons
def cart_item_count(driver):
    return len(driver.find_elements(*CART_REMOVE_BUTTONS))

# Find the cart total text for the cart header
def cart_header(driver):
    return driver.find_element(*CART_TOTAL).text.strip()

# Wait for cart header to contain given String s
def wait_for_cart_header(wait, s):
    wait.until(EC.text_to_be_present_in_element(CART_TOTAL, s))

# Wait for cart page to show the expected number of values
def wait_for_cart_item_count(wait, expected_value):
    def matches(driver):
        return cart_item_count(driver) == expected_value
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

# Test Scenario 1 -> Remove last item from cart
def test_t10_scenario1():
    driver = setup()
    wait = WebDriverWait(driver, 10)
    try:
        add_product_from_home_page(driver, wait, 0)
        go_to_cart_page(driver, wait)
        assert cart_item_count(driver) == 1

        wait.until(EC.element_to_be_clickable(CART_REMOVE_BUTTONS)).click()

        # The cart page content has change to empty-cart message
        wait.until(EC.text_to_be_present_in_element(CART_EMPTY_MSG, "Your shopping cart is empty!"))
        assert cart_item_count(driver) == 0

        # The card header total matches the empty cart
        wait_for_cart_header(wait, "0 item(s)")
    finally:
        teardown(driver)

#Test Scenario 2 -> Remove one item of two 
def test_t10_scenario2():
    driver = setup()
    wait = WebDriverWait(driver, 10)
    try: 
        add_product_from_home_page(driver, wait, 0)
        add_product_from_home_page(driver, wait, 1)
        go_to_cart_page(driver, wait)
        assert cart_item_count(driver) == 2

        # Saving the item names before removing
        names = [el.text for el in driver.find_elements(*CART_ITEMS)]
        assert len(names) == 2
        removed_name = names[0]

        driver.find_elements(*CART_REMOVE_BUTTONS)[0].click()
        wait_for_cart_item_count(wait, 1)

        # Ensuring the right item was removed and the other was not 
        leftovers = [el.text for el in driver.find_elements(*CART_ITEMS)]
        assert removed_name not in leftovers
        assert names[1] in leftovers

        # Making sure the header total matches the one remaining item
        wait_for_cart_header(wait, "1 item(s)")
    finally:
        teardown(driver)

#Test Scenario 3 -> Remove an item using the cart dropdown men
def test_t10_scenario3():
    driver = setup()
    wait = WebDriverWait(driver, 10)
    try:
        add_product_from_home_page(driver, wait, 0)

        wait_for_cart_header(wait, "1 item(s)")
        wait.until(EC.element_to_be_clickable(HEADER_CART_BUTTON)).click()
        remove_btn = wait.until(EC.element_to_be_clickable(DROPDOWN_REMOVE_BUTTONS))
        assert len(driver.find_elements(*DROPDOWN_REMOVE_BUTTONS)) == 1

        remove_btn.click()

        # Ensuring the header total updates
        wait_for_cart_header(wait, "0 item(s)")

        # Refreshing the page for a more stable check at this stage
        driver.refresh()
        wait.until(EC.element_to_be_clickable(HEADER_CART_BUTTON)).click()

        # Seeing if the dropdown list says the cart is empty
        wait.until(EC.presence_of_element_located(DROPDOWN_EMPTY))
        assert "empty" in driver.find_element(*DROPDOWN_EMPTY).text.lower()

        # Last cross-check on the cart page for reassurance
        go_to_cart_page(driver, wait)
        assert cart_item_count(driver) == 0
    finally:
        teardown(driver)
