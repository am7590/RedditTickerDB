import json
import sqlite3
import requests
from requests.exceptions import HTTPError
import time

# Graphing libraries
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import style

style.use('fivethirtyeight')


class tickerClass:
    def __init__(self, date, ticker, freq):
        self.date = date
        self.ticker = ticker
        self.freq = freq

    def date_freq(self):
        return [self.date, self.freq]


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


def connect_to_db(db):
    engine = None
    cursor = None
    try:
        engine = sqlite3.connect(db)
        cursor = engine.cursor()
    except Exception as error:
        print(error)

    return [engine, cursor]


def send_to_db(json_dict):
    # Grab values from json_dict
    post_time = json_dict["time_compiled"]
    post_type = str(json_dict["type"])
    posts = json_dict["posts"]
    content = str(*json_dict["content"])

    # Convert to dataframe
    # df = pd.DataFrame(json_dict)

    # Connect to SQLite DB
    [engine, cursor] = connect_to_db('TickerDb.db')

    # Insert values into database
    cursor.execute("INSERT INTO ticker_data VALUES(?,?,?,?)", (post_time, post_type, posts, content))
    engine.commit()
    engine.close()


def make_table():
    [engine, cursor] = connect_to_db('TickerDb.db')

    # Initially create SQL table
    cursor.execute('CREATE TABLE ticker_data(time TEXT, type TEXT, posts INTEGER, content TEXT)')
    engine.commit()
    engine.close()


def grab_data():
    [engine, cursor] = connect_to_db('TickerDb.db')
    cursor.execute('SELECT * FROM ticker_data WHERE type="new"')  # Parse hot posts
    # cursor.execute('SELECT * FROM ticker_data WHERE type="new"')  # Parse new posts
    data = cursor.fetchall()
    engine.close()

    return data


def delete_table():
    [engine, cursor] = connect_to_db('TickerDb.db')
    cursor.execute('DROP TABLE ticker_data;')
    engine.close()


def reset_table():
    delete_table()
    make_table()


def run_5m_loop():
    count = 0
    while True:
        print("TickerDatabase has been updated " + str(count + 1) + " times:")
        # Read and send data from hot posts to DB
        hot_data = try_api('https://flask-service.bg7bq3bnlj1de.us-east-1.cs.amazonlightsail.com/hot/?hot=100')
        send_to_db(hot_data)
        print("Hot posts scraped: " + str(hot_data))

        # Read and send data from new posts to DB
        new_data = try_api('https://flask-service.bg7bq3bnlj1de.us-east-1.cs.amazonlightsail.com/new/?new=100')
        send_to_db(new_data)
        print("New posts scraped: " + str(new_data))

        print("\n")
        grab_data()
        print("\n")

        count += 1

        time.sleep(300)


# Good tutorial: https://www.youtube.com/watch?v=pq4nwICEB4U
def graph_data(new, ticker):
    [engine, cursor] = connect_to_db('TickerDb.db')

    if new:
        cursor.execute('SELECT time, content FROM ticker_data WHERE type="new"')
    else:
        cursor.execute('SELECT time, content FROM ticker_data WHERE type="hot"')
    times = []
    content = []

    # count = 0
    for obj in cursor.fetchall():
        # if count < 50:
        values = obj[1]
        times.append((obj[0]))
        content.append((obj[1]))
        # count += 1

    # print(times)
    # print(content)

    class_list = []
    item_list, freq_list = [], []
    iter = 0
    for item in content:
        item_list = str(item).split("'")
        item_list = item_list[1::2]

        freq_list = str(item).split("'")
        for i in range(0, len(freq_list), 1):
            if freq_list[i].strip(":, {}").isnumeric():
                freq_list[i] = int(freq_list[i].strip(":, }"))
        freq_list = freq_list[2::2]

        for i in range(0, len(item_list), 1):
            if item_list[i] == ticker:
                class_list.append(tickerClass(times[iter], item_list[i], freq_list[i]))

        # print(item_list)
        # print(freq_list)

        iter += 1

        # Iterate through all data
        # Select frequency, time for ticker

    graph_time, graph_freq = [], []
    for i in class_list:
        graph_freq.append(i.freq)
        graph_time.append(i.date)

    plt.plot_date(graph_time, graph_freq, "-")
    plt.show()


if __name__ == '__main__':
    # Grab and print data
    # data_list = grab_data()
    # for item in data_list:
    #     print(item)

    graph_data(True, "GME")  # New posts
    graph_data(False, "GME")  # Hot posts
