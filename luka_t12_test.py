# By Luka Katovcic
# STQM Assessment 3 Test Case T12 -> Add to Wishlist

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setting constant values for the page URLs
HOME_URL = "https://opencart.abstracta.us/"
LOGIN_URL = "https://opencart.abstracta.us/index.php?route=account/login"
WISHLIST_URL = "https://opencart.abstracta.us/index.php?route=account/wishlist"

# Setting constant values for sample account
ACCOUNT_EMAIL = "examplegmailaccount@gmail.com"
ACCOUNT_PASSWORD = "password"

# Element locators for home page
WISHLIST_BUTTONS = (By.CSS_SELECTOR, ".product-thumb button[onclick^='wishlist.add']")
PRODUCT_NAMES_ON_LIST = (By.CSS_SELECTOR, ".product-thumb h4 a")
SUCCESS_ALERT = (By.CSS_SELECTOR, ".alert-success")
WISHLIST_TOTAL = (By.ID, "wishlist-total")

# Element locators for login page & account page
LOGIN_EMAIL_TF = (By.ID, "input-email")
LOGIN_PASSWORD_PF = (By.ID, "input-password")
LOGIN_SUBMIT_BUTTON = (By.CSS_SELECTOR, "input[value='Login']")
ACCOUNT_PAGE_HEADING = (By.CSS_SELECTOR, "#content h2")

# Element locators for wishlist page
WISHLIST_CONTENTS = (By.ID, "content")
WISHLIST_NAMES = (By.CSS_SELECTOR, "#content table tbody td.text-left a")
WISHLIST_REMOVE_BUTTONS = (By.CSS_SELECTOR, "#content table a.btn-danger[href*='remove=']")
WISHLIST_EMPTY_MSG = (By.CSS_SELECTOR, "#content p")

# ----- HELPER FUNCTIONS START -----
# Log in with registered sample account and load account page
def log_in(driver, wait):
    driver.get(LOGIN_URL)
    wait.until(EC.visibility_of_element_located(LOGIN_EMAIL_TF)).send_keys(ACCOUNT_EMAIL)
    driver.find_element(*LOGIN_PASSWORD_PF).send_keys(ACCOUNT_PASSWORD)
    driver.find_element(*LOGIN_SUBMIT_BUTTON).click()

    # Logged in once account page heading is 'My Account'
    wait.until(EC.text_to_be_present_in_element(ACCOUNT_PAGE_HEADING, "My Account"))

# Open the wishlist page and load everything on it
def go_to_wishlist_page(driver, wait):
    driver.get(WISHLIST_URL)
    wait.until(EC.presence_of_element_located(WISHLIST_CONTENTS))

# Find the number of items on the wishlist page by counting the number of remove buttons
def wishlist_item_count(driver):
    return len(driver.find_elements(*WISHLIST_REMOVE_BUTTONS))

# Find the product names of wishlisted products
def wishlist_item_names(driver):
    return [product.text for product in driver.find_elements(*WISHLIST_NAMES)]

# Find the wishlist header text
def header_wishlist(driver):
    return driver.find_element(*WISHLIST_TOTAL).text.strip()

# Wait for wishlist page to show the desired number of items
def wait_for_wishlist_count_update(wait, expected_value):
    def matches(driver):
        return wishlist_item_count(driver) == expected_value
    wait.until(matches)

# Remove every item from the wishlist
def clear_wishlist(driver, wait):
    go_to_wishlist_page(driver, wait)
    while wishlist_item_count(driver) > 0:
        count = wishlist_item_count(driver)
        driver.find_elements(*WISHLIST_REMOVE_BUTTONS)[0].click()

        # Wait for the count to drop
        wait_for_wishlist_count_update(wait, count - 1)

# Click 'Add to Wish List' button on home page products and find name
def add_to_wishlist_from_home(driver, wait, i, page_loaded=True):
    if page_loaded:
        driver.get(HOME_URL)

    # Wait for wishlist buttons on the page to work
    wait.until(EC.element_to_be_clickable(WISHLIST_BUTTONS))
    names = driver.find_elements(*PRODUCT_NAMES_ON_LIST)
    product_buttons = driver.find_elements(*WISHLIST_BUTTONS)
    product_name = names[i].text
    product_buttons[i].click()

    # Wait for success alert to popup
    wait.until(EC.text_to_be_present_in_element(SUCCESS_ALERT, product_name))
    return product_name

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

#Test Scenario 1 -> Guest/non logged-in user tries to Add to Wishlist
def test_t12_scenario1():
    driver = setup()
    wait = WebDriverWait(driver, 10)
    try:
        add_to_wishlist_from_home(driver, wait, 0)

        # Asking guest to log in or register 
        alert_string = driver.find_element(*SUCCESS_ALERT).text.lower()
        assert "login" in alert_string
        assert "create an account" in alert_string
        assert "(1)" in header_wishlist(driver)

        # Ensuring the guest cannot view the wishlist page and it redirects them to login page
        driver.get(WISHLIST_URL)
        wait.until(EC.presence_of_element_located(LOGIN_EMAIL_TF))
        assert len(driver.find_elements(*LOGIN_EMAIL_TF)) == 1
        assert len(driver.find_elements(*WISHLIST_REMOVE_BUTTONS)) == 0
    finally:
        teardown(driver)

#Test Scenario 2 -> A logged-in user adds an item to Wishlist
def test_t12_scenario2():
    driver = setup()
    wait = WebDriverWait(driver, 10)
    try:
        log_in(driver, wait)

        # Clear the wishlist to remove any remaining items from previous tests
        clear_wishlist(driver, wait)

        products_added = add_to_wishlist_from_home(driver, wait, 0)

        # Check success alert and wishlist counter
        assert "added" in driver.find_element(*SUCCESS_ALERT).text.lower()
        assert "(1)" in header_wishlist(driver)

        # Ensure the wishlist page has the correct product added to it
        go_to_wishlist_page(driver, wait)
        assert wishlist_item_count(driver) == 1
        assert wishlist_item_names(driver) == [products_added]
    finally:

        # One last clear so that the wishlist is unaffected in later tests
        clear_wishlist(driver, wait)
        teardown(driver)

#Test Scenario 3 -> Logged-in user adds the same item multiple times and removes it
def test_t12_scenario3():
    driver = setup()
    wait = WebDriverWait(driver, 10)
    try:
        log_in(driver, wait)

        # Clear the wishlist to remove any remaining items from previous tests
        clear_wishlist(driver, wait)

        # Add the same item thrice
        driver.get(HOME_URL)
        products_added = add_to_wishlist_from_home(driver, wait, 0, page_loaded=False)
        add_to_wishlist_from_home(driver, wait, 0, page_loaded=False)
        add_to_wishlist_from_home(driver, wait, 0, page_loaded=False)

        # Ensure only one entry is in the wishlist
        assert "(1)" in header_wishlist(driver)
        go_to_wishlist_page(driver, wait)
        assert wishlist_item_count(driver) == 1
        assert wishlist_item_names(driver) == [products_added]

        # Removing the item and checking if the wishlist is empty
        driver.find_elements(*WISHLIST_REMOVE_BUTTONS)[0].click()
        wait_for_wishlist_count_update(wait, 0)
        wait.until(EC.text_to_be_present_in_element(WISHLIST_EMPTY_MSG, "empty"))
        assert wishlist_item_names(driver) == []
    finally:

        # One last clear so that the wishlist is unaffected in later tests
        clear_wishlist(driver, wait)
        teardown(driver)