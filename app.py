#!/usr/bin/python3
import tweepy
import pandas as pd
import requests
from datetime import datetime, timedelta, timezone
import re
import time
from flask import Flask, request, render_template, send_file, redirect, url_for

# Initialize Flask app
app = Flask(__name__)

# Twitter API authentication
import os
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")  # Secure Token privacy using env variable
client = tweepy.Client(bearer_token=bearer_token)

# Fetch the list of cryptocurrencies from CoinGecko
response = requests.get("https://api.coingecko.com/api/v3/coins/list")
coins = response.json()

# Create a dictionary with symbols and full names
crypto_data = {}
for coin in coins:
    symbol = coin["symbol"].lower()
    name = coin["name"].lower()
    if symbol not in crypto_data:  # Avoid duplicates by using the first occurrence
        crypto_data[symbol] = {"id": coin["id"], "name": name}

# Compile regex patterns for each cryptocurrency
crypto_patterns = {}
for symbol, info in crypto_data.items():
    patterns = [
        rf'\${re.escape(symbol)}\b(?![0-9])'  # e.g., $btc, but not $5000
    ]
    if re.match(r'^[a-z]+$', symbol):  # Only include alphabetic symbols
        crypto_patterns[symbol] = re.compile('|'.join(patterns), re.IGNORECASE)

# Function to detect cryptocurrency mentions in tweet text
def find_crypto_mentions(tweet_text):
    tweet_lower = tweet_text.lower()
    mentions = set()
    for symbol, pattern in crypto_patterns.items():
        if pattern.search(tweet_lower):
            if symbol in crypto_data:
                mentions.add(symbol)
    return list(mentions)

# Function to fetch price data and contract addresses
def fetch_price_data(coin_ids):
    if not coin_ids:
        return {}
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(coin_ids)}"
    response = requests.get(url)
    if response.status_code == 200:
        filtered_coins = [
            coin for coin in response.json()
            if 'market_cap' in coin and coin['market_cap'] is not None
            and 2000000 <= coin['market_cap'] <= 2000000000
        ]
        coin_info = {}
        for coin in filtered_coins:
            ca = None
            if 'platforms' in coin and coin['platforms']:
                ca = (coin['platforms'].get('solana') or
                      coin['platforms'].get('ethereum') or
                      next(iter(coin['platforms'].values()), None))
            coin_info[coin["id"]] = {
                "current_price": coin["current_price"],
                "contract_address": ca if ca else "N/A"
            }
        return coin_info
    return {}

# Core analysis function
def analyze_influencer(influencer, days):
    try:
        user = client.get_user(username=influencer)
        user_id = user.data.id
    except Exception as e:
        return f"Error fetching user: {e}", None

    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    since_time = current_time - timedelta(days=days)

    all_tweets = []
    pagination_token = None
    max_requests = 3
    for i in range(max_requests):
        try:
            tweets = client.get_users_tweets(
                id=user_id,
                max_results=25,
                tweet_fields=["created_at"],
                start_time=since_time,
                pagination_token=pagination_token
            )
            if tweets.data:
                all_tweets.extend(tweets.data)
            pagination_token = tweets.meta.get("next_token")
            if not pagination_token:
                break
            time.sleep(1)
        except tweepy.TooManyRequests:
            time.sleep(900)
        except Exception as e:
            return f"Error fetching tweets: {e}", None

    if days <= 1:
        processable_tweets = [tweet for tweet in all_tweets if tweet.created_at + timedelta(minutes=15) < current_time]
    else:
        processable_tweets = [tweet for tweet in all_tweets if tweet.created_at + timedelta(hours=3) < current_time]

    unique_mentions = set()
    for tweet in processable_tweets:
        mentions = find_crypto_mentions(tweet.text)
        unique_mentions.update(mentions)

    unique_coin_ids = [crypto_data[mention]["id"] for mention in unique_mentions]
    price_data = fetch_price_data(unique_coin_ids)

    data = []
    for tweet in processable_tweets:
        tweet_time = tweet.created_at
        tweet_text = tweet.text
        mentions = find_crypto_mentions(tweet_text)
        for mention in mentions:
            coin_id = crypto_data[mention]["id"]
            coin_info = price_data.get(coin_id, None)
            if coin_info is None:
                continue
            price_at_tweet = coin_info["current_price"]
            contract_address = coin_info["contract_address"]
            if days <= 1:
                price_at_5m = price_at_tweet
                price_at_10m = price_at_tweet
                price_at_15m = price_at_tweet
                percent_change = 0.0
                data.append({
                    "Influencer": f"@{influencer}",
                    "Token": f"${mention.upper()}",
                    "CA": contract_address,
                    "Tweet Time": tweet_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "Price @Tweet": price_at_tweet,
                    "Price @5m": price_at_5m,
                    "Price @10m": price_at_10m,
                    "Price @15m": price_at_15m,
                    "% Change": percent_change
                })
            else:
                price_at_1h = price_at_tweet
                price_at_2h = price_at_tweet
                price_at_3h = price_at_tweet
                percent_change = 0.0
                data.append({
                    "Influencer": f"@{influencer}",
                    "Token": f"${mention.upper()}",
                    "CA": contract_address,
                    "Tweet Time": tweet_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "Price @Tweet": price_at_tweet,
                    "Price @1h": price_at_1h,
                    "Price @2h": price_at_2h,
                    "Price @3h": price_at_3h,
                    "% Change": percent_change
                })

    if data:
        df = pd.DataFrame(data)
        filename = f"{influencer}_crypto_performance_{days}days.csv"
        df.to_csv(filename, index=False)
        return None, filename
    return "No data found.", None

# Flask routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        influencer = request.form['influencer'].strip()
        days = int(request.form['days'])
        if days > 7:
            days = 7
        elif days < 1:
            days = 1

        error, filename = analyze_influencer(influencer, days)
        if error:
            return render_template('index.html', error=error)
        return redirect(url_for('download', filename=filename))
    return render_template('index.html', error=None)

@app.route('/download/<filename>')
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True, host='0.0.0.0', port=5000)

