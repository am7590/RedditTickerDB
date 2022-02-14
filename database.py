import json
import sqlite3
import requests
from requests.exceptions import HTTPError
import time


# Get engine, cursor from SQL database
def connect_to_db(db):
    engine = None
    cursor = None
    try:
        engine = sqlite3.connect(db)
        cursor = engine.cursor()
    except Exception as error:
        print(error)

    return [engine, cursor]


# Insert values into the database
def send_to_db(json_dict):
    # Grab values from json_dict
    post_time = json_dict["time_compiled"]
    post_type = str(json_dict["type"])
    posts = json_dict["posts"]
    content = str(*json_dict["content"])

    # Connect to SQLite DB
    [engine, cursor] = connect_to_db('TickerDb.db')

    # Insert values into database
    cursor.execute("INSERT INTO new_data VALUES(?,?,?,?)", (post_time, post_type, posts, content))
    engine.commit()
    engine.close()


def make_table():
    [engine, cursor] = connect_to_db('TickerDb.db')

    # Initially create SQL table
    cursor.execute('CREATE TABLE new_data(time TEXT, type TEXT, posts INTEGER, content TEXT)')
    engine.commit()
    engine.close()


def delete_table():
    [engine, cursor] = connect_to_db('TickerDb.db')
    cursor.execute('DROP TABLE new_data;')
    engine.close()


def reset_table():
    delete_table()
    make_table()


def grab_data():
    [engine, cursor] = connect_to_db('TickerDb.db')
    cursor.execute('SELECT * FROM new_data WHERE type="new"')  # Parse hot posts
    # cursor.execute('SELECT * FROM ticker_data WHERE type="new"')  # Parse new posts
    data = cursor.fetchall()
    engine.close()

    return data


# Get JSON api data from https://github.com/am7590/WSB-Ticker-API
def try_api(link):
    json_dict = ""
    try:
        # Scrape data on the hottest 50 posts
        response = requests.get(link)
        response.raise_for_status()

        # Retrieve JSON data
        json_response = response.json()
        # print(json_response)
        json_dict = json.loads(json.dumps(json_response))

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

    return json_dict


# Get time, ticker/frequency dict lists
def get_times_content_lists(new):
    [engine, cursor] = connect_to_db('TickerDb.db')

    if new:
        cursor.execute('SELECT time, content FROM new_data WHERE type="new"')
    else:
        cursor.execute('SELECT time, content FROM new_data WHERE type="hot"')
    times = []
    content = []

    for obj in cursor.fetchall():
        times.append((obj[0]))
        content.append((obj[1]))

    return [times, content]


# Runs an infinite loop that sends API data to the database every 5 mins
# Hot: try_api("https://flask-service.bg7bq3bnlj1de.us-east-1.cs.amazonlightsail.com/hot/?subreddit=wallstreetbets&hot=100")
# New: try_api("https://flask-service.bg7bq3bnlj1de.us-east-1.cs.amazonlightsail.com/new/?subreddit=pennystocks&new=100")
def run_5m_loop():
    count = 0
    while True:
        print("TickerDatabase has been updated " + str(count + 1) + " times:")
        # Read and send data from hot posts to DB
        hot_data = try_api('https://flask-service.bg7bq3bnlj1de.us-east-1.cs.amazonlightsail.com/hot/?subreddit=wallstreetbets&hot=100')
        send_to_db(hot_data)
        print("Hot posts scraped: " + str(hot_data))

        # Read and send data from new posts to DB
        new_data = try_api('https://flask-service.bg7bq3bnlj1de.us-east-1.cs.amazonlightsail.com/new/?subreddit=pennystocks&new=100')
        send_to_db(new_data)
        print("New posts scraped: " + str(new_data))

        print("\n")
        grab_data()
        print("\n")

        count += 1

        time.sleep(300)
