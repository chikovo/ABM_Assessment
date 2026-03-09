import json
from playwright.sync_api import sync_playwright


def run_scraper():
    url = "https://egypt.blsspainglobal.com/Global/CaptchaPublic/GenerateCaptcha?data=4CDiA9odF2%2b%2bsWCkAU8htqZkgDyUa5SR6waINtJfg1ThGb6rPIIpxNjefP9UkAaSp%2fGsNNuJJi5Zt1nbVACkDRusgqfb418%2bScFkcoa1F0I%3d"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()

        print(f"Opening URL:\n{url}\n")
        page.goto(url)

        try:
            # We wait for the main CAPTCHA container to be loaded, preventing timeout from Cloudflare
            page.wait_for_selector(".main-div-container", timeout=15000)
            page.wait_for_timeout(3000)
        except Exception as e:
            print("Timeout waiting for CAPTCHA grid to load.", e)

        # ---------------------------------------------------------
        # 1. Scrape all images
        # ---------------------------------------------------------
        print("Scraping ALL images...")
        all_images_b64 = []
        for img in page.locator("img").all():
            all_images_b64.append(img.get_attribute("src"))

        print(f"Found a total of {len(all_images_b64)} images on the page.")

        # ---------------------------------------------------------
        # 2. Scrape exactly the 9 visible images by Raycasting
        # ---------------------------------------------------------
        print("Scraping exactly the 9 VISIBLE images...")
        visible_images_b64 = []

        container = page.locator(".main-div-container")
        if container.count() > 0:
            box = container.bounding_box()
            if box:
                start_x = box["x"]
                start_y = box["y"] + 60  # Captcha grid has top:60px offset

                # We calculate the precise centers of the 3x3 grid cells (each cell is 110x110)
                centers = []
                for row in range(3):
                    for col in range(3):
                        cx = start_x + 55 + (col * 110)
                        cy = start_y + 55 + (row * 110)
                        centers.append((cx, cy))

                for i, (cx, cy) in enumerate(centers):
                    # Use Javascript just to get the top element at this exact pixel coordinate
                    visible_b64 = page.evaluate(
                        """([x, y]) => {
                        let topEl = document.elementFromPoint(x, y);
                        if (!topEl) return null;
                        
                        if (topEl.tagName.toLowerCase() === 'img') return topEl.src;
                        
                        let style = window.getComputedStyle(topEl);
                        if (style.backgroundImage && style.backgroundImage.includes('url(')) {
                            let match = style.backgroundImage.match(/url\\(["']?(.*?)["']?\\)/);
                            if (match) return match[1];
                        }
                        
                        let img = topEl.querySelector('img');
                        if (img) return img.src;
                        return null;
                    }""",
                        [cx, cy],
                    )

                    if visible_b64 and len(visible_b64) > 10:
                        if visible_b64 not in visible_images_b64:
                            visible_images_b64.append(visible_b64)
                            print(
                                f"  Visible Image {len(visible_images_b64)} found at ({cx}, {cy})"
                            )

        # ---------------------------------------------------------
        # 3. Scrape exactly the single visible instruction text
        # ---------------------------------------------------------
        print("\nScraping visible text instructions...")
        visible_texts = []
        labels = page.locator(".box-label").all()
        for lbl in labels:
            if lbl.is_visible():
                box = lbl.bounding_box()
                if box and box["width"] > 0 and box["height"] > 0:
                    cx = box["x"] + box["width"] / 2
                    cy = box["y"] + box["height"] / 2

                    # Verify if this label is physically the top-most rendered element
                    is_top = lbl.evaluate(
                        """(el, params) => {
                        let topEl = document.elementFromPoint(params.x, params.y);
                        return topEl === el || el.contains(topEl) || (topEl && topEl.contains(el));
                    }""",
                        {"x": cx, "y": cy},
                    )

                    if is_top:
                        text = lbl.inner_text().strip()
                        if text and text not in visible_texts:
                            visible_texts.append(text)

        # ---------------------------------------------------------
        # 4. Save results to files
        # ---------------------------------------------------------
        with open("allimages.json", "w", encoding="utf-8") as f:
            json.dump(all_images_b64, f, indent=4)
        print(f"\nSaved {len(all_images_b64)} total images to 'allimages.json'")

        with open("visible_images_only.json", "w", encoding="utf-8") as f:
            json.dump(visible_images_b64, f, indent=4)
        print(
            f"Saved {len(visible_images_b64)} VISIBLE images to 'visible_images_only.json'"
        )

        print("\n--- VISIBLE TEXT INSTRUCTIONS FOUND ---")
        for t in visible_texts:
            print(f"- {t}")
        print("---------------------------------------")

        with open("visible_instructions.txt", "w", encoding="utf-8") as f:
            f.write("\\n".join(visible_texts))

        print("\nDone! Data collected successfully.")

        # Prevent the browser from closing automatically
        print("\nBrowser is intentionally left open for inspection.")
        try:
            input(
                "Press ENTER in this terminal to close the browser and exit the script..."
            )
        except KeyboardInterrupt:
            pass

        browser.close()


if __name__ == "__main__":
    run_scraper()
