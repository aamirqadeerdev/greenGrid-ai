

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


# Five simulated DER sites across Canada
SITES = [
    {
        "id": 1,
        "name": "Oakville Solar Farm",
        "location": "Oakville, Ontario",
        "lat": 43.4675,
        "lon": -79.6877,
        "solar_kw": 800,
        "wind_kw": 0,
        "bess_kwh": 400,
        "bess_kw": 200,
        "ev_kw": 50,
        "grid_operator": "IESO"
    },
    {
        "id": 2,
        "name": "Kingston Wind Farm",
        "location": "Kingston, Ontario",
        "lat": 44.2312,
        "lon": -76.4860,
        "solar_kw": 200,
        "wind_kw": 500,
        "bess_kwh": 300,
        "bess_kw": 150,
        "ev_kw": 30,
        "grid_operator": "IESO"
    },
    {
        "id": 3,
        "name": "Calgary Solar Storage",
        "location": "Calgary, Alberta",
        "lat": 51.0447,
        "lon": -114.0719,
        "solar_kw": 600,
        "wind_kw": 200,
        "bess_kwh": 500,
        "bess_kw": 250,
        "ev_kw": 80,
        "grid_operator": "AESO"
    },
    {
        "id": 4,
        "name": "Guelph Community Energy",
        "location": "Guelph, Ontario",
        "lat": 43.5448,
        "lon": -80.2482,
        "solar_kw": 400,
        "wind_kw": 100,
        "bess_kwh": 200,
        "bess_kw": 100,
        "ev_kw": 40,
        "grid_operator": "IESO"
    },
    {
        "id": 5,
        "name": "Edmonton Wind Solar",
        "location": "Edmonton, Alberta",
        "lat": 53.5461,
        "lon": -113.4938,
        "solar_kw": 300,
        "wind_kw": 400,
        "bess_kwh": 350,
        "bess_kw": 175,
        "ev_kw": 60,
        "grid_operator": "AESO"
    }
]


def get_site_status():
    statuses = []
    for site in SITES:
        hour = datetime.now().hour
        if 6 <= hour <= 19:
            solar_output = site["solar_kw"] * np.random.uniform(0.3, 0.9)
        else:
            solar_output = 0

        wind_output = site["wind_kw"] * np.random.uniform(0.2, 0.8)
        bess_soc = np.random.uniform(30, 85)
        load = np.random.uniform(200, 600)
        status = np.random.choice(
            ["Online", "Online", "Online", "Warning"],
            p=[0.7, 0.15, 0.1, 0.05]
        )

        statuses.append({
            "id": site["id"],
            "name": site["name"],
            "location": site["location"],
            "lat": site["lat"],
            "lon": site["lon"],
            "solar_kw": round(solar_output, 1),
            "wind_kw": round(wind_output, 1),
            "bess_soc_pct": round(bess_soc, 1),
            "load_kw": round(load, 1),
            "grid_operator": site["grid_operator"],
            "status": status,
            "solar_capacity": site["solar_kw"],
            "wind_capacity": site["wind_kw"],
            "bess_capacity_kwh": site["bess_kwh"],
            "bess_kw": site["bess_kw"]
        })

    return statuses


def get_vpp_aggregation(site_statuses):
    total_solar = sum(s["solar_kw"] for s in site_statuses)
    total_wind = sum(s["wind_kw"] for s in site_statuses)
    total_solar_capacity = sum(s["solar_capacity"] for s in site_statuses)
    total_wind_capacity = sum(s["wind_capacity"] for s in site_statuses)
    total_bess_kwh = sum(s["bess_capacity_kwh"] for s in site_statuses)
    total_bess_kw = sum(s["bess_kw"] for s in site_statuses)
    total_load = sum(s["load_kw"] for s in site_statuses)
    avg_bess_soc = sum(s["bess_soc_pct"] for s in site_statuses) / len(site_statuses)

    dispatchable_kw = total_bess_kw * (avg_bess_soc / 100)
    available_capacity = total_solar + total_wind + dispatchable_kw

    ieso_sites = [s for s in site_statuses if s["grid_operator"] == "IESO"]
    aeso_sites = [s for s in site_statuses if s["grid_operator"] == "AESO"]

    return {
        "total_solar_kw": round(total_solar, 1),
        "total_wind_kw": round(total_wind, 1),
        "total_solar_capacity_kw": total_solar_capacity,
        "total_wind_capacity_kw": total_wind_capacity,
        "total_bess_kwh": total_bess_kwh,
        "total_bess_kw": total_bess_kw,
        "total_load_kw": round(total_load, 1),
        "avg_bess_soc_pct": round(avg_bess_soc, 1),
        "dispatchable_kw": round(dispatchable_kw, 1),
        "available_capacity_kw": round(available_capacity, 1),
        "total_sites": len(site_statuses),
        "ieso_sites": len(ieso_sites),
        "aeso_sites": len(aeso_sites),
        "online_sites": len([s for s in site_statuses
                             if s["status"] == "Online"])
    }


def get_market_data():
    hour = datetime.now().hour
    if 7 <= hour <= 11 or 17 <= hour <= 19:
        ieso_price = config.ONTARIO_ON_PEAK * 1000
    elif 11 <= hour <= 17:
        ieso_price = config.ONTARIO_MID_PEAK * 1000
    else:
        ieso_price = config.ONTARIO_OFF_PEAK * 1000

    aeso_price = np.random.uniform(50, 120)

    next_peak = None
    if hour < 7:
        next_peak = "07:00"
    elif hour < 17:
        next_peak = "17:00"
    else:
        next_peak = "07:00 tomorrow"

    return {
        "ieso_price_mwh": round(ieso_price, 2),
        "aeso_price_mwh": round(aeso_price, 2),
        "next_peak_window": next_peak,
        "dr_program_active": True,
        "market_status": "Open"
    }


def get_revenue_data():
    daily_energy_revenue = np.random.uniform(800, 1500)
    daily_dr_revenue = np.random.uniform(200, 600)
    daily_ancillary_revenue = np.random.uniform(100, 300)
    daily_total = daily_energy_revenue + daily_dr_revenue + daily_ancillary_revenue

    return {
        "daily_energy_cad": round(daily_energy_revenue, 2),
        "daily_dr_cad": round(daily_dr_revenue, 2),
        "daily_ancillary_cad": round(daily_ancillary_revenue, 2),
        "daily_total_cad": round(daily_total, 2),
        "monthly_total_cad": round(daily_total * 30, 2),
        "annual_total_cad": round(daily_total * 365, 2)
    }


def get_bid_recommendation(vpp_data, market_data):
    dispatchable = vpp_data["dispatchable_kw"]
    price = market_data["ieso_price_mwh"]

    if price >= config.ONTARIO_ON_PEAK * 1000:
        bid_quantity = dispatchable * 0.8
        recommendation = "HIGH PRICE — Submit maximum bid now"
        urgency = "HIGH"
    elif price >= config.ONTARIO_MID_PEAK * 1000:
        bid_quantity = dispatchable * 0.5
        recommendation = "MID PRICE — Submit partial bid"
        urgency = "MEDIUM"
    else:
        bid_quantity = 0
        recommendation = "LOW PRICE — Hold capacity for peak hours"
        urgency = "LOW"

    expected_revenue = (bid_quantity / 1000) * price

    return {
        "bid_quantity_kw": round(bid_quantity, 1),
        "recommendation": recommendation,
        "urgency": urgency,
        "expected_revenue_cad": round(expected_revenue, 2),
        "price_mwh": price
    }

