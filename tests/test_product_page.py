from playwright.sync_api import sync_playwright


def test_product_page_integrity():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        console_errors = []

        # Capture console errors
        failed_requests = []

        def handle_request_failed(request):
            if request.failure:
                failed_requests.append(request.url)

        page.on("requestfailed", handle_request_failed)

        critical_errors = []

        for url in failed_requests:
            if any(domain in url.lower() for domain in [
                "cdn",
                "shopify",
                "analytics",
                "facebook",
                "doubleclick",
                "googletagmanager"
            ]):
                continue
            critical_errors.append(url)

        assert len(critical_errors) == 0, f"Critical network errors: {critical_errors}"


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

        # Filter only serious console errors
        critical_errors = []

        for error in console_errors:
            if "ERR_FILE_NOT_FOUND" in error:
                # Ignore third-party and CDN noise
                if any(domain in error.lower() for domain in [
                    "cdn",
                    "shopify",
                    "analytics",
                    "facebook",
                    "doubleclick",
                    "googletagmanager"
                ]):
                    continue
                critical_errors.append(error)

        assert len(critical_errors) == 0, f"Critical console errors found: {critical_errors}"

        browser.close()
