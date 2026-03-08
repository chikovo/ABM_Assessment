# ABM Assessment - Automation Tasks

Hi team,

Thank you for the opportunity to work on this assessment! Below is a breakdown of what I did and the approaches I took for the three tasks provided: `stealth.py`, `interceptor.py`, and `scraper.py`.

## 1. Stealth Bypass (`stealth.py`)

**Objective:** Bypass the Turnstile CAPTCHA and retrieve the verification token in both headed and headless modes.

**Approach:**
- **Hybrid Framework Use:** I used `seleniumbase` with its undetected Chrome (`uc=True`) and `headless2` settings to handle the initial browser launch. This effectively mitigates Cloudflare's headless detection mechanisms.
- **CDP Connection:** To get the best of both worlds, I connected `playwright` to the `seleniumbase` browser instance via the Chrome DevTools Protocol (CDP) port.
- **Token Extraction:** Once the page loads, the script waits for the Turnstile script to inject the token into the hidden input field (`[name="cf-turnstile-response"]`). Playwright reads the value, clicks "Submit", and verifies the success message.
- **Testing:** The `main` function runs a loop of 10 attempts (5 in headless mode, 5 in headed mode) to demonstrate script reliability and calculates the final success rate.

## 2. Request Interception & Token Injection (`interceptor.py`)

**Objective:** Prevent the Turnstile CAPTCHA from loading, extract CAPTCHA configuration data, and inject a valid token to bypass the challenge.

**Approach:**
- **Request Interception:** I used Playwright's asynchronous API (`async_playwright`) and `page.route` to intercept all network requests. Any request containing `challenges.cloudflare.com` is forcefully aborted, preventing the Turnstile script from loading entirely.
- **Data Capture:** With the script blocked, I extracted the site key, action, and cdata from the `.cf-turnstile` div element in the DOM. If `data-cdata` isn't found in the attributes, a fallback regex scans the page source, however i didn't find any actior or cdata in the page source.
- **Token Injection:** I used JavaScript via `page.evaluate` to dynamically create or update the hidden `cf-turnstile-response` input field and inject a valid token (retrieved via a utility function `get_Token()`).
- **Submission:** Finally, Playwright auto-clicks the Submit button and validates the subsequent "Success!" message verification.

## 3. Advanced Captcha Scraping (`scraper.py`)

**Objective:** Extract images and specific instruction texts from a heavily obfuscated CAPTCHA page where elements use CSS tricks (like `background-image`) or are intentionally hidden under other overlapping elements.

**Approach:**
- **Scraping ALL Images:** For verification, I used Javascript within `page.evaluate`, I iterated through all DOM elements. I checked for `<img>` tags, `<input type="image">` tags, and extracted URLs from the `getComputedStyle` `background-image` property, aggressively collecting all base64 data which always turned out to be 54 images, owever I couldn't find any other images in the page source, so I turned  back to python.
- **Scraping Only VISIBLE Images (The 3x3 Grid):** To beat CSS overlapping hidden elements, I mapped out the bounding box of the `.main-div-container`. Using math, I pinpointed the exact pixel coordinates for the center of each cell in the 3x3 array. By executing `document.elementFromPoint(x, y)` at those physical coordinates, the browser engine naturally ignores z-index obscured or visually hidden elements, returning only the actual visible image the user sees. I had to do this because the .visible class was not working.
- **Scraping Visible Text Instructions:** For the instruction text (`.box-label`), I calculated the center of each label's bounding box and performed the same `document.elementFromPoint()` raycast. This confirmed the label was genuinely the top-most rendered element and not visually hidden.
- **Output:** The script cleanly separates the output into JSON files: one containing all image bloat `allimages.json`, one containing strictly the 9 visible images `visibleimages.json`, and a text file for the visible instructions `instructions.txt`.

---

I enjoyed tackling these distinct challenges. Please let me know if you have any questions about my approach or implementation!
