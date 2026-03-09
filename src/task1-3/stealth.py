import asyncio
from playwright.sync_api import sync_playwright
from seleniumbase import sb_cdp, SB 

def run_turnstile_attempt(mode):
    # if mode == True:
    #     sb = sb_cdp.Chrome()
    #     cdp_url = sb.get_endpoint_url()
    # else:    
    with SB(uc= True, headless2=mode) as sb:
        sb.uc_open_with_reconnect("http://cd.captchaaiplus.com/turnstile.html",5)
        # Handle the CAPTCHA if it appears
        
        # 3. GET THE BRIDGE ADDRESS
        # We extract the specific port Chrome is listening on
        c_options = sb.driver.capabilities.get("goog:chromeOptions")
        debugger_address = c_options.get("debuggerAddress") # e.g., "localhost:9222"
        cdp_url = f"http://{debugger_address}"
    
        with sync_playwright() as p:
            # Launch browser (supports both headless True and False) 
            browser = p.chromium.connect_over_cdp(cdp_url)
            context = browser.contexts[0]
            page = context.pages[0]   
            try:
                # 2. Wait for the Turnstile verification process
                #wait for the injection of the token
                # into the hidden input field: 'cf-turnstile-response'
                page.wait_for_function(
                    "() => {"
                    "  const el = document.querySelector('[name=cf-turnstile-response]');"
                    "  return el && el.value.length > 0;"
                    "}", timeout=30000
                )
                
                # 3. Extract the Turnstile Token 
                token = page.eval_on_selector("[name='cf-turnstile-response']", "el => el.value")
                
                # 4. Click Submit 
                page.get_by_role("button", name="Submit").click()
                
                # 5. Verify the final success message
                final_msg = page.get_by_text("Success! Turnstile verified.")
                final_msg.wait_for(state="visible")
                
                print(f"Token Retrieved: {token[:50]}...")
                sb.sleep(2)
                browser.close()
                return True
            except Exception as e:
                print(f"Attempt failed: {e}")
                browser.close()
                return False

def main():
    attempts = 10
    success_count = 0
    # Requirement: Test in both headless True and False 
    modes = [True] * 5 + [False] * 5
    
    for i, mode in enumerate(modes):
        print(f"--- Starting Attempt {i+1} (Headless: {mode}) ---")
        success = run_turnstile_attempt(mode)
        if success:
            success_count += 1
            
    # Calculate and print final success rate 
    success_rate = (success_count / attempts) * 100
    print(f"\nFinal Success Rate: {success_rate}%")

if __name__ == "__main__":
    main()