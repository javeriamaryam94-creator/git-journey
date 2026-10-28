import os
import time
import google.generativeai as genai
from playwright.sync_api import sync_playwright

# Configure Gemini AI
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_reply(incoming_message, guidelines="Emphasize high-grade pink salt and spice bulk exports, FOB/CIF terms, and professional responsiveness."):
    prompt = f"""
You are an expert B2B export manager for a salt and spices export company. Follow these company guidelines: {guidelines}
Incoming buyer message on LinkedIn: "{incoming_message}"
Write a professional, concise response keeping the tone executive and polite:
"""
    response = model.generate_content(prompt)
    return response.text.strip()

def run_linkedin_outreach_and_messaging(profile_urls):
    with sync_playwright() as p:
        # Launch browser in non-headless mode so you can log in manually
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Go to LinkedIn login
        page.goto("https://www.linkedin.com/login")
        print("Please log into your LinkedIn account in the opened browser window...")
        
        # Wait until user is logged in (detects feed URL - 5 min timeout)
        page.wait_for_url("**/feed/**", timeout=300000)
        print("Login detected! Starting outreach & inbox monitoring sequence...")

        # --- PART 1: OUTREACH TO TARGET LEADS ---
        for url in profile_urls:
            try:
                print(f"Visiting profile: {url}")
                page.goto(url, timeout=60000)
                time.sleep(3) # Wait for page load
                
                # Attempt to find and click the Connect button
                connect_btn = page.locator("button:has-text('Connect')").first
                if connect_btn.is_visible():
                    connect_btn.click()
                    time.sleep(1)
                    
                    # Click 'Add a note' and send personalized pitch via Gemini
                    add_note_btn = page.locator("button:has-text('Add a note')")
                    if add_note_btn.is_visible():
                        add_note_btn.click()
                        
                        note_prompt = "Write a brief 2-sentence B2B connection note pitching Himalayan pink salt and spices bulk exports."
                        note_text = model.generate_content(note_prompt).text.strip()[:300]
                        
                        page.locator("textarea[name='message']").fill(note_text)
                        page.locator("button:has-text('Send')").click()
                        print(f" -> Connection invite sent with personalized note to {url}")
                else:
                    print(f" -> Connect button not directly visible on {url} (already connected or requires Follow)")
                
                time.sleep(10) # Human-like delay
            except Exception as e:
                print(f" -> Error interacting with {url}: {e}")

        # --- PART 2: CHECK INBOX & AUTO-REPLY TO BUYERS ---
        print("\nNavigating to LinkedIn Messaging to check for incoming inquiries...")
        page.goto("https://www.linkedin.com/messaging/", timeout=60000)
        time.sleep(5)

        try:
            # Select the first unread conversation (or top conversation)
            first_conv = page.locator(".msg-conversation-listitem").first
            if first_conv.is_visible():
                first_conv.click()
                time.sleep(3)

                # Get the latest message from the chat history
                messages = page.locator(".msg-s-event-listitem__body").all_text_contents()
                if messages:
                    latest_incoming = messages[-1]
                    print(f"Latest buyer message detected: '{latest_incoming}'")

                    # Generate AI response
                    ai_response = generate_reply(latest_incoming)
                    print(f"Generated AI Reply: '{ai_response}'")

                    # Type and send reply in messaging box
                    msg_box = page.locator("div.msg-form__contenteditable")
                    if msg_box.is_visible():
                        msg_box.fill(ai_response)
                        time.sleep(1)
                        page.locator("button.msg-form__send-button").click()
                        print(" -> Automated reply successfully sent to buyer!")
            else:
                print("No active conversations found in inbox.")
        except Exception as e:
            print(f" -> Messaging automation note: {e}")

        print("\nAgent sequence completed successfully!")
        browser.close()

if __name__ == "__main__":
    # Swap these out for individual founder/investor profile URLs to test connection notes
    target_leads = [
        # Example format: "https://www.linkedin.com/in/username/"
    ]
    run_linkedin_outreach_and_messaging(target_leads)
    # run_linkedin_outreach(target_leads)
