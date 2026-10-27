import os
import time
import google.generativeai as genai
from playwright.sync_api import sync_playwright

# Configure Gemini AI
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_reply(incoming_message, guidelines):
    prompt = f"""
    You are an expert B2B export manager for a salt and spices export company.
    Follow these company guidelines: {guidelines}
    
    Incoming buyer message on LinkedIn: "{incoming_message}"
    
    Write a professional, concise response keeping the tone executive and polite:
    """
    response = model.generate_content(prompt)
    return response.text.strip()

def run_linkedin_outreach(profile_urls):
    with sync_playwright() as p:
        # Launch browser in non-headless mode so you can log in manually the first time if needed
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Go to LinkedIn
        page.goto("https://www.linkedin.com/login")
        print("Please log into your LinkedIn account in the opened browser window...")
        
        # Wait until user is logged in (detects feed URL)
        page.wait_for_url("**/feed/**", timeout=60000)
        print("Login detected! Starting outreach sequence...")

        for url in profile_urls:
            try:
                print(f"Visiting profile: {url}")
                page.goto(url)
                time.sleep(3) # Wait for page load
                
                # Attempt to find and click the Connect button
                connect_btn = page.locator("button:has-text('Connect')").first
                if connect_btn.is_visible():
                    connect_btn.click()
                    time.sleep(1)
                    
                    # Optional: Click 'Add a note' and send personalized pitch via Gemini
                    add_note_btn = page.locator("button:has-text('Add a note')")
                    if add_note_btn.is_visible():
                        add_note_btn.click()
                        
                        # Generate personalized note via Gemini
                        note_prompt = "Write a brief 2-sentence B2B connection note pitching Himalayan pink salt and spices exports."
                        note_text = model.generate_content(note_prompt).text.strip()[:300] # LinkedIn limit
                        
                        page.locator("textarea[name='message']").fill(note_text)
                        page.locator("button:has-text('Send')").click()
                        print(f" -> Connection invite sent with personalized note to {url}")
                
                # Random delay to mimic human behavior and protect account
                time.sleep(10)
                
            except Exception as e:
                print(f" -> Error interacting with {url}: {e}")

        browser.close()
if __name__ == "__main__":
    # Add your target LinkedIn profile URLs here
    target_leads = [
        "https://www.linkedin.com/company/zaynvc/",
        "https://www.linkedin.com/company/indusvalleycap",
        "https://www.linkedin.com/company/sarmayacar/",
        "https://pk.linkedin.com/company/fatima-gobi-ventures",
        "https://pk.linkedin.com/company/i2i-ventures"
    ]
    run_linkedin_outreach(target_leads)
    ]
    # run_linkedin_outreach(target_leads)
