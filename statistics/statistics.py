import matplotlib.pyplot as plt
import numpy as np

class Statistic():
    def __init__(self, name, data):
        self.name = name
        self.data = data

def load_csv(filename):
    with open(f"data/{filename}", "r") as file:
        lines = file.readlines()
        lines = [line.replace("\n","") for line in lines]
        data = [line.split(",") for line in lines]
        statistics = {d[0]: list(map(float, d[1:])) for d in data}
    return statistics


def barchart():
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

    # First subplot
    axes[0].plot(lux, thresh_fe, label="Thresh")
    axes[0].plot(lux, hist_fe, label="Histogram")
    axes[0].plot(lux, canny_fe, label="Canny")
    axes[0].legend()
    axes[0].set_xlabel('Lux')
    axes[0].set_ylabel('Found / Expected')
    axes[0].set_title('Rate of found cracks vs expected finds in different lighting')

    # Second subplot
    axes[1].plot(lux, thresh_bad, label="Thresh")
    axes[1].plot(lux, hist_bad, label="Histogram")
    axes[1].plot(lux, canny_bad, label="Canny")
    axes[1].legend()
    axes[1].set_xlabel('Lux')
    axes[1].set_ylabel('Bad cracks')
    axes[1].set_title('Bad cracks found in different lighting')

    plt.tight_layout()
    plt.savefig("plots/lighting.png")
    plt.show()


if __name__ == '__main__':
    lighting()
    barchart()