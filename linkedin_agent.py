import os
import time
import google.generativeai as genai
import anthropic
import requests
from playwright.sync_api import sync_playwright

# --- API KEY CONFIGURATION ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY") # Used for Qwen & Arena consensus

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-3.8-flash")

def get_claude_pitch(prompt):
    if not ANTHROPIC_API_KEY:
        return None
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=250,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()
    except Exception as e:
        print(f" -> Claude API Error: {e}")
        return None

def get_qwen_pitch(prompt):
    if not OPENROUTER_API_KEY:
        return None
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "qwen/qwen-2.5-72b-instruct",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f" -> Qwen API Error: {e}")
        return None

def get_gemini_pitch(prompt):
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f" -> Gemini API Error: {e}")
        return None

def generate_arena_team_pitch(profile_name, profile_headline):
    """
    Acts as an Arena Orchestrator: Asks Gemini, Claude, and Qwen to draft 
    the pitch independently, then uses Gemini to judge/synthesize the absolute 
    best, most professional human-like response.
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
    
    print(" -> Summoning AI Team (Gemini, Claude, Qwen)...")
    
    # Gather drafts from available models
    gemini_draft = get_gemini_pitch(prompt)
    claude_draft = get_claude_pitch(prompt)
    qwen_draft = get_qwen_pitch(prompt)
    
    valid_drafts = [d for d in [gemini_draft, claude_draft, qwen_draft] if d]
    
    if not valid_drafts:
        return "Hi " + profile_name + ", reaching out from HESHI Salt and Spices regarding premium Himalayan pink salt exports. Best, Hasham"

    if len(valid_drafts) == 1:
        return valid_drafts[0]

    # Arena Consensus / Judge Step: Have Gemini review the drafts and pick or refine the best one
    arena_judge_prompt = f"""
    You are an expert chief communications officer reviewing B2B outreach drafts written by top AI models (Gemini, Claude, Qwen) for Hasham, Founder of HESHI Salt and Spices.
    
    Candidate Drafts:
    {valid_drafts}
    
    Select the most natural, human-sounding, polished, and persuasive draft. Output ONLY the final revised message text, ensuring it signs off cleanly as Hasham, Founder of HESHI Salt and Spices. No extra commentary.
    """
    
    final_response = gemini_model.generate_content(arena_judge_prompt)
    return final_response.text.strip()

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
        
        print("Starting professional Arena team outreach sequence...")
        
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
                
                # Run the multi-model Arena team consensus
                custom_pitch = generate_arena_team_pitch(name, headline)
                print(f" -> Winning Arena Pitch:\n{custom_pitch}\n")
                
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
