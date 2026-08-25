import os
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google import genai


LEADS_XLSX = Path("leads.xlsx")
MODEL_NAME = "models/gemini-2.0-flash"


def build_prompt(biz_name, biz_rating, biz_website, manual_notes_from_terminal):
    return f"""
ACT AS: A Senior Conversion Rate Optimization (CRO) Consultant. ou are a Senior Conversion Rate Optimization (CRO) and UI/UX Specialist with 15 years of experience in High-Ticket Lead Generation. Your goal is to identify why a website is 'leaking' money and how to fix it
I am providing two screenshots (Desktop and Mobile) for [Business Name].
My Manual Observations: [Insert your notes here, e.g., 'The order button is hidden at the bottom of the page.']

Task 1: The UI Audit
Conduct a heuristic evaluation. Provide:

The 5-Second Test: Is it immediately clear what they sell and how to buy it?

Mobile Friction: Identify 2 mobile-specific issues (e.g., tap targets too small, text overlap).

Conversion Killers: List 3 'Red Flag' design flaws that prevent users from converting.

Task 2: The Cold Outreach Email
Write a 3nd-person cold email to the owner.

Tone: Professional, helpful, and non-spammy.

Subject Line: Use a 'Pattern Interrupt' (e.g., 'A quick observation about [Business Name] Mobile UI').

Content: Mention their [Rating] star rating. Be specific about one design flaw from the audit.

Call to Action: Ask for a 5-minute chat to show them a mockup of a fix.

Constraint: Keep the email under 120 words."
BUSINESS: {biz_name} (Rating: {biz_rating} stars)
WEBSITE: {biz_website}

OBSERVED UI FLAWS: {manual_notes_from_terminal}
   - Reference their {biz_rating} star rating to build rapport.
   - Specifically mention how fixing the "{manual_notes_from_terminal}" will increase their bookings.
   - Tone should be "Helpful Expert," not "Salesperson."
"""


def ensure_columns(df):
    required_columns = [
        "Name",
        "Website",
        "Rating",
        "Manual_Notes",
        "Audit_Generated",
        "Full_Audit",
        "Draft_Email",
    ]
    for col in required_columns:
        if col not in df.columns:
            if col == "Audit_Generated":
                df[col] = "False"
            else:
                df[col] = ""
    return df


def parse_ai_response(text):
    content = (text or "").strip()
    if not content:
        return "", ""

    separators = ["\n\nCold Email:", "\n\nEmail:", "\n\nDRAFT EMAIL:"]
    for sep in separators:
        if sep in content:
            left, right = content.split(sep, 1)
            return left.strip(), right.strip()

    lines = [line for line in content.splitlines() if line.strip()]
    if len(lines) > 6:
        return "\n".join(lines[:-4]).strip(), "\n".join(lines[-4:]).strip()

    return content, ""


def generate_audit_and_email(client, biz_name, biz_rating, biz_website, manual_notes):
    prompt = build_prompt(biz_name, biz_rating, biz_website, manual_notes)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[prompt],
    )
    return response.text or ""


def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment or .env")

    if not LEADS_XLSX.exists():
        raise FileNotFoundError("leads.xlsx not found. Run Landscape.py first.")

    client = genai.Client(api_key=api_key)

    df = pd.read_excel(LEADS_XLSX)
    df = ensure_columns(df)

    pending = df[df["Audit_Generated"].astype(str).str.lower() == "false"]
    if pending.empty:
        print("No businesses pending audit generation.")
        return

    print("Businesses pending audit generation:")
    for idx, row in pending.iterrows():
        print(f"- Row {idx}: {row.get('Name', 'Unknown')} | {row.get('Website', '')}")

    for idx, row in pending.iterrows():
        biz_name = str(row.get("Name", "Business") or "Business")
        biz_rating = str(row.get("Rating", "N/A") or "N/A")
        biz_website = str(row.get("Website", "") or "")

        manual_notes = input(f"Please enter UI/UX flaws observed for {biz_name}: ").strip()
        if not manual_notes:
            print(f"Skipping {biz_name}: no manual notes provided.")
            continue

        while True:
            try:
                ai_text = generate_audit_and_email(
                    client, biz_name, biz_rating, biz_website, manual_notes
                )
                full_audit, draft_email = parse_ai_response(ai_text)

                df.at[idx, "Manual_Notes"] = manual_notes
                df.at[idx, "Full_Audit"] = full_audit
                df.at[idx, "Draft_Email"] = draft_email if draft_email else ai_text
                df.at[idx, "Audit_Generated"] = "True"

                df.to_excel(LEADS_XLSX, index=False, engine="openpyxl")
                print(f"Saved audit + email for {biz_name}")
                break
            except Exception as e:
                error_text = str(e)
                if "429" in error_text or "resource exhausted" in error_text.lower():
                    print("429 rate limit hit. Sleeping 65 seconds and retrying...")
                    time.sleep(65)
                    continue
                print(f"Failed to generate audit for {biz_name}: {e}")
                break


if __name__ == "__main__":
    main()
