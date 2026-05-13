# GreenGrid AI

**Smart Distributed Energy Resource Management System**
Engineered for North American Enterprise — Ontario & Alberta, Canada

---

## Overview

GreenGrid AI is a commercial web application purpose-built for small Canadian DER operators who manage Solar PV, Battery Energy Storage Systems (BESS), Wind generation, and EV charging fleets. It delivers enterprise-grade intelligence at a fraction of traditional SCADA system costs — targeting operators priced out of USD 500K+ solutions.

> **Demo Mode Active** — All values are simulated for demonstration purposes. Contact us to connect real DER hardware.

---

## Live Demo

| Item | Detail |
|---|---|
| **Access** | `http://localhost:8501` — or hosted link via Streamlit Cloud |
| **Password** | `GreenGrid2026` |
| **Pricing** | CAD 299 / month |
| **Status** | Commercial — Private Product |

---

## Technology Stack

| Technology | Purpose |
|---|---|
| **Streamlit** | Web application framework |
| **Prophet** | ML-powered energy forecasting |
| **PuLP** | Linear programming optimization engine |
| **LangChain + Groq** | AI Advisor RAG chatbot |
| **FAISS** | Vector store for knowledge base |
| **Open-Meteo API** | Real-time Ontario weather data |
| **Plotly** | Interactive charts and Canada map |
| **HuggingFace** | Sentence embeddings (all-MiniLM-L6-v2) |

---

## Six-Page Application

### Page 1 — Live Dashboard
Real-time KPI cards for Solar, Wind, BESS, Load, and Grid power. Includes a 48-hour power flow area chart, DER device status cards with health indicators, energy summary donut chart, and plain English system summary. Auto-refreshes every 30 seconds.

### Page 2 — Forecasting
Integrates the Open-Meteo API to fetch real Ontario weather data. Runs Prophet ML models to forecast solar irradiance, wind speed, load demand, and net load for 24 and 48-hour horizons with uncertainty confidence intervals. Detects offline state and displays an honest unavailability message when the API is unreachable.

### Page 3 — Optimization
PuLP linear programming engine optimizes BESS charge and discharge scheduling for minimum electricity cost using Ontario Time-of-Use (TOU) pricing in CAD. EV smart charging algorithm guarantees 90% battery state by 08:00. Demonstrates up to 61% cost reduction versus unmanaged operation.

### Page 4 — VPP Aggregation
Simulates five Canadian DER sites across Oakville, Kingston, Calgary, Guelph, and Edmonton on an interactive Canada map. Displays real-time IESO and AESO market prices, VPP bid recommendations, and projects CAD 587,779 in annual VPP revenue.

### Page 5 — Ancillary Services
Real-time frequency monitor targeting the 60.00 Hz NERC standard with voltage stability gauge and spinning reserve compliance per NERC BAL-002. Four service cards cover Frequency Regulation, Voltage Support, Spinning Reserve, and Black Start. Includes a grid event log with CSV download and CAD 4,210/month ancillary revenue tracking.

### Page 6 — AI Advisor
LangChain RAG chatbot with FAISS vector store and HuggingFace embeddings. Knowledge base covers Canadian electricity pricing, BESS sizing, solar and wind performance, IESO and AESO market rules, NERC CIP compliance, net metering regulations, and NRCan incentives. Ten example question buttons with persistent chat history.

---

## Site Configuration (Demo)

| Parameter | Value |
|---|---|
| Site Location | Ontario, Canada |
| Solar Capacity | 500 kW |
| Wind Capacity | 200 kW |
| BESS Capacity | 300 kWh |
| BESS Max Rate | 150 kW |
| EV Fleet | 50 kW |
| Grid Limit | 1,000 kW |
| Grid Frequency Target | 60.00 Hz |
| Voltage Nominal | 120 V |

---

## Ontario Electricity Pricing (CAD)

| Period | Rate |
|---|---|
| Off-Peak | $0.074 / kWh |
| Mid-Peak | $0.113 / kWh |
| On-Peak | $0.170 / kWh |

---

## Simulated Data Architecture

The application uses a `data_generator.py` module to produce realistic DER readings without physical hardware:

| Data Stream | Method | Unit |
|---|---|---|
| Solar Output | Sin-wave curve (6am–7pm) + random noise | kW |
| Wind Output | Random base speed + cubic power law | kW |
| Building Load | Hour-based demand profiles + noise | kW |
| Battery Power | Net surplus/deficit reaction logic | kW |
| Battery SOC | Cumulative charge/discharge tracking | % |
| Grid Import | Load minus all local generation | kW |

Real weather data (temperature, solar radiation, wind speed, cloud cover) is fetched live from the **Open-Meteo API** and used to drive the Prophet forecasting models on Page 2.

---

## Installation

### Requirements

- Python 3.10+
- All dependencies listed in `requirements.txt`

### Quick Start

1. Clone or download the repository
2. Place your `.env` file in the project root with:
```
GROQ_API_KEY=your_groq_api_key_here
DEMO_PASSWORD=GreenGrid2026
```
3. Double-click `Launch_GreenGrid_AI.bat` — dependencies install automatically on first run

### Manual Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Project Structure

```
greenGrid-ai/
├── app.py                        # Home page
├── config.py                     # All system settings and constants
├── requirements.txt              # Python dependencies
├── Launch_GreenGrid_AI.bat       # One-click launcher
├── .env                          # API keys and password (not in repo)
├── pages/
│   ├── 1_Live_Dashboard.py
│   ├── 2_Forecasting.py
│   ├── 3_Optimization.py
│   ├── 4_VPP_Aggregation.py
│   ├── 5_Ancillary_Services.py
│   └── 6_AI_Advisor.py
├── modules/
│   ├── data_generator.py         # Simulated DER data engine
│   ├── weather.py                # Open-Meteo API integration
│   ├── forecaster.py             # Prophet ML models
│   ├── optimizer.py              # PuLP optimization engine
│   ├── aggregator.py             # VPP aggregation logic
│   └── ancillary.py              # Grid stability monitoring
├── data/                         # Static reference data
├── compliance/                   # NERC CIP compliance documents
└── docs/                         # Project documentation
```

---

## Commercial Value Proposition

| Metric | Value |
|---|---|
| Target Market | 2,400+ small Canadian DER operators |
| Monthly Subscription | CAD 299 / month |
| Monthly Client Value | CAD 2,845 – 7,465 |
| ROI for Client | 950% – 2,495% per month |
| Competing Enterprise SCADA | USD 500,000+ |

---

## Compliance Standards

- **NERC BAL-002** — Spinning reserve requirements
- **NERC CIP** — Cybersecurity and event logging
- **IEEE 1547** — Distributed resource interconnection
- **IESO** — Ontario Independent Electricity System Operator rules
- **AESO** — Alberta Electric System Operator rules

---

## Author

**Aamir Qadeer**
AI & Energy Engineer
aamirqadeer.ca@gmail.com
GitHub: [aamirqadeerdev](https://github.com/aamirqadeerdev)

---

*GreenGrid AI v1.0 — © 2026 Aamir Qadeer — All Rights Reserved*
*Proprietary Software — Unauthorized copying prohibited*
*Not published on GitHub — Demo available via Zoom screen share*
