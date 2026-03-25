

from modules.ui_utils import hide_running_man
hide_running_man()

import streamlit as st
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import config
from modules.forecaster import (
    get_solar_forecast,
    get_wind_forecast,
    get_load_forecast,
    get_net_load_forecast
)

load_dotenv()


# --- Build Live Forecast Context -------------------------------------------
def build_live_forecast_context():
    """
    Generates a plain-English summary of today's Prophet forecasts.
    This is injected into every RAG prompt so the LLM can answer
    time-specific questions about today's generation and export.
    """
    try:
        solar_fc  = get_solar_forecast(horizon_hours=24)
        wind_fc   = get_wind_forecast(horizon_hours=24)
        load_fc   = get_load_forecast(horizon_hours=24)
        net_fc    = get_net_load_forecast(horizon_hours=24)

        # Peak solar
        solar_peak_row  = solar_fc.loc[solar_fc['forecast'].idxmax()]
        solar_peak_kw   = solar_peak_row['forecast']
        solar_peak_time = solar_peak_row['timestamp'].strftime('%H:%M')

        # Peak wind
        wind_peak_row   = wind_fc.loc[wind_fc['forecast'].idxmax()]
        wind_peak_kw    = wind_peak_row['forecast']
        wind_peak_time  = wind_peak_row['timestamp'].strftime('%H:%M')

        # Combined generation per hour — FIX: track solar and wind separately
        combined = solar_fc.copy()
        combined['solar_gen'] = solar_fc['forecast']
        combined['wind_gen']  = wind_fc['forecast']
        combined['total_gen'] = solar_fc['forecast'] + wind_fc['forecast']
        combined['net_export'] = combined['total_gen'] - load_fc['forecast']

        # Best export hour = highest (generation - load)
        export_row   = combined.loc[combined['net_export'].idxmax()]
        export_time  = export_row['timestamp'].strftime('%H:%M')
        export_kw    = max(export_row['net_export'], 0)

        # Total daily figures
        total_solar_kwh  = round(solar_fc['forecast'].sum(), 0)
        total_wind_kwh   = round(wind_fc['forecast'].sum(), 0)
        total_load_kwh   = round(load_fc['forecast'].sum(), 0)
        peak_load_kw     = round(load_fc['forecast'].max(), 0)
        peak_load_time   = load_fc.loc[
            load_fc['forecast'].idxmax(), 'timestamp'
        ].strftime('%H:%M')

        # Hours with surplus generation (export possible)
        export_hours = combined[combined['net_export'] > 0]
        if len(export_hours) > 0:
            first_export = export_hours.iloc[0]['timestamp'].strftime('%H:%M')
            last_export  = export_hours.iloc[-1]['timestamp'].strftime('%H:%M')
            export_window = f"from {first_export} to {last_export}"
        else:
            export_window = "no surplus generation forecast today"

        # Hourly breakdown — FIX: show solar, wind, total separately
        hourly_lines = []
        for _, row in combined.iterrows():
            hour     = row['timestamp'].strftime('%H:%M')
            solar    = row['solar_gen']
            wind     = row['wind_gen']
            total    = row['total_gen']
            load_val = load_fc.loc[
                load_fc['timestamp'] == row['timestamp'], 'forecast'
            ]
            load_val = load_val.values[0] if len(load_val) > 0 else 0
            net      = total - load_val
            status   = "SURPLUS — can export" if net > 0 else "DEFICIT — importing from grid"
            hourly_lines.append(
                f"  {hour}: Solar {solar:.0f} kW, Wind {wind:.0f} kW, "
                f"Total Gen {total:.0f} kW, Load {load_val:.0f} kW, "
                f"Net {net:+.0f} kW ({status})"
            )
        hourly_text = "\n".join(hourly_lines)

        summary = f"""
=== LIVE FORECAST DATA FOR TODAY ===
(Generated from Prophet ML models — use this to answer time-specific questions)

SOLAR FORECAST TODAY:
- Total solar generation: {total_solar_kwh:.0f} kWh
- Peak solar output: {solar_peak_kw:.0f} kW at {solar_peak_time}

WIND FORECAST TODAY:
- Total wind generation: {total_wind_kwh:.0f} kWh
- Peak wind output: {wind_peak_kw:.0f} kW at {wind_peak_time}

LOAD FORECAST TODAY:
- Total load demand: {total_load_kwh:.0f} kWh
- Peak load demand: {peak_load_kw:.0f} kW at {peak_load_time}

EXPORT OPPORTUNITY TODAY:
- Maximum export window: {export_window}
- Best single hour for export: {export_time} with approximately {export_kw:.0f} kW surplus

HOURLY GENERATION vs LOAD BREAKDOWN:
(Each hour shows Solar, Wind, Total Generation, Load, and Net status)
{hourly_text}
=====================================
"""
        return summary

    except Exception as e:
        return f"\n=== LIVE FORECAST DATA: Unavailable ({str(e)}) ===\n"


# --- Page Configuration ----------------------------------------------------
st.set_page_config(page_title="AI Advisor", layout="wide")

st.markdown('<h1 style="color:#00cc44;">AI Energy Advisor</h1>',
            unsafe_allow_html=True)
st.markdown("Ask any question about your energy system in plain English")
st.divider()


