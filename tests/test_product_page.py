from playwright.sync_api import sync_playwright


def test_product_page_integrity():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        console_errors = []

        # Capture console errors
        page.on("console", lambda msg: 
            console_errors.append(msg.text) 
            if msg.type == "error" else None
        )

        url = "https://metafashion.in"
        response = page.goto(url)

        # Validate page loads successfully
        assert response.status == 200

        # Validate title exists
        assert page.title() != ""

        # Validate no broken images
        images = page.locator("img")
        count = images.count()

        for i in range(count):
            src = images.nth(i).get_attribute("src")
            if src:
                img_response = page.request.get(src)
                assert img_response.status == 200, f"Broken image: {src}"

        # Validate no console errors
        assert len(console_errors) == 0, f"Console errors found: {console_errors}"

        browser.close()
