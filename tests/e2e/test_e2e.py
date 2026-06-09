from playwright.sync_api import sync_playwright

def test_home_page_e2e():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://127.0.0.1:5001/")
        assert "API is running!" in page.content()
        browser.close()