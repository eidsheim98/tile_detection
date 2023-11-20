import matplotlib.pyplot as plt
import numpy as np

class Statistic():
    """
    The statistic class
    """
    def __init__(self, name, data):
        self.name = name
        self.data = data

def load_csv(filename):
    """
    Loads the csv file and converts it to a dict
    :param filename: The relative filepath of the file from the statistics/ directory
    :return: The dictionary containing the data
    """
    with open(f"data/{filename}", "r") as file:
        lines = file.readlines()
        lines = [line.replace("\n","") for line in lines]
        data = [line.split(",") for line in lines]
        statistics = {d[0]: list(map(float, d[1:])) for d in data}
    return statistics


def barchart():
    """
    Produces a statistical bar chart
    """
    thresh_data = load_csv("performance/thresh.csv")
    hist_data = load_csv("performance/hist.csv")
    canny_data = load_csv("performance/canny.csv")

    xaxis = thresh_data["Iteration"]
    thresh = thresh_data["Found / expected"]
    hist = hist_data["Found / expected"]
    canny = canny_data["Found / expected"]

    # Create a single subplot
    fig, ax = plt.subplots(figsize=(12, 6))

    # Set the width of the bars
    bar_width = 0.2

    x = np.arange(len(xaxis))

    # Plot all three datasets with adjusted x-axis positions
    ax.bar(x - bar_width, thresh, width=bar_width, alpha=0.7, color='b', label='Thresh')
    ax.bar(x, hist, width=bar_width, color='g', alpha=0.7, label='Histogram')
    ax.bar(x + bar_width, canny, width=bar_width, alpha=0.7,  color='r', label='Canny')

    # Add legend and labels
    ax.legend(bbox_to_anchor =(1.12, 1.15), ncol = 1)

    # Add average lines
    ax.axhline(np.mean(thresh), color='blue', linestyle='dashed', linewidth=2, label='Thresh Avg')
    ax.axhline(np.mean(hist), color='green', linestyle='dashed', linewidth=2, label='Histogram Avg')
    ax.axhline(np.mean(canny), color='red', linestyle='dashed', linewidth=2, label='Canny Avg')

    ax.set_xlabel('Iteration')
    ax.set_ylabel('Cracks found / expected')
    ax.set_title('Performance of the detectors over 12 iterations')

    y_pos = np.arange(len(xaxis))
    plt.xticks(y_pos, [str(int(x)) for x in xaxis])
    plt.savefig("plots/barchart.png")
    plt.show()


def lighting():
    """
    Produces a histogram containing our performance data in different lighting
    """
    thresh_data = load_csv("lighting/thresh.csv")
    hist_data = load_csv("lighting/hist.csv")
    canny_data = load_csv("lighting/canny.csv")

    lux = thresh_data["Lux"]
    thresh_fe = thresh_data["Found / expected"]
    hist_fe = hist_data["Found / expected"]
    canny_fe = canny_data["Found / expected"]

    thresh_bad = thresh_data["Bad"]
    hist_bad = hist_data["Bad"]
    canny_bad = canny_data["Bad"]

    # Set a wider figure size
    fig, axes = plt.subplots(2, 1, figsize=(12, 12), sharex=False)

    # Set the width of the bars
    bar_width = 0.2
    x = np.arange(len(lux))

    # Plot all three datasets with adjusted x-axis positions
    axes[0].bar(x - bar_width, thresh_fe, width=bar_width, alpha=0.7, color='b', label='Thresh')
    axes[0].bar(x, hist_fe, width=bar_width, color='g', alpha=0.7, label='Histogram',
                tick_label=[str(int(x)) for x in lux])
    axes[0].bar(x + bar_width, canny_fe, width=bar_width, alpha=0.7, color='r', label='Canny')

    # First subplot
    axes[0].legend()
    axes[0].set_xlabel('Lux')
    axes[0].set_ylabel('Found / Expected')
    axes[0].set_title('Rate of found cracks vs expected finds in different lighting')

    # Plot all three datasets with adjusted x-axis positions
    axes[1].bar(x - bar_width, thresh_bad, width=bar_width, alpha=0.7, color='b', label='Thresh')
    axes[1].bar(x, hist_bad, width=bar_width, color='g', alpha=0.7, label='Histogram',
                tick_label=[str(int(x)) for x in lux])
    axes[1].bar(x + bar_width, canny_bad, width=bar_width, alpha=0.7, color='r', label='Canny')

    # Second subplot
    axes[1].legend()
    axes[1].set_xlabel('Lux')
    axes[1].set_ylabel('Found cracks that are not there')
    axes[1].set_title('Found cracks that are not there in different lighting')

    plt.tight_layout()
    plt.savefig("plots/lighting.png")
    plt.show()


if __name__ == '__main__':
    lighting()
    barchart()