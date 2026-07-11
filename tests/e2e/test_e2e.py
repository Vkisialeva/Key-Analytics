import socket
import threading
import time

import pytest
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

from src.app import app


@pytest.fixture(scope="module")
def live_server():
    server = make_server("127.0.0.1", 5001, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", 5001), timeout=0.5):
                break
        except OSError:
            time.sleep(0.1)
    else:
        pytest.fail("Flask server did not start in time")

    yield

    server.shutdown()
    thread.join(timeout=5)
    server.server_close()


def test_home_page_e2e(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:5001/", wait_until="domcontentloaded")
        assert "API is running!" in page.content()
        browser.close()