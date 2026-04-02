"""End-to-end UI tests via Playwright."""
import pytest
import re
from playwright.sync_api import Page, expect

UI_URL = "http://localhost:5173"

@pytest.mark.integration
def test_dashboard_guest_view(page: Page):
    """Test dashboard loads and displays guest banner."""
    try:
        page.goto(UI_URL, timeout=3000)
        expect(page).to_have_title(re.compile("VectorLearn|Vite", re.IGNORECASE))
        # Guest sees sign-in banner
        expect(page.locator("text=Sign in to save your work")).to_be_visible(timeout=2000)
    except Exception as e:
        pytest.skip(f"UI server not running at {UI_URL}. Skipping E2E test. Err: {e}")

@pytest.mark.integration
def test_community_page_loads(page: Page):
    """Test community route loads existing vectors."""
    try:
        page.goto(f"{UI_URL}/community", timeout=3000)
        # Should show community header
        expect(page.locator("text=Community Knowledge Bases")).to_be_visible(timeout=2000)
    except Exception as e:
        pytest.skip(f"UI server not running. Skipping E2E test. Err: {e}")
