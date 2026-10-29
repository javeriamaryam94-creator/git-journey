import os
import time
import google.generativeai as genai
from playwright.sync_api import sync_playwright

# Configure AI Models
# You can swap model_engine between "gemini-3.8-flash", "claude-3-5-sonnet", or "qwen-max"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-3.8-flash")

def generate_personalized_pitch(profile_name, profile_headline):
    """
    Acts as an elite B2B Export Executive. Uses multi-model logic 
    to write a deeply researched, human-like outreach pitch.
    """
    prompt = f"""
    You are Javeria Mariam, Co-Founder and Head of Technical Operations at an export company specializing in certified, premium-grade Himalayan pink salt and pure bulk spices.
    
    You are reaching out on LinkedIn to a prospective partner/investor:
    - Name: {profile_name}
    - Headline/Background: {profile_headline}
    
    Write a short, highly professional, human-sounding B2B outreach message (under 3 sentences). 
    - Do NOT use generic robotic filler.
    - Reference their specific background or headline naturally.
    - Mention our direct FOB/CIF export capabilities for premium Himalayan pink salt and spices.
    - Sign off cleanly as Javeria Mariam.
    """
    
    # Utilizing Gemini (or extensible to Claude/Qwen endpoints)
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

def run_linkedin_outreach(profile_urls):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Go to LinkedIn login
        page.goto("https://www.linkedin.com/login")
        print("Please log into your LinkedIn account in the browser window...")
        page.wait_for_url("**/feed/**", timeout=300000)
        print("Login detected! Starting professional research & outreach sequence...")
        
        for url in profile_urls:
            try:
                print(f"\nAnalyzing profile: {url}")
                page.goto(url, timeout=60000)
                time.sleep(4)
                
                # Scrape profile details for human-like personalization
                # Fallbacks if elements vary between personal profiles and company pages
                try:
                    name = page.locator("h1.text-heading-xlarge").inner_text(timeout=3000).strip()
                except:
                    name = "Industry Leader"
                    
                try:
                    headline = page.locator("div.text-body-medium").inner_text(timeout=3000).strip()
                except:
                    headline = "Strategic Partner in Global Trade"
                
                print(f" -> Extracted Profile: {name} | {headline}")
                
                # Generate tailored pitch
                custom_pitch = generate_personalized_pitch(name, headline)
                print(f" -> Generated Pitch:\n{custom_pitch}\n")
                
                # Action: Open message box
                message_btn = page.locator("button:has-text('Message')").first
                if message_btn.is_visible():
                    message_btn.click()
                    time.sleep(2)
                    
                    msg_box = page.locator("div.msg-form__contenteditable")
                    if msg_box.is_visible():
                        msg_box.fill(custom_pitch)
                        time.sleep(1.5)
                        try:
                            page.locator("button.msg-form__send-button").click(force=True)
                        except:
                            msg_box.press("Enter")
                        print(f" -> Tailored message successfully sent to {name}!")
                else:
                    print(f" -> Direct message button not immediately available for {url}")
                    
                time.sleep(8) # Natural human delay between profiles
                
            except Exception as e:
                print(f" -> Error processing {url}: {e}")
                
        print("\nOutreach sequence completed successfully.")
        browser.close()

if __name__ == "__main__":
    # Add your target individual or decision-maker profiles here
    target_leads = [
        "https://www.linkedin.com/in/example-lead-profile/" # Replace with actual target profiles
    ]
    run_linkedin_outreach(target_leads)
    # run_linkedin_outreach(target_leads)
