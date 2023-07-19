import unittest
from openap import polymer


flight = polymer.Flight("A320")

assert flight.fuel(distance=1000) == 2780
assert flight.fuel(distance=[1000]) == 2780
assert flight.fuel(distance=1000, mass=65000) == 2757
assert flight.fuel(distance=[1000], mass=[65000]) == 2757

unittest.TestCase().assertListEqual(
    list(flight.fuel(distance=[1000, 2000], mass=[65000, 70000])),
    [2757, 5661],
)

assert flight.co2(distance=1000) == 8784

unittest.TestCase().assertListEqual(
    list(flight.co2(distance=[1000, 2000], mass=[65000, 70000])),
    [8712, 17888],
)
