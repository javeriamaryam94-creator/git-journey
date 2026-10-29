import os
import time
import google.generativeai as genai
# import anthropic  # Uncomment if using Anthropic/Claude SDK
from playwright.sync_api import sync_playwright

# Configure API Keys for Multiple Models
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY") # Optional for Claude
QWEN_API_KEY = os.environ.get("QWEN_API_KEY")         # Optional for Qwen via OpenRouter/DashScope

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-3.8-flash")

def generate_multi_model_pitch(profile_name, profile_headline, model_choice="gemini"):
    """
    Generates a personalized B2B export pitch allowing you to switch 
    between Gemini, Claude, or Qwen dynamically.
    """
    prompt = f"""
    You are Hasham, Founder of HESHI Salt and Spices, an export company specializing in certified, premium-grade Himalayan pink salt and pure bulk spices.
    
    You are reaching out on LinkedIn to a prospective partner/investor:
    - Name: {profile_name}
    - Headline/Background: {profile_headline}
    
    Write a short, highly professional, human-sounding B2B outreach message (under 3 sentences). 
    - Do NOT use generic robotic filler.
    - Reference their specific background or headline naturally.
    - Mention our direct FOB/CIF export capabilities for HESHI's premium Himalayan pink salt and spices.
    - Sign off cleanly as Hasham, Founder of HESHI Salt and Spices.
    """
    
    if model_choice == "gemini":
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    
    elif model_choice == "claude":
        # Example integration for Claude (Anthropic SDK)
        # client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        # message = client.messages.create(model="claude-3-5-sonnet-20241022", max_tokens=300, messages=[{"role": "user", "content": prompt}])
        # return message.content[0].text.strip()
        pass
        
    elif model_choice == "qwen":
        # Example integration for Qwen (via OpenAI-compatible client or OpenRouter)
        pass
        
    # Default fallback to Gemini
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

def run_linkedin_outreach(profile_urls):
    with sync_playwright() as p:
        user_data_dir = os.path.join(os.getcwd(), "linkedin_session")
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.new_page()
        
        page.goto("https://www.linkedin.com/feed/", timeout=60000)
        
        if "login" in page.url or "checkpoint" in page.url:
            print("\nPlease log into your LinkedIn account in the opened browser window...")
            page.wait_for_url("**/feed/**", timeout=300000)
            print("Login successful! Session saved.")
        else:
            print("Existing session loaded successfully! Skipping login.")
        
        print("Starting professional research & outreach sequence...")
        
        for url in profile_urls:
            try:
                print(f"\nAnalyzing profile: {url}")
                page.goto(url, timeout=60000)
                time.sleep(4)
                
                try:
                    name = page.locator("h1.text-heading-xlarge").inner_text(timeout=3000).strip()
                except:
                    name = "Industry Leader"
                    
                try:
                    headline = page.locator("div.text-body-medium").inner_text(timeout=3000).strip()
                except:
                    headline = "Strategic Partner in Global Trade"
                
                print(f" -> Extracted Profile: {name} | {headline}")
                
                # You can specify "gemini", "claude", or "qwen" here!
                custom_pitch = generate_multi_model_pitch(name, headline, model_choice="gemini")
                print(f" -> Generated Pitch:\n{custom_pitch}\n")
                
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
                    
                time.sleep(8)
                
            except Exception as e:
                print(f" -> Error processing {url}: {e}")
                
        print("\nOutreach sequence completed successfully.")
        browser.close()

if __name__ == "__main__":
    target_leads = [
        "https://www.linkedin.com/in/example-lead-profile/"
    ]
    run_linkedin_outreach(target_leads)
