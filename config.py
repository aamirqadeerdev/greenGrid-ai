
import os
from dotenv import load_dotenv

load_dotenv()

# ─── API Keys ───────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ─── Site Configuration ──────────────────────────────────────
SITE_NAME = "GreenGrid AI — Demo Site"
SITE_LOCATION = "Ontario, Canada"
SITE_LATITUDE = 43.6532
SITE_LONGITUDE = -79.3832

# ─── DER Capacities (kW) ─────────────────────────────────────
SOLAR_CAPACITY_KW = 500
WIND_CAPACITY_KW = 200
BESS_CAPACITY_KWH = 300
BESS_MAX_RATE_KW = 150
EV_FLEET_KW = 50
HVAC_KW = 100
GENERATOR_KW = 250
GRID_LIMIT_KW = 1000

# ─── BESS Settings ───────────────────────────────────────────
BESS_SOC_MIN = 0.20
BESS_SOC_MAX = 0.90
BESS_SOC_INITIAL = 0.50
BESS_EFFICIENCY = 0.95
BESS_MAX_CYCLES_PER_DAY = 2

# ─── Grid Settings ───────────────────────────────────────────
GRID_FREQUENCY_HZ = 60.00
FREQUENCY_WARNING = 0.2
FREQUENCY_CRITICAL = 0.5
VOLTAGE_NOMINAL_V = 120
VOLTAGE_WARNING_PCT = 0.05
VOLTAGE_CRITICAL_PCT = 0.10

# ─── Canadian Electricity Pricing (CAD $/kWh) ────────────────
ONTARIO_OFF_PEAK = 0.074
ONTARIO_MID_PEAK = 0.113
ONTARIO_ON_PEAK = 0.170
ALBERTA_AVERAGE = 0.085
BC_OFF_PEAK = 0.094
BC_ON_PEAK = 0.142

# ─── Forecasting Settings ────────────────────────────────────
FORECAST_HORIZON_24H = 24
FORECAST_HORIZON_48H = 48
FORECAST_INTERVAL_MIN = 15

# ─── Dashboard Settings ──────────────────────────────────────
DASHBOARD_REFRESH_SECONDS = 30
CHART_HEIGHT = 400

# ─── VPP Settings ────────────────────────────────────────────
VPP_MAX_SITES = 5
VPP_MAX_CAPACITY_KW = 10000

# ─── Alert Colors ────────────────────────────────────────────
COLOR_NORMAL = "#00cc44"
COLOR_WARNING = "#ff8c00"
COLOR_CRITICAL = "#ff0000"
COLOR_INFO = "#1890ff"
COLOR_SOLAR = "#f4c542"
COLOR_WIND = "#42a4f5"
COLOR_BESS = "#7b42f5"
COLOR_GRID = "#f54242"
COLOR_EV = "#42f5a7"

