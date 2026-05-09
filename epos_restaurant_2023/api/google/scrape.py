import frappe
from playwright.sync_api import sync_playwright
import os

def get_google_image(q):
    query = q
    if q =="":
        return []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ]
        )
        
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        storage_state = os.path.join(
            current_dir,
            "..",
            "google",
            "google.json"
        )
        storage_state = os.path.abspath(storage_state) 
        
        # Load saved cookies
        context = browser.new_context(
            storage_state=storage_state,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/136.0.0.0 Safari/537.36"
            )
        )

        page = context.new_page()

        page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """)

        url = f"https://www.google.com/search?q={query}&udm=2&tbs=isz:m"
        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        # get all child items
        items = page.locator("div.wIjY0d.jFk0f").locator("> div")

        # wait images container
        page.wait_for_selector("div.wIjY0d.jFk0f")

        count = items.count()
        images = []
        for i in range(count):
            item = items.nth(i)

            try:
                # find image
                img_locator = item.locator("div.H8Rx8c img")

                # skip invalid item
                if img_locator.count() == 0:
                    continue

                img = img_locator.first

                src = (
                    img.get_attribute("src")
                    or img.get_attribute("data-src")
                    or img.get_attribute("data-iurl")
                )

                # get title text
                title_locator = item.locator("div.toI8Rb.OSrXXb")

                title = ""
                if title_locator.count() > 0:
                    title = title_locator.first.inner_text()
                    

                if src:
                    images.append({
                        "title": title,
                        "image": src
                    })
                    
            except Exception as e:
                print("ERROR:", e)
                
        browser.close()
         
    
        result = [d for d in images if d.get("image")!="data:image/gif;base64,R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="]        
        return result


@frappe.whitelist(allow_guest=True)
def query_image(q): 
    result = get_google_image(q)     
    return {
        "count":len(result),
        "data":result
    }
 