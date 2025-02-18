# /// script
# dependencies = [
#   "matplotlib",
#   "mod",
# ]
# ///

from typing import Generator
import matplotlib
import matplotlib.pyplot as plt
from mod import Mod

matplotlib.use("TkAgg")


def lcg(m: int, a: int, c: int, x_0: int) -> Generator[int]:
    x_n = Mod(x_0, m)
    while True:
        x_n = a * x_n + c
        yield int(x_n)


def lcg_real(m: int, a: float, c: float, x_0: float) -> Generator[float]:
    x_n = Mod(x_0, m)
    while True:
        x_n = a * x_n + c
        yield x_n / m


if __name__ == "__main__":
    m = 2**15
    a = 11 * 17 * 71
    c = 11

    seed = 10

    num_points = 2**15
    lcg_gen = lcg(m, a, c, seed)
    values = [next(lcg_gen) for _ in range(num_points)]

    x_values = values[:-1]
    y_values = values[1:]

    plot = plt.subplots()

    plt.scatter(x_values, y_values, s=1)
    plt.title("Scatter plot of LCG generated numbers")
    plt.xlabel("X values")
    plt.ylabel("Y values")
    plt.show()
