

import pandas as pd
import numpy as np
from prophet import Prophet
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.data_generator import get_der_dataframe
import config
import streamlit as st


def prepare_prophet_data(df, column):
    prophet_df = df[['timestamp', column]].copy()
    prophet_df.columns = ['ds', 'y']
    prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
    return prophet_df


def train_and_forecast(df, column, horizon_hours=24):
    prophet_df = prepare_prophet_data(df, column)

    model = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=False,
        interval_width=0.80,
        changepoint_prior_scale=0.05
    )

    model.fit(prophet_df)

    future = model.make_future_dataframe(
        periods=horizon_hours,
        freq='H'
    )

    forecast = model.predict(future)

    forecast_only = forecast.tail(horizon_hours)[
        ['ds', 'yhat', 'yhat_lower', 'yhat_upper']
    ].copy()

    forecast_only.columns = [
        'timestamp', 'forecast', 'lower_bound', 'upper_bound'
    ]

    forecast_only['forecast'] = forecast_only['forecast'].clip(lower=0)
    forecast_only['lower_bound'] = forecast_only['lower_bound'].clip(lower=0)
    forecast_only['upper_bound'] = forecast_only['upper_bound'].clip(lower=0)

    return forecast_only


@st.cache_data(ttl=3600)
def get_solar_forecast(horizon_hours=24):
    df = get_der_dataframe(hours=168)
    return train_and_forecast(df, 'solar_kw', horizon_hours)


@st.cache_data(ttl=3600)
def get_wind_forecast(horizon_hours=24):
    df = get_der_dataframe(hours=168)
    return train_and_forecast(df, 'wind_kw', horizon_hours)


@st.cache_data(ttl=3600)
def get_load_forecast(horizon_hours=24):
    df = get_der_dataframe(hours=168)
    return train_and_forecast(df, 'load_kw', horizon_hours)


@st.cache_data(ttl=3600)
def get_net_load_forecast(horizon_hours=24):
    solar = get_solar_forecast(horizon_hours)
    wind = get_wind_forecast(horizon_hours)
    load = get_load_forecast(horizon_hours)

    net = load.copy()
    net['forecast'] = (
        load['forecast'] - solar['forecast'] - wind['forecast']
    ).clip(lower=0)
    net['lower_bound'] = (
        load['lower_bound'] - solar['upper_bound'] - wind['upper_bound']
    ).clip(lower=0)
    net['upper_bound'] = (
        load['upper_bound'] - solar['lower_bound'] - wind['lower_bound']
    ).clip(lower=0)

    return net


def calculate_accuracy(actual, predicted):
    if len(actual) == 0 or len(predicted) == 0:
        return {
            "mae": "NOT AVAILABLE",
            "mape": "NOT AVAILABLE",
            "r2": "NOT AVAILABLE"
        }

    actual = np.array(actual)
    predicted = np.array(predicted)

    mae = np.mean(np.abs(actual - predicted))

    mask = actual != 0
    if mask.sum() > 0:
        mape = np.mean(
            np.abs((actual[mask] - predicted[mask]) / actual[mask])
        ) * 100
    else:
        mape = 0

    ss_res = np.sum((actual - predicted) ** 2)
    ss_tot = np.sum((actual - np.mean(actual)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

    return {
        "mae": round(mae, 2),
        "mape": round(mape, 2),
        "r2": round(r2, 4)
    }


def get_forecast_summary(solar_fc, wind_fc, load_fc):
    summary = {
        "total_solar_kwh": round(solar_fc['forecast'].sum(), 0),
        "total_wind_kwh": round(wind_fc['forecast'].sum(), 0),
        "peak_load_kw": round(load_fc['forecast'].max(), 0),
        "peak_load_hour": load_fc.loc[
            load_fc['forecast'].idxmax(), 'timestamp'
        ].strftime('%H:%M'),
        "min_load_kw": round(load_fc['forecast'].min(), 0),
        "total_renewable_kwh": round(
            solar_fc['forecast'].sum() + wind_fc['forecast'].sum(), 0
        )
    }
    return summary

