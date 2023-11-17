import matplotlib.pyplot as plt
import numpy as np

def performance():
    xaxis = np.array([1, 11])
    canny = []
    thresh = []
    hist = []

    plt.plot(xaxis, canny)
    plt.plot(xaxis, thresh)
    plt.plot(xaxis, hist)
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
