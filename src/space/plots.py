import matplotlib.pyplot as plt

from space.models import Asteroid


def asteroids_plot(asteroids: list[Asteroid], filepath):
    plt.title("Asteroids")
    plt.xlabel("X - distance (million km)")
    plt.ylabel("Y - diameter (km)")

    for asteroid in asteroids:
        diameter = (
            asteroid.estimated_diameter.kilometers.estimated_diameter_max
            + asteroid.estimated_diameter.kilometers.estimated_diameter_min
        ) / 2
        diameter = round(diameter, 2)
        distance = round(
            asteroid.close_approach_data[0].miss_distance.kilometers / 10**6, 2
        )
        is_hazardous = asteroid.is_potentially_hazardous_asteroid

        if is_hazardous:
            plt.scatter(distance, diameter, c="red")
        else:
            plt.scatter(distance, diameter, c="blue")

    plt.savefig(filepath)
