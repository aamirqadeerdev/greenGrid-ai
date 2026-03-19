
import pandas as pd
import numpy as np
from pulp import (
    LpProblem, LpMinimize, LpVariable,
    lpSum, LpStatus, value
)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def get_ontario_prices(hours=24):
    prices = []
    for hour in range(hours):
        h = hour % 24
        if 7 <= h <= 11 or 17 <= h <= 19:
            prices.append(config.ONTARIO_ON_PEAK)
        elif 11 <= h <= 17:
            prices.append(config.ONTARIO_MID_PEAK)
        else:
            prices.append(config.ONTARIO_OFF_PEAK)
    return prices


def optimize_bess_schedule(
    load_forecast,
    solar_forecast,
    wind_forecast,
    hours=24
):
    prices = get_ontario_prices(hours)

    prob = LpProblem("BESS_Optimization", LpMinimize)

    charge = [LpVariable(f"charge_{h}", 0, config.BESS_MAX_RATE_KW)
              for h in range(hours)]
    discharge = [LpVariable(f"discharge_{h}", 0, config.BESS_MAX_RATE_KW)
                 for h in range(hours)]
    grid_import = [LpVariable(f"grid_{h}", 0, config.GRID_LIMIT_KW)
                   for h in range(hours)]
    soc = [LpVariable(f"soc_{h}",
                      config.BESS_SOC_MIN * config.BESS_CAPACITY_KWH,
                      config.BESS_SOC_MAX * config.BESS_CAPACITY_KWH)
           for h in range(hours)]

    prob += lpSum([grid_import[h] * prices[h] for h in range(hours)])

    prob += soc[0] == config.BESS_SOC_INITIAL * config.BESS_CAPACITY_KWH

    for h in range(hours):
        solar = solar_forecast[h] if h < len(solar_forecast) else 0
        wind = wind_forecast[h] if h < len(wind_forecast) else 0
        load = load_forecast[h] if h < len(load_forecast) else 500

        prob += (grid_import[h] + solar + wind + discharge[h] ==
                 load + charge[h])

        if h > 0:
            prob += (soc[h] == soc[h-1] +
                     charge[h-1] * config.BESS_EFFICIENCY -
                     discharge[h-1] / config.BESS_EFFICIENCY)

    prob.solve()

    results = {
        "status": LpStatus[prob.status],
        "hours": list(range(hours)),
        "charge_kw": [max(0, value(charge[h])) for h in range(hours)],
        "discharge_kw": [max(0, value(discharge[h])) for h in range(hours)],
        "grid_import_kw": [max(0, value(grid_import[h])) for h in range(hours)],
        "soc_kwh": [max(0, value(soc[h])) for h in range(hours)],
        "soc_pct": [max(0, value(soc[h])) / config.BESS_CAPACITY_KWH * 100
                    for h in range(hours)],
        "prices": prices,
        "load": load_forecast[:hours],
        "solar": solar_forecast[:hours],
        "wind": wind_forecast[:hours]
    }

    total_cost = sum(results["grid_import_kw"][h] * prices[h]
                     for h in range(hours))
    baseline_cost = sum(load_forecast[h] * prices[h]
                        for h in range(hours))
    results["total_cost_cad"] = round(total_cost, 2)
    results["baseline_cost_cad"] = round(baseline_cost, 2)
    results["cost_saving_cad"] = round(baseline_cost - total_cost, 2)
    results["saving_pct"] = round(
        (baseline_cost - total_cost) / baseline_cost * 100, 1
    ) if baseline_cost > 0 else 0

    return results


def optimize_ev_charging(
    departure_hour=8,
    target_soc_pct=90,
    current_soc_pct=20,
    ev_capacity_kwh=60,
    max_charge_rate_kw=11,
    hours=12
):
    prices = get_ontario_prices(hours)
    energy_needed = (target_soc_pct - current_soc_pct) / 100 * ev_capacity_kwh

    prob = LpProblem("EV_Charging", LpMinimize)

    charge = [LpVariable(f"ev_charge_{h}", 0, max_charge_rate_kw)
              for h in range(hours)]

    prob += lpSum([charge[h] * prices[h] for h in range(hours)])

    prob += lpSum(charge) >= energy_needed

    for h in range(departure_hour, hours):
        prob += charge[h] == 0

    prob.solve()

    results = {
        "status": LpStatus[prob.status],
        "hours": list(range(hours)),
        "charge_kw": [max(0, value(charge[h])) for h in range(hours)],
        "prices": prices,
        "energy_needed_kwh": round(energy_needed, 1),
        "departure_hour": departure_hour,
        "target_soc_pct": target_soc_pct
    }

    total_cost = sum(results["charge_kw"][h] * prices[h]
                     for h in range(hours))
    unmanaged_cost = energy_needed * max(prices)
    results["optimized_cost_cad"] = round(total_cost, 2)
    results["unmanaged_cost_cad"] = round(unmanaged_cost, 2)
    results["saving_cad"] = round(unmanaged_cost - total_cost, 2)

    return results


def calculate_peak_shaving(load_forecast, bess_discharge):
    original_peak = max(load_forecast)
    shaved_load = [load_forecast[h] - bess_discharge[h]
                   for h in range(len(load_forecast))]
    shaved_peak = max(shaved_load)
    peak_reduction = original_peak - shaved_peak
    demand_charge_saving = peak_reduction * 15.0
    return {
        "original_peak_kw": round(original_peak, 1),
        "shaved_peak_kw": round(shaved_peak, 1),
        "peak_reduction_kw": round(peak_reduction, 1),
        "demand_charge_saving_cad": round(demand_charge_saving, 2),
        "shaved_load": shaved_load
    }


def get_optimization_explanation(results):
    explanations = []
    prices = results["prices"]

    cheap_hours = [h for h in range(24)
                   if prices[h] == config.ONTARIO_OFF_PEAK]
    peak_hours = [h for h in range(24)
                  if prices[h] == config.ONTARIO_ON_PEAK]

    if cheap_hours:
        explanations.append(
            f"Charge battery during off-peak hours "
            f"({cheap_hours[0]:02d}:00 to {cheap_hours[-1]+1:02d}:00) "
            f"when electricity costs only "
            f"CAD {config.ONTARIO_OFF_PEAK}/kWh."
        )

    if peak_hours:
        explanations.append(
            f"Discharge battery during on-peak hours "
            f"({peak_hours[0]:02d}:00 to {peak_hours[-1]+1:02d}:00) "
            f"when electricity costs CAD {config.ONTARIO_ON_PEAK}/kWh "
            f"saving you money by avoiding expensive grid electricity."
        )

    explanations.append(
        f"Total optimized cost: CAD {results['total_cost_cad']} "
        f"vs CAD {results['baseline_cost_cad']} without optimization. "
        f"Saving: CAD {results['cost_saving_cad']} "
        f"({results['saving_pct']}% reduction)."
    )

    return explanations
