# %%
import os
import click
import itertools
import warnings
from pathlib import Path
from tqdm import tqdm
import numpy as np
import openap
import pandas as pd
from openap import top
from multiprocessing import Pool
from multiprocessing import current_process


warnings.filterwarnings("ignore")


# %%
def generate_ac(ac, overwrite=True):
    dir = Path(__file__).resolve().parent.parent
    fout = f"{dir}/data/{ac}.csv"

    if not overwrite and os.path.exists(fout):
        return False

    wrap = openap.WRAP(ac, use_synonym=True)
    cruise_range = wrap.cruise_range()
    dmin, dmax = 200, cruise_range["maximum"]

    aircraft = openap.prop.aircraft(ac)
    m_oew = aircraft["limits"]["OEW"]
    m_mtow = aircraft["limits"]["MTOW"]
    mmin, mmax = (m_oew / m_mtow) * 1.2, 0.99

    engines = openap.prop.aircraft("A320")["engine"]["options"]

    if isinstance(engines, dict):
        engines = list(engines.values())

    results = []

    total_fuel = 0

    options = itertools.product(
        engines, np.linspace(mmin, mmax, 20), np.linspace(dmin, dmax, 10)
    )

    current = current_process()
    pos = current._identity[0] - 1

    with tqdm(total=200 * len(engines), ncols=0, position=pos, desc=f"{ac}") as pbar:
        for eng, m, d in options:
            pbar.update(1)
            start = (0, 0)
            end = (d / 110.574, 0)  # km -> deg

            optimizer = top.CompleteFlight(ac, start, end, m, use_synonym=True)
            optimizer.change_engine(eng)
            optimizer.setup_dc(nodes=30)
            # optimizer.debug = True

            flight = optimizer.trajectory(objective="fuel")

            if flight is None:
                total_fuel = 0
                continue

            total_fuel = flight.fuel.sum()  # kg
            total_time = flight.ts.iloc[-1] / 60  # minutes

            results.append(
                dict(
                    ac=ac,
                    eng=eng,
                    mass=int(round(m * m_mtow, -1)),
                    distance=int(d),
                    fuel=int(round(total_fuel, -1)),
                    time=int(round(total_time)),
                )
            )

    df = pd.DataFrame(results)
    df.to_csv(fout, index=False)
    return df


@click.command()
@click.option("--ac", required=True, help="aircraft type")
@click.option("--overwrite", default=False, help="aircraft type")
def main(ac, overwrite):
    ac = ac.lower()
    if ac == "all":
        all_acs = openap.prop.available_aircraft()

        with Pool(16) as pool:
            pool.map(generate_ac, all_acs)
    else:
        generate_ac(ac, overwrite)


# %%
if __name__ == "__main__":
    main()
