# Coingram (Crypto Tweet Analyzer)

## Overview

The **Coingram** is a web application that allows users to analyze cryptocurrency mentions in tweets from a specified Twitter influencer. By inputting a Twitter username and a timeframe (up to 7 days), the app fetches recent tweets, identifies mentions of cryptocurrencies (e.g., `$BTC`, `$SOL`), and retrieves their current prices and contract addresses from CoinGecko. The results are compiled into a CSV file, detailing token mentions, prices at specific intervals, and percentage changes, which users can download directly from the web interface.

This tool is designed for non-technical users, providing a simple front-end to explore how influencer tweets correlate with crypto market data, focusing on tokens with market caps between $2M and $20B.

## Features

- **Input**: Enter a Twitter username (e.g., "VitalikButerin") and number of days (1-7).
- **Tweet Analysis**: Scans tweets for crypto mentions prefixed with "$" (e.g., `$ETH`), excluding monetary amounts (e.g., `$5000`).
- **Data Retrieval**: Fetches current prices and contract addresses from CoinGecko for detected tokens.
- **Output**: Generates a CSV file with columns:
  - Influencer
  - Token
  - CA (Contract Address)
  - Tweet Time
  - Price @Tweet, @5m, @10m, @15m (or @1h, @2h, @3h for >1 day)
  - % Change
- **Web Interface**: Simple form-based UI for easy access.

## Prerequisites

- Python 3.6+
- Dependencies: `tweepy`, `pandas`, `requests`, `flask`
- A Twitter API Bearer Token (free tier)
- Internet connection for API calls

## Setup

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd crypto-tweet-analyzer

2. **Install Dependencies:**
    ```bash
    pip install tweepy pandas requests flask

3. **Configure Twitter API:***
- Replace the bearer_token in app.py with your own Twitter API Bearer Token (obtained from the Twitter Developer Portal).

4. **Run the App:**
    ```bash
    python3 app.py

    - The app will start on http://localhost:5000.

## Usage
    1. Open your browser and navigate to http://localhost:5000.
    2. Enter a Twitter username (e.g., "elonmusk") and the number of days (1-7).
    3. Click "Analyze" to process the tweets.
    4. If successful, a CSV file (e.g., elonmusk_crypto_performance_7days.csv) will download automatically.
    5. If an error occurs (e.g., invalid user), an error message will display on the page.

## Example Output
    For a 1-day timeframe:

Influencer,Token,CA,Tweet Time,Price @Tweet,Price @5m,Price @10m,Price @15m,% Change
@elonmusk,$SOL,So111111111111111111111...,2025-03-19 10:00:00 UTC,150.0,150.0,150.0,150.0,0.0

## Limitations
    - Twitter API: Free tier limits to 500,000 tweets/month and 7-day history.
    - CoinGecko API: Free tier provides only current prices, not historical data, so price changes are static (0.0%).
    - Rate Limits: May pause for 15 minutes if Twitter API limits are hit.

## Deployment (Optional)

To host publicly:

- **Heroku**:
  1. Create a `Procfile`: `web: python app.py`
  2. Add `requirements.txt`: `tweepy pandas requests flask gunicorn`
  3. Deploy: `heroku create`, `git push heroku main`

- **Render**: Use their dashboard with `python app.py` as the start command.

## Contributing
Feel free to fork this project, submit issues, or send pull requests to enhance functionality (e.g., historical price tracking, better UI).

## License
This project is open-source under the MIT License.