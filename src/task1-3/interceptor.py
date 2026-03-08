import asyncio
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from seleniumbase import SB 
from get_token import get_Token


async def task_2_interception(token):
    if not token:
        print("No token provided, aborting.")
        547\

    print("Starting Interceptor...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        async def intercept_turnstile(route):
            url = route.request.url
            if "challenges.cloudflare.com" in url:
                print(f"--- Intercepted & Blocked Request: {url[:60]}... ---")
                await route.abort()
            else:
                await route.continue_()

        # Set up the route interception 
        await page.route("**/*", intercept_turnstile)

        # 1. Open the site
        await page.goto("https://cd.captchaaiplus.com/turnstile.html")
        await page.wait_for_load_state('domcontentloaded')

        # Capture details from DOM since script is blocked
        cf_div = page.locator('.cf-turnstile')
        if await cf_div.count() > 0:
            print("--- Capturing Turnstile Details ---")
            sitekey = await cf_div.get_attribute('data-sitekey')
            action = await cf_div.get_attribute('data-action')
            cdata = await cf_div.get_attribute('data-cdata')

            if not cdata:
                import re
                print("cdata not found in DOM attributes, scanning page source...")
                content = await page.content()
                cdata_match = re.search(r'cdata:\s*["\']([^"\']+)["\']', content)
                if cdata_match:
                    cdata = cdata_match.group(1)
                    print("Found cdata in page source via regex.")
                else:
                    print("Could not find cdata in page source.")

            print(f"Sitekey: {sitekey}")
            print(f"Pageaction: {action}")
            print(f"cdata: {cdata}")
        else:
            print("No .cf-turnstile div found.")

        # 2. Inject the valid token 
        await page.evaluate(f"""
            () => {{
                let input = document.querySelector('[name="cf-turnstile-response"]');
                if (!input) {{
                    input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = 'cf-turnstile-response';
                    document.getElementById('turnstile-form').appendChild(input);
                }}
                input.value = "{token}";
            }}
        """)
        print("Token injected successfully.")

        # 3. Press Submit 
        await page.get_by_role("button", name="Submit").click()

        # 4. Wait for Success message
        try:
            success_msg = page.get_by_text("Success!", exact=False)
            await success_msg.wait_for(state="visible", timeout=8000)
            print("Final Result: Success! Verified (via Injection)")
        except Exception as e:
            print(f"Failed to verify injected token: {e}")

        await asyncio.sleep(3) # Time to record the video result
        await browser.close()

if __name__ == "__main__":
    token = get_Token()
    asyncio.run(task_2_interception(token))