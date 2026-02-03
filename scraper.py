import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import json

# --- SETTINGS ---
CITY = "mumbai"
SHEET_NAME = "Pixie_Event_Tracker"

def connect_to_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # GitHub Actions ke liye: Secret se credentials lega
    # Local ke liye: credentials.json file se lega
    if os.path.exists('credentials.json'):
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    else:
        creds_json = os.getenv('GCP_CREDENTIALS')
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1

def fetch_events(city):
    url = f"https://in.bookmyshow.com/explore/events-{city.lower()}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    print(f"Requesting URL: {url}")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    extracted_events = []
    
    # BookMyShow ke common event card selectors (Yeh update hote rehte hain)
    # Agar site structure change ho, toh yahan logic update karein
    cards = soup.find_all('div', {'style': 'cursor:pointer'}) # Common container
    
    for card in cards:
        try:
            name_tag = card.find('div', style=lambda v: v and 'font-size:18px' in v) or card.find('h3')
            if not name_tag: continue
            
            name = name_tag.text.strip()
            # Unique URL generate karein taaki deduplication ho sake
            link_tag = card.find_parent('a') or card.find('a')
            link = "https://in.bookmyshow.com" + link_tag['href'] if link_tag else "N/A"
            
            # Date/Venue logic (Agar site par accessible hai)
            extracted_events.append({
                "name": name,
                "date": datetime.now().strftime('%Y-%m-%d'), # Defaulting to today for demo
                "venue": "Check Link",
                "city": city.capitalize(),
                "url": link,
                "category": "Event",
                "status": "Active"
            })
        except Exception as e:
            continue
            
    return extracted_events

def sync_to_sheet(sheet, events):
    # Get all existing rows
    existing_records = sheet.get_all_records()
    existing_urls = [str(row.get('URL', '')) for row in existing_records]
    today = datetime.now().date()

    # 1. Deduplication: Add only if URL is new
    new_rows = []
    for event in events:
        if event['url'] not in existing_urls:
            new_rows.append([
                event['name'], event['date'], event['venue'], 
                event['city'], event['category'], event['url'], "Active"
            ])
            existing_urls.append(event['url']) # Temporary avoid double adds

    if new_rows:
        sheet.append_rows(new_rows)
        print(f"Added {len(new_rows)} new events.")
    else:
        print("No new events to add.")

    # 2. Expiry Logic: Mark old events as 'Expired'
    # Column 2 = Date, Column 7 = Status
    for i, row in enumerate(existing_records, start=2):
        try:
            event_date_str = str(row.get('Date', ''))
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
            if event_date < today and row.get('Status') != 'Expired':
                sheet.update_cell(i, 7, "Expired")
        except:
            continue

if __name__ == "__main__":
    try:
        sheet = connect_to_sheets()
        print("Connected to Sheet.")
        scraped_data = fetch_events(CITY)
        print(f"Scraped {len(scraped_data)} events.")
        sync_to_sheet(sheet, scraped_data)
        print("Automation Script Finished.")
    except Exception as e:
        print(f"Script Error: {e}")