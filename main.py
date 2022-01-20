# Local files
from database import *
from ticker import *

# Graphing libraries
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import style

# Set style for matplotlib
style.use('fivethirtyeight')


# Parse extra characters and convert DB data from strings to lists
def make_item_list(item):
    item_list = str(item).split("'")
    item_list = item_list[1::2]

    freq_list = str(item).split("'")
    for i in range(0, len(freq_list), 1):
        if freq_list[i].strip(":, {}").isnumeric():
            freq_list[i] = int(freq_list[i].strip(":, }"))

    return [item_list, freq_list[2::2]]


# Good tutorial: https://www.youtube.com/watch?v=pq4nwICEB4U
def graph_data(new, ticker):
    # Get ordered lists for times (dates), content (ticker dict)
    times, content = get_times_content_lists(new)

    class_list = []
    iterator = 0

    # Create ticker objects for every data point we want to graph
    for item in content:
        [item_list, freq_list] = make_item_list(item)

        # Parse data that doesn't match with input ticker
        for i in range(0, len(item_list), 1):
            if item_list[i] == ticker:
                class_list.append(tickerClass(times[iterator], item_list[i], freq_list[i]))

        iterator += 1

    # Iterate through all data
    # Select frequency, time for ticker
    graph_time, graph_freq = [], []
    for i in class_list:
        graph_freq.append(i.freq)
        graph_time.append(i.date)

    # Plot on graphs using matplotlib.pyplot
    plt.plot_date(graph_time, graph_freq, "-")
    plt.show()


# Grab and print data_list
def print_data_list():
    data_list = grab_data()
    for item in data_list:
        print(item)


if __name__ == '__main__':
    # print_data_list()

    graph_data(True, "GME")  # Graph all data from new posts
    graph_data(False, "GME")  # Graph all data from hot posts

