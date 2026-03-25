
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import config

def generate_timestamps(hours=48):
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    timestamps = [now - timedelta(hours=i) for i in range(hours, 0, -1)]
    return timestamps

def generate_solar(timestamps):
    solar = []
    for ts in timestamps:
        hour = ts.hour
        if 6 <= hour <= 19:
            peak = np.sin(np.pi * (hour - 6) / 13)
            noise = np.random.normal(0, 0.05)
            output = max(0, (peak + noise) * config.SOLAR_CAPACITY_KW)
        else:
            output = 0.0
        solar.append(round(output, 2))
    return solar

def generate_wind(timestamps):
    wind = []
    base_speed = np.random.uniform(5, 12)
    for ts in timestamps:
        speed = base_speed + np.random.normal(0, 1.5)
        speed = max(0, speed)
        if speed < 3:
            output = 0
        elif speed > 25:
            output = 0
        else:
            output = min(
                config.WIND_CAPACITY_KW,
                config.WIND_CAPACITY_KW * (speed / 12) ** 3
            )
        wind.append(round(output, 2))
    return wind

def generate_load(timestamps):
    load = []
    for ts in timestamps:
        hour = ts.hour
        if 6 <= hour <= 9:
            base = 600
        elif 10 <= hour <= 16:
            base = 450
        elif 17 <= hour <= 21:
            base = 750
        elif 22 <= hour <= 23:
            base = 400
        else:
            base = 300
        noise = np.random.normal(0, 30)
        load.append(round(max(200, base + noise), 2))
    return load

def generate_bess(timestamps, solar, load):
    bess_power = []
    soc = config.BESS_SOC_INITIAL
    soc_list = []
    for i, ts in enumerate(timestamps):
        net = solar[i] - load[i]
        if net > 0 and soc < config.BESS_SOC_MAX:
            charge = min(net, config.BESS_MAX_RATE_KW)
            soc += (charge * (1/60)) / config.BESS_CAPACITY_KWH
            soc = min(soc, config.BESS_SOC_MAX)
            bess_power.append(round(charge, 2))
        elif net < 0 and soc > config.BESS_SOC_MIN:
            discharge = min(abs(net), config.BESS_MAX_RATE_KW)
            soc -= (discharge * (1/60)) / config.BESS_CAPACITY_KWH
            soc = max(soc, config.BESS_SOC_MIN)
            bess_power.append(round(-discharge, 2))
        else:
            bess_power.append(0.0)
        soc_list.append(round(soc * 100, 1))
    return bess_power, soc_list

def generate_grid(solar, wind, load, bess):
    grid = []
    for i in range(len(load)):
        net = load[i] - solar[i] - wind[i] - bess[i]
        grid.append(round(net, 2))
    return grid

import streamlit as st

@st.cache_data(ttl=30)
def get_der_dataframe(hours=48):
    
    timestamps = generate_timestamps(hours)
    solar = generate_solar(timestamps)
    wind = generate_wind(timestamps)
    load = generate_load(timestamps)
    bess, soc = generate_bess(timestamps, solar, load)
    grid = generate_grid(solar, wind, load, bess)
    df = pd.DataFrame({
        'timestamp': timestamps,
        'solar_kw': solar,
        'wind_kw': wind,
        'load_kw': load,
        'bess_kw': bess,
        'bess_soc_pct': soc,
        'grid_kw': grid
    })
    return df
