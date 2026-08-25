import argparse
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from playwright.sync_api import sync_playwright


LEADS_XLSX = Path("leads.xlsx")
COLUMNS = [
    "Name",
    "Website",
    "Phone",
    "Rating",
    "Address",
    "Google_Maps_Link",
    "Manual_Notes",
    "Audit_Generated",
]


@dataclass
class Business:
    name: str = ""
    website: str = ""
    phone: str = "N/A"
    rating: str = "N/A"
    address: str = "N/A"
    google_maps_link: str = ""


def parse_args():
    parser = argparse.ArgumentParser(description="Scrape Google Maps leads into leads.xlsx")
    parser.add_argument(
        "--query",
        default="bakery sacramento ca",
        help="Google Maps search query (default: bakery sacramento ca)",
    )
    parser.add_argument(
        "--max-listings",
        type=int,
        default=5,
        help="Maximum listings to process from the current results page.",
    )
    return parser.parse_args()


def load_existing_leads():
    if not LEADS_XLSX.exists():
        return pd.DataFrame(columns=COLUMNS)

    df = pd.read_excel(LEADS_XLSX)
    for col in COLUMNS:
        if col not in df.columns:
            default_value = "" if col == "Manual_Notes" else "False" if col == "Audit_Generated" else ""
            df[col] = default_value
    return df[COLUMNS]


def get_seen_websites(df):
    websites = df["Website"].fillna("").astype(str).str.strip()
    return {website for website in websites if website}


def save_lead_row(existing_df, biz):
    new_row = pd.DataFrame(
        [
            {
                "Name": biz.name,
                "Website": biz.website,
                "Phone": biz.phone,
                "Rating": biz.rating,
                "Address": biz.address,
                "Google_Maps_Link": biz.google_maps_link,
                "Manual_Notes": "",
                "Audit_Generated": "False",
            }
        ]
    )
    updated_df = pd.concat([existing_df, new_row], ignore_index=True)
    updated_df.to_excel(LEADS_XLSX, index=False, engine="openpyxl")
    return updated_df


def get_website(page):
    web_loc = page.locator('a[aria-label*="website"]')
    if web_loc.count() == 0:
        return ""
    return web_loc.get_attribute("href") or ""


def get_phone(page):
    phone_loc = page.locator('button[aria-label*="Phone"]')
    return phone_loc.inner_text() if phone_loc.count() > 0 else "N/A"


def get_rating(page):
    rating_loc = page.locator('div.F7nice span[aria-hidden="true"]')
    return rating_loc.first.inner_text() if rating_loc.count() > 0 else "N/A"


def get_address(page):
    addr_loc = page.locator('button[aria-label^="Address:"]')
    if addr_loc.count() == 0:
        return "N/A"
    label = addr_loc.first.get_attribute("aria-label") or ""
    return label.replace("Address:", "").strip() or "N/A"


def get_google_maps_link(page):
    return page.url


def main():
    args = parse_args()

    leads_df = load_existing_leads()
    seen_websites = get_seen_websites(leads_df)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        print("Searching Google Maps...")
        query_slug = args.query.strip().replace(" ", "+")
        page.goto(f"https://www.google.com/maps/search/{query_slug}")
        page.wait_for_selector('a[href*="/maps/place/"]', timeout=10000)

        listings = page.locator('a[href*="/maps/place/"]').all()[: args.max_listings]
        print(f"Found {len(listings)} listings.")

        for i, listing in enumerate(listings):
            biz = Business()
            try:
                print(f"Processing listing {i + 1}...")
                listing.click()
                page.wait_for_timeout(3000)

                biz.name = page.locator("h1.DUwDvf").inner_text().strip()
                biz.website = get_website(page).strip()
                biz.phone = get_phone(page)
                biz.rating = get_rating(page)
                biz.address = get_address(page)
                biz.google_maps_link = get_google_maps_link(page)

                if not biz.website:
                    print(f"Skipping {biz.name}: no website")
                    continue
                if biz.website in seen_websites:
                    print(f"Skipping {biz.name}: already in leads.xlsx")
                    continue

                leads_df = save_lead_row(leads_df, biz)
                seen_websites.add(biz.website)
                print(f"Saved lead: {biz.name}")

            except Exception as e:
                print(f"Failed listing {i + 1}: {e}")

        browser.close()


if __name__ == "__main__":
    main()
