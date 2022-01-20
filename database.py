import json
import sqlite3
import requests
from requests.exceptions import HTTPError
import time
from datetime import datetime
import datetime


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
def send_to_db(json_dict, db):
    # Grab values from json_dict
    post_time = json_dict["time_compiled"]
    post_type = str(json_dict["type"])
    posts = json_dict["posts"]
    content = str(*json_dict["content"])

    # Connect to SQLite DB
    [engine, cursor] = connect_to_db('TickerDb.db')

    # Insert values into database
    cursor.execute("INSERT INTO " + db + " VALUES(?,?,?,?)", (post_time, post_type, posts, content))
    engine.commit()
    engine.close()


def make_table(db):
    [engine, cursor] = connect_to_db('TickerDb.db')

    # Initially create SQL table
    cursor.execute('CREATE TABLE IF NOT EXISTS ' + db + '(time TEXT, type TEXT, posts INTEGER, content TEXT)')
    engine.commit()
    engine.close()


def delete_table(db):
    [engine, cursor] = connect_to_db('TickerDb.db')
    cursor.execute('DROP TABLE ' + db + ';')
    engine.close()


def reset_table():
    delete_table(make_date_string())
    make_table()


def grab_data(db):
    [engine, cursor] = connect_to_db('TickerDb.db')
    # cursor.execute('SELECT * FROM ' + db + ' WHERE type="new"')  # Parse hot posts
    cursor.execute('SELECT * FROM ' + db + ' WHERE type="new"')  # Parse new posts

    # Fetch data
    data = cursor.fetchall()

    # Print data
    for row in cursor:
        print(row)

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
def get_times_content_lists(new, db):
    [engine, cursor] = connect_to_db('TickerDb.db')

    if new:
        cursor.execute('SELECT time, content FROM ' + db + ' WHERE type="new"')
    else:
        cursor.execute('SELECT time, content FROM ' + db + ' WHERE type="hot"')
    times = []
    content = []

    for obj in cursor.fetchall():
        times.append((obj[0]))
        content.append((obj[1]))

    return [times, content]


# Runs an infinite loop that sends API data to the database every 5 mins
def collect_data(interval, db):
    count = 0
    while True:
        # If it doesn't exist, make a new table
        make_table(db)

        print(db + " has been updated " + str(count + 1) + " times:")
        # Read and send data from hot posts to DB
        hot_data = try_api('https://flask-service.bg7bq3bnlj1de.us-east-1.cs.amazonlightsail.com/hot/?hot=100')
        send_to_db(hot_data, db)
        print("Hot posts scraped: " + str(hot_data))

        # Read and send data from new posts to DB
        new_data = try_api('https://flask-service.bg7bq3bnlj1de.us-east-1.cs.amazonlightsail.com/new/?new=100')
        send_to_db(new_data, db)
        print("New posts scraped: " + str(new_data))

        print("\n")
        grab_data(db)
        print("\n")

        count += 1

        time.sleep(interval)


# These functions are help create the db table names,
# which is the date written as a string with words
def letter_to_word(letter):
    letter_word_dict = {1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five',
                        6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine', 10: 'Ten',
                        11: 'Eleven', 12: 'Twelve', 13: 'Thirteen', 14: 'Fourteen',
                        15: 'Fifteen', 16: 'Sixteen', 17: 'Seventeen', 18: 'Eighteen',
                        19: 'Nineteen', 20: 'Twenty', 21: 'TwentyOne', 22: 'TwentyTwo',
                        23: 'TwentyThree', 24: 'TwentyFour', 25: 'TwentyFive', 26: 'TwentySix',
                        27: 'TwentySeven', 28: 'TwentyEight', 29: 'TwentyNine', 30: 'Thirty',
                        31: 'ThirtyOne', 32: 'ThirtyTwo', 40: 'Forty',
                        50: 'Fifty', 60: 'Sixty', 70: 'Seventy', 80: 'Eighty',
                        90: 'Ninety', 0: 'Zero'}

    try:
        return letter_word_dict[letter]
    except KeyError:
        try:
            print(letter_word_dict[letter - letter % 10] + letter_word_dict[letter % 10].lower())
        except KeyError:
            print('Error: Number out of range')


def make_date_string():
    date = datetime.datetime.now().strftime("%b %d %Y")
    month_day_year = date.split(" ")
    date_string = month_day_year[0] + letter_to_word(int(month_day_year[1])) \
                  + letter_to_word(int(month_day_year[2][:2])) \
                  + letter_to_word(int(month_day_year[2][2:]))

    return date_string
