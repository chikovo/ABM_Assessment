from playwright.sync_api import sync_playwright
from seleniumbase import SB


def get_Token():
    print("Fetching fresh single-use token...")
    with SB(uc=True, headless2=True) as sb:
        sb.uc_open_with_reconnect("https://cd.captchaaiplus.com/turnstile.html", 5)

        c_options = sb.driver.capabilities.get("goog:chromeOptions")
        cdp_url = f"http://{c_options.get('debuggerAddress')}"

        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(cdp_url)
            page = browser.contexts[0].pages[0]
            try:
                page.wait_for_function(
                    "() => {"
                    "  const el = document.querySelector('[name=cf-turnstile-response]');"
                    "  return el && el.value.length > 0;"
                    "}",
                    timeout=30000,
                )
                token = page.eval_on_selector(
                    "[name='cf-turnstile-response']", "el => el.value"
                )
                print(f"Token fetched: {token[:30]}...")
                browser.close()
                return token
            except Exception as e:
                print(f"Failed to fetch token: {e}")
                browser.close()
                return None
    return token


if __name__ == "__main__":
    print(get_Token())
