"""
One-off test: does GitHub Actions' runner IP still get hit with
Cloudflare's bot-detection wall when loading X's login page?

This does NOT log in or use any credentials — it just loads the page
and checks whether Cloudflare's interstitial challenge ("Just a
moment...") appears instead of the real login form.
"""

from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        )

        print("[test] navigating to https://x.com/login")
        page.goto("https://x.com/login", timeout=30000, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)  # give any challenge time to render

        title = page.title()
        content = page.content()
        page.screenshot(path="ip_test_result.png", full_page=True)

        print(f"[test] page title: {title!r}")

        cloudflare_markers = ["Just a moment", "Checking your browser", "cf-browser-verification", "challenges.cloudflare.com"]
        hit_cloudflare = any(marker.lower() in content.lower() for marker in cloudflare_markers)

        login_markers = ["Sign in to X", "phone, email, or username", "name=\"text\""]
        saw_login_form = any(marker.lower() in content.lower() for marker in login_markers)

        print(f"[test] Cloudflare challenge detected: {hit_cloudflare}")
        print(f"[test] Real login form detected: {saw_login_form}")

        if hit_cloudflare:
            print("[result] STILL BLOCKED — Cloudflare challenge appeared instead of the login page.")
        elif saw_login_form:
            print("[result] NOT BLOCKED — the real login page loaded normally.")
        else:
            print("[result] UNCLEAR — neither a clear challenge nor a clear login form was detected. Check the screenshot.")

        browser.close()


if __name__ == "__main__":
    main()
