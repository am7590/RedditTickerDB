# This class holds data for every individual ticker/frequency/time that needs to be plotted
class tickerClass:
    def __init__(self, date, ticker, freq):
        self.date = date
        self.ticker = ticker
        self.freq = freq

    def print_ticker(self):
        print(self.ticker + " " + str(self.freq) + " " + self.date)