# --- Load Knowledge Base ---------------------------------------------------
@st.cache_resource
def load_knowledge_base():
    docs_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "docs",
        "energy_knowledge_base.txt"
    )

    try:
        loader = TextLoader(docs_path, encoding='utf-8')
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = splitter.split_documents(documents)

        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        vector_store = FAISS.from_documents(chunks, embeddings)
        retriever = vector_store.as_retriever(
            search_kwargs={"k": 4}
        )

        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.3
        )

        prompt = PromptTemplate.from_template("""
You are GreenGrid AI's expert energy advisor for small Canadian
DER operators. You answer questions using two sources:

1. KNOWLEDGE BASE CONTEXT: General knowledge about Canadian energy
   markets, regulations, battery best practices, solar/wind performance,
   NERC compliance, grants and net metering.

2. LIVE FORECAST DATA: Real-time Prophet ML forecast for TODAY showing
   hourly solar generation, wind generation, load demand, and net
   export/import at each hour.

When a question is about TODAY (e.g. "when will I have maximum export",
"what time should I charge my battery today", "when is peak generation"),
use the LIVE FORECAST DATA to give a specific, time-based answer.

IMPORTANT RULES FOR READING FORECAST DATA:
- Each hour in the breakdown shows Solar, Wind, Total Generation, Load, and Net separately.
- When asked about wind output at a specific time, read ONLY the Wind value for that hour.
- When asked about solar output at a specific time, read ONLY the Solar value for that hour.
- Peak wind output is the single highest Wind value across all hours.
- Peak solar output is the single highest Solar value across all hours.
- Never confuse Total Generation with Solar-only or Wind-only values.
- Net = Total Generation minus Load. Positive Net means surplus (can export). Negative means deficit (importing).

For general knowledge questions use the KNOWLEDGE BASE CONTEXT.

Always answer in plain English that a non-technical business owner
can understand. Never use unexplained technical jargon.
If the answer involves money always use Canadian dollars.
If you cannot find the answer in either source say:
"I could not find specific information about this in my knowledge base.
Please contact your grid operator or a qualified energy engineer."

Knowledge Base Context: {context}

Live Forecast Data: {live_forecast}

Chat History: {chat_history}

Question: {question}

Answer in plain English:""")

        chain = prompt | llm | StrOutputParser()

        return chain, retriever, True

    except Exception as e:
        return None, None, False


# --- Initialize ------------------------------------------------------------
chain, retriever, kb_loaded = load_knowledge_base()

if not kb_loaded:
    st.error("""
    Knowledge base could not be loaded.
    Please check that the docs/energy_knowledge_base.txt
    file exists and try again.
    """)
    st.stop()

st.success("AI Advisor ready — knowledge base loaded successfully")

# Load live forecast once per session
with st.spinner("Loading today's forecast data..."):
    live_forecast_context = build_live_forecast_context()

if "Unavailable" in live_forecast_context:
    st.warning("Live forecast data unavailable — Advisor will answer from knowledge base only.")
else:
    st.info("Live forecast data loaded — I can answer questions about today's generation and export times.")


# --- Example Questions -----------------------------------------------------
st.subheader("Common Questions — Click to Ask")

example_questions = [
    "At what time today will I have maximum energy to export?",
    "When is the best time to charge my battery today?",
    "What is my peak solar generation time today?",
    "What is my peak wind generation time today?",
    "What is the wind output at 5pm today?",
    "How do I register for IESO demand response program?",
    "What are my NERC CIP cybersecurity requirements?",
    "How much is my carbon offset worth in Canadian dollars?",
    "What government grants am I eligible for?",
    "Should I upgrade my battery from 300 kWh to 500 kWh?",
]

cols = st.columns(2)
for i, question in enumerate(example_questions):
    with cols[i % 2]:
        if st.button(question, key=f"q_{i}"):
            st.session_state.selected_question = question

st.divider()


# --- Chat Interface --------------------------------------------------------
st.subheader("Ask Your Question")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "selected_question" not in st.session_state:
    st.session_state.selected_question = ""

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle selected question from buttons
question = None
if st.session_state.selected_question:
    question = st.session_state.selected_question
    st.session_state.selected_question = ""
else:
    question = st.chat_input(
        "Ask anything about your energy system..."
    )

# Process question
if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            try:
                docs = retriever.invoke(question)
                context = "\n\n".join(
                    doc.page_content for doc in docs
                )

                history_text = ""
                for human, assistant in st.session_state.chat_history:
                    history_text += (
                        f"Human: {human}\n"
                        f"Assistant: {assistant}\n"
                    )

                answer = chain.invoke({
                    "context": context,
                    "live_forecast": live_forecast_context,
                    "chat_history": history_text,
                    "question": question
                })

                st.markdown(answer)

                st.session_state.chat_history.append(
                    (question, answer)
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:
                st.error(
                    "I encountered an error processing your question. "
                    "Please check your internet connection and "
                    "Groq API key and try again."
                )

st.divider()


# --- Knowledge Base Topics -------------------------------------------------
st.subheader("Topics I Can Help With")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Today's Live Data**
    - Maximum export time today
    - Best battery charging window
    - Peak solar generation hour
    - Peak wind generation hour
    - Hourly generation vs load
    - Surplus energy windows
    """)

with col2:
    st.markdown("""
    **Canadian Electricity Markets**
    - Ontario IESO pricing and markets
    - Alberta AESO pool prices
    - BC Hydro time of use rates
    - How to join energy markets
    - Demand response programs
    """)

with col3:
    st.markdown("""
    **Compliance and Incentives**
    - NERC CIP cybersecurity rules
    - Canadian government grants
    - Carbon offset calculations
    - IEEE 1547 requirements
    - Provincial net metering rules
    """)

st.divider()
st.caption("GreenGrid AI v1.0 — AI Advisor powered by LangChain + Groq + Llama 3.3 70B + Live Prophet Forecasts")

