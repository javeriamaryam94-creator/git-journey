import os
import time
import google.generativeai as genai
from playwright.sync_api import sync_playwright

# Configure Gemini AI
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

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
                
                # Check for Connect button first
                connect_btn = page.locator("button:has-text('Connect')").first
                message_btn = page.locator("button:has-text('Message')").first
                follow_btn = page.locator("button:has-text('Follow')").first

                if connect_btn.is_visible():
                    connect_btn.click()
                    time.sleep(1)
                    
                    # Click 'Add a note' if available
                    add_note_btn = page.locator("button:has-text('Add a note')")
                    if add_note_btn.is_visible():
                        add_note_btn.click()
                        
                        note_prompt = "Write a brief 2-sentence B2B connection note pitching Himalayan pink salt and spices bulk exports."
                        note_text = model.generate_content(note_prompt).text.strip()[:300]
                        
                        page.locator("textarea[name='message']").fill(note_text)
                        page.locator("button:has-text('Send')").click()
                        print(f" -> Connection invite sent with note to {url}")
                elif message_btn.is_visible():
                    message_btn.click()
                    time.sleep(2)
                    print(f" -> Opened direct message window for {url}")
                    
                    # Optional: Send direct pitch if message box opens
                    msg_box = page.locator("div.msg-form__contenteditable")
                    if msg_box.is_visible():
                        pitch_prompt = "Write a short, polite 2-sentence B2B sales message pitching bulk Himalayan salt and spices exports."
                        pitch_text = model.generate_content(pitch_prompt).text.strip()
                        msg_box.fill(pitch_text)
                        time.sleep(1)
                        page.locator("button.msg-form__send-button").click()
                        print(f" -> Direct pitch message sent to {url}")
                elif follow_btn.is_visible():
                    follow_btn.click()
                    print(f" -> Clicked Follow for {url}")
                else:
                    print(f" -> No direct action button found on {url}")
                
                time.sleep(10) # Human-like delay
            except Exception as e:
                print(f" -> Error interacting with {url}: {e}")
        # --- PART 2: CHECK INBOX & AUTO-REPLY TO BUYERS ---
        print("\nNavigating to LinkedIn Messaging to check for incoming inquiries...")
        page.goto("https://www.linkedin.com/messaging/", timeout=60000)
        time.sleep(5)

        try:
            # Select the first conversation in the list
            first_conv = page.locator(".msg-conversation-listitem").first
            if first_conv.is_visible():
                first_conv.click()
                time.sleep(3)

                # Check if the last message has a badge or class indicating it's sent BY YOU
                # LinkedIn outgoing messages typically contain 'msg-s-event--currentUser'
                last_msg_item = page.locator(".msg-s-event-listitem").last
                
                if last_msg_item.is_visible():
                    classes = last_msg_item.get_attribute("class") or ""
                    
                    if "msg-s-event--currentUser" in classes:
                        print(" -> Last message was sent by YOU. Skipping auto-reply to avoid replying to yourself.")
                    else:
                        # It's an incoming message from the lead!
                        latest_incoming = last_msg_item.locator(".msg-s-event-listitem__body").inner_text()
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
                    print("No messages found in the active conversation.")
            else:
                print("No active conversations found in inbox.")
        except Exception as e:
            print(f" -> Messaging automation note: {e}")

        print("\nAgent sequence completed successfully!")
        browser.close()

if __name__ == "__main__":
    target_leads = [
        "https://www.linkedin.com/company/zaynvc/",
        "https://www.linkedin.com/company/indusvalleycap",
        "https://www.linkedin.com/company/sarmayacar/",
        "https://pk.linkedin.com/company/fatima-gobi-ventures",
        "https://pk.linkedin.com/company/i2i-ventures"
    ]
    run_linkedin_outreach_and_messaging(target_leads)
    # run_linkedin_outreach(target_leads)
