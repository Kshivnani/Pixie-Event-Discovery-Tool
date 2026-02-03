# 🚀 Pixie Event Discovery & Automation Tool

An automated system designed to discover, track, and manage event data from platforms like BookMyShow and District, syncing everything into a centralized Google Spreadsheet.

## 🌟 Key Features

- **Automated Scraping:** Uses Python (BeautifulSoup) to fetch event details.
- **Smart Deduplication:** Automatically checks for existing event URLs in the Google Sheet to prevent duplicate entries.
- **Auto-Expiry Logic:** Identifies past events and marks their status as "Expired" automatically.
- **Cloud Automation:** Integrated with **GitHub Actions** to run on a daily schedule (Cron Job) without manual intervention.
- **City-Based Filtering:** Easily configurable to track events for specific cities (e.g., Mumbai, Delhi).

## 🛠️ Tech Stack

- **Language:** Python 3.x
- **Storage:** Google Sheets API (via `gspread`)
- **Automation:** GitHub Actions (CI/CD)
- **Scraping:** BeautifulSoup4 & Requests

## 📂 Project Structure

```text
├── .github/workflows/
│   └── main.yml         # GitHub Actions automation config
├── scraper.py           # Main Python logic
├── requirements.txt     # Python dependencies
├── .gitignore           # Prevents sensitive data (credentials) from being public
└── README.md            # Project documentation
