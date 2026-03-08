# ABM Assessment

This project is a scalable automation framework built with Python and Async Playwright. It focuses on robust architectural design, stealth evasion for bot protection (e.g. Cloudflare Turnstile), network request interception, and generic DOM/Image scraping utilities.

## Directory Structure

- `src/task1-3/`: Core modules encapsulating the logic for stealth driving, network interception, and content parsing along with a readme describing the logic.
- `src/system_design/`: Architectural diagram and readme describing the structure.

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Run the tests:
   ```bash
   pytest tests/
   ```
