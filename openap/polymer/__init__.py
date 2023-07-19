# %%
from collections.abc import Iterable
import openap
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

current_path = os.path.dirname(os.path.realpath(__file__))


# %%
class Flight:
    def __init__(self, ac, degree=2):
        self.degree = degree
        self.ac = ac
        self.data = pd.read_csv(f"{current_path}/data/{self.ac.lower()}.csv")
        self.model = make_pipeline(PolynomialFeatures(degree), LinearRegression())

        X_train = self.data[["mass", "distance"]]
        y_train = self.data[["fuel"]]

        self.model.fit(X_train, y_train)
        self.data = self.data.assign(predict=self.model.predict(X_train))

    def fuel(self, distance, mass=None):
        if not isinstance(distance, Iterable):
            distance = [distance]

        if mass is None:
            print("warning: mass not specified, using 85% of maximum weight")
            mass = openap.prop.aircraft("a320")["limits"]["MTOW"] * 0.85

        if not isinstance(mass, Iterable):
            mass = [mass] * len(distance)

        assert len(mass) == len(distance)

        X_pred = pd.DataFrame.from_dict(dict(mass=mass, distance=distance))
        fuel = self.model.predict(X_pred)

        if fuel.shape[0] == 1:
            fuel = fuel[0][0]

        return fuel.flatten().astype(int)

    def co2(self, distance, mass=None):
        co2 = self.fuel(distance, mass) * 3.16
        return co2.astype(int)

    def plot(self):
        import seaborn as sns

        sns.lineplot(data=self.data, x="distance", y="predict", hue="mass")
        plt.xlabel("Distance (km)")
        plt.ylabel("Fuel (kg)")
        plt.legend(title="mass (kg)")
        plt.show()
