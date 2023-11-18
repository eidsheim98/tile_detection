import matplotlib.pyplot as plt
import numpy as np

class Statistic():
    def __init__(self, name, data):
        self.name = name
        self.data = data

def load_csv(filename):
    with open(f"data/{filename}", "r") as file:
        lines = file.readlines()
        data = [line.split(",") for line in lines]
        statistics = {d[0]: list(map(float, d[1:-1])) for d in data}
    return statistics

def performance():
    thresh_data = load_csv("thresh.csv")
    hist_data = load_csv("hist.csv")
    canny_data = load_csv("canny.csv")

    xaxis = list(range(1, 11))
    thresh = thresh_data["Found / expected"]
    hist = hist_data["Found / expected"]
    canny = canny_data["Found / expected"]

    thresh_c = [sum(thresh[:i + 1]) for i in range(len(thresh))]
    hist_c = [sum(hist[:i + 1]) for i in range(len(hist))]
    canny_c = [sum(canny[:i + 1]) for i in range(len(canny))]


    plt.plot(xaxis, thresh_c)
    plt.plot(xaxis, hist_c)
    plt.plot(xaxis, canny_c)
    plt.show()


def lighting():
    xaxis = [0, 15, 50, 120, 300, 730]

    canny = [3, 3, 4, 4, 5, 6]
    thresh = [4, 4, 5, 6, 6, 6]

    plt.plot(xaxis, canny)
    plt.plot(xaxis, thresh)
    plt.show()

if __name__ == '__main__':
    lighting()
