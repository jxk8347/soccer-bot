import time
import os
from playwright.sync_api import sync_playwright
import requests

# Store login session so you don't need to log in every run
USER_DATA_DIR = os.path.join(os.path.expanduser("~"), "soccerprop_session")

# Discord webhook
WEBHOOK_URL = ""

# Track seen props
seen_props = {
    "Passes Attempted": set(),
    "Clearances": set(),
    "Shots": set(),
    "Attempted Dribbles": set()
}

# Emojis for each stat type
EMOJIS = {
    "Passes Attempted": "🅿️",
    "Clearances": "🧹",
    "Shots": "🎯",
    "Attempted Dribbles": "🦶"
}

def send_discord_alert(stat_type, player, line):
    emoji = EMOJIS.get(stat_type, "⚽")
    content = f"{emoji} {stat_type} → **{player}** - **{line}**"
    print(f"📢 Sending: {content}")
    requests.post(WEBHOOK_URL, json={"content": content})

def scrape_stat_table(page, stat_type, table_id):
    try:
        table_locator = page.locator(f"#{table_id} tbody tr")
        row_count = table_locator.count()

        if row_count == 0:
            print(f"⚠️ {stat_type} table not found yet — skipping.")
            return

        for row in table_locator.all():
            cells = row.locator("td").all()
            if len(cells) >= 4:
                player_raw = cells[0].inner_text().strip().lower()

                # Skip removed, starting, or 🔥 props
                if any(term in player_raw for term in ["removed", "starting", "🔥"]):
                    continue

                player = cells[0].inner_text().strip()
                line = cells[3].inner_text().strip()

                if player not in seen_props[stat_type]:
                    send_discord_alert(stat_type, player, line)
                    seen_props[stat_type].add(player)

    except Exception as e:
        print(f"[!] Error scraping {stat_type}: {e}")

def run_bot():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(USER_DATA_DIR, headless=False)
        page = browser.new_page()

        # Login check
        print("🔐 Checking login...")
        page.goto("https://soccerprop.com/")
        if "login" in page.url:
            print("🔓 Please log in manually. Window will stay open for 60 seconds.")
            page.goto("https://soccerprop.com/login/")
            time.sleep(60)
            print("✅ Login session saved.")

        # Go to props page
        page.goto("https://soccerprop.com/todays-props/")
        time.sleep(3)

        stats = [
            ("Passes Attempted", "passesattempted-table"),
            ("Clearances", "clearances-table"),
            ("Shots", "shots-table"),
            ("Attempted Dribbles", "dribblesattempted-table")
        ]

        for stat_type, table_id in stats:
            scrape_stat_table(page, stat_type, table_id)

        browser.close()

if __name__ == "__main__":
    print("🚀 Bot started.")
    first_run = True

    while True:
        try:
            if first_run:
                # First run: mark existing props as seen (no alerts)
                with sync_playwright() as p:
                    browser = p.chromium.launch_persistent_context(USER_DATA_DIR, headless=False)
                    page = browser.new_page()
                    page.goto("https://soccerprop.com/todays-props/")
                    time.sleep(3)

                    stats = [
                        ("Passes Attempted", "passesattempted-table"),
                        ("Clearances", "clearances-table"),
                        ("Shots", "shots-table"),
                        ("Attempted Dribbles", "dribblesattempted-table")
                    ]

                    for stat_type, table_id in stats:
                        try:
                            table_locator = page.locator(f"#{table_id} tbody tr")
                            for row in table_locator.all():
                                cells = row.locator("td").all()
                                if len(cells) >= 4:
                                    player = cells[0].inner_text().strip()
                                    seen_props[stat_type].add(player)
                        except:
                            pass

                    browser.close()

                first_run = False
                print("✅ First run complete — existing props stored, no alerts sent.")

            else:
                run_bot()

            print("⏱️ Waiting 2 minutes...\n")
            time.sleep(120)

        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(60)
