from playwright.sync_api import sync_playwright
import time

BASE_URL = "https://india.vkydlabs.com"

def test_cart_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        console_errors = []

        # Capture console errors
        page.on("console", lambda msg:
            console_errors.append(msg.text)
            if msg.type == "error" else None
        )

        product_url = f"{BASE_URL}/products/steampunk-corset-with-jacket-skirt"
        response = page.goto(product_url)

        assert response.status == 200

        # Wait for Shopify hydration
        page.wait_for_load_state("networkidle")

        # Product title (Shopify themes vary)
        title = page.locator("h1, .product__title, .product-title").first
        title.wait_for(state="visible", timeout=7000)

        # Price visibility
        # Wait for any Shopify price container to appear
        price = page.locator(
            ".price, .price-item, .product__price, span.money"
        ).first

        price.wait_for(state="visible", timeout=7000)

        # Ensure price text contains currency or digits
        price_text = price.inner_text()
        assert any(char.isdigit() for char in price_text), "Price text did not contain digits"


        # Add to Cart
        add_to_cart = page.locator("button:has-text('Add to cart'), button:has-text('Add to Cart')")
        add_to_cart.first.click()

        # Allow AJAX cart update
        time.sleep(3)

        # Go to cart page
        page.goto(f"{BASE_URL}/cart")

        page.wait_for_load_state("networkidle")

        # Validate cart contains item
        if not page.locator("#cart").is_visible():
            cart_form = page.locator("#cart-notification-form")
            cart_form.wait_for(state="visible", timeout=7000)

        # Checkout button exists
        checkout_button = page.locator("#checkout")
        checkout_button.wait_for(state="visible", timeout=7000)

        # Filter critical console errors (ignore third-party noise)
        critical_errors = []

        for error in console_errors:
            if "ERR_FILE_NOT_FOUND" in error:
                # Ignore known external noise
                if any(domain in error.lower() for domain in ["cdn", "shopify", "analytics", "facebook"]):
                    continue
                critical_errors.append(error)


        assert len(critical_errors) == 0, f"Critical console errors found: {critical_errors}"

        browser.close()
