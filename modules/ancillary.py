
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def get_grid_frequency():
    base_freq = config.GRID_FREQUENCY_HZ
    deviation = np.random.normal(0, 0.05)
    frequency = round(base_freq + deviation, 3)

    if abs(deviation) >= config.FREQUENCY_CRITICAL:
        status = "CRITICAL"
        color = config.COLOR_CRITICAL
        message = (f"CRITICAL: Frequency {frequency} Hz — "
                   f"immediate action required!")
    elif abs(deviation) >= config.FREQUENCY_WARNING:
        status = "WARNING"
        color = config.COLOR_WARNING
        message = (f"WARNING: Frequency {frequency} Hz — "
                   f"monitor closely.")
    else:
        status = "NORMAL"
        color = config.COLOR_NORMAL
        message = f"NORMAL: Frequency {frequency} Hz — grid stable."

    return {
        "frequency_hz": frequency,
        "deviation_hz": round(deviation, 3),
        "status": status,
        "color": color,
        "message": message
    }


def get_voltage_status():
    nominal = config.VOLTAGE_NOMINAL_V
    deviation_pct = np.random.normal(0, 0.02)
    voltage = round(nominal * (1 + deviation_pct), 1)
    deviation_abs = abs(deviation_pct)

    if deviation_abs >= config.VOLTAGE_CRITICAL_PCT:
        status = "CRITICAL"
        color = config.COLOR_CRITICAL
        message = (f"CRITICAL: Voltage {voltage} V — "
                   f"outside safe operating range!")
    elif deviation_abs >= config.VOLTAGE_WARNING_PCT:
        status = "WARNING"
        color = config.COLOR_WARNING
        message = (f"WARNING: Voltage {voltage} V — "
                   f"approaching limits.")
    else:
        status = "NORMAL"
        color = config.COLOR_NORMAL
        message = f"NORMAL: Voltage {voltage} V — within safe range."

    return {
        "voltage_v": voltage,
        "nominal_v": nominal,
        "deviation_pct": round(deviation_pct * 100, 2),
        "status": status,
        "color": color,
        "message": message
    }


def get_spinning_reserve():
    available = config.BESS_MAX_RATE_KW * np.random.uniform(0.5, 0.9)
    required = config.BESS_MAX_RATE_KW * 0.4
    compliant = available >= required

    return {
        "available_kw": round(available, 1),
        "required_kw": round(required, 1),
        "compliant": compliant,
        "status": "COMPLIANT" if compliant else "NON-COMPLIANT",
        "color": config.COLOR_NORMAL if compliant else config.COLOR_CRITICAL
    }


def get_ancillary_services_status():
    services = [
        {
            "name": "Frequency Regulation",
            "status": "Active",
            "capacity_kw": round(
                config.BESS_MAX_RATE_KW * np.random.uniform(0.3, 0.6), 1
            ),
            "revenue_today_cad": round(np.random.uniform(50, 200), 2),
            "color": config.COLOR_NORMAL
        },
        {
            "name": "Voltage Support",
            "status": "Standby",
            "capacity_kw": round(
                config.BESS_MAX_RATE_KW * np.random.uniform(0.1, 0.3), 1
            ),
            "revenue_today_cad": round(np.random.uniform(20, 80), 2),
            "color": config.COLOR_WARNING
        },
        {
            "name": "Spinning Reserve",
            "status": "Active",
            "capacity_kw": round(
                config.BESS_MAX_RATE_KW * np.random.uniform(0.4, 0.7), 1
            ),
            "revenue_today_cad": round(np.random.uniform(30, 150), 2),
            "color": config.COLOR_NORMAL
        },
        {
            "name": "Black Start",
            "status": "Ready",
            "capacity_kw": config.GENERATOR_KW,
            "revenue_today_cad": round(np.random.uniform(10, 50), 2),
            "color": config.COLOR_NORMAL
        }
    ]
    return services


def generate_grid_events(num_events=10):
    events = []
    now = datetime.now()

    event_types = [
        ("Frequency deviation detected", "WARNING"),
        ("Voltage sag at PCC", "WARNING"),
        ("Frequency regulation activated", "INFO"),
        ("BESS dispatched for grid support", "INFO"),
        ("Demand response signal received", "INFO"),
        ("Grid frequency restored to normal", "INFO"),
        ("Spinning reserve deployed", "WARNING"),
        ("Anti-islanding protection tested", "INFO"),
        ("Voltage support activated", "WARNING"),
        ("Grid event cleared", "INFO")
    ]

    for i in range(num_events):
        event_time = now - timedelta(
            hours=np.random.randint(0, 24),
            minutes=np.random.randint(0, 60)
        )
        event_type, severity = event_types[
            np.random.randint(0, len(event_types))
        ]
        duration = np.random.randint(1, 30)

        events.append({
            "timestamp": event_time.strftime("%Y-%m-%d %H:%M"),
            "event": event_type,
            "severity": severity,
            "duration_min": duration,
            "response": "Automatic" if severity == "INFO" else "Manual review",
            "status": "Resolved"
        })

    events.sort(key=lambda x: x["timestamp"], reverse=True)
    return events


def get_frequency_history(hours=4):
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    timestamps = [now - timedelta(minutes=i*5)
                  for i in range(hours * 12, 0, -1)]
    frequencies = [
        round(config.GRID_FREQUENCY_HZ + np.random.normal(0, 0.03), 3)
        for _ in timestamps
    ]
    return {
        "timestamps": [t.strftime("%H:%M") for t in timestamps],
        "frequencies": frequencies
    }


def get_ancillary_revenue():
    return {
        "frequency_regulation_cad": round(
            np.random.uniform(1500, 3000), 2
        ),
        "voltage_support_cad": round(
            np.random.uniform(500, 1200), 2
        ),
        "spinning_reserve_cad": round(
            np.random.uniform(800, 2000), 2
        ),
        "black_start_cad": round(
            np.random.uniform(200, 600), 2
        )
    }


