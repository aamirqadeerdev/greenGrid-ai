

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

load_dotenv()

# ─── Page Configuration ──────────────────────────────────────
st.set_page_config(page_title="AI Advisor", layout="wide")

st.markdown('<h1 style="color:#00cc44;">AI Energy Advisor</h1>',
            unsafe_allow_html=True)
st.markdown("Ask any question about your energy system in plain English")
st.divider()

# ─── Load Knowledge Base ──────────────────────────────────────
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
DER operators. You answer questions based strictly on the
provided context about Canadian energy markets regulations
and DER management best practices.

Always answer in plain English that a non-technical business
owner can understand. Never use unexplained technical jargon.
If the answer involves money always use Canadian dollars.
If you cannot find the answer in the context say:
"I could not find specific information about this in my
knowledge base. Please contact your grid operator or a
qualified energy engineer for advice on this topic."

Context: {context}

Chat History: {chat_history}

Question: {question}

Answer in plain English:""")

        chain = prompt | llm | StrOutputParser()

        return chain, retriever, True

    except Exception as e:
        return None, None, False


# ─── Initialize ───────────────────────────────────────────────
chain, retriever, kb_loaded = load_knowledge_base()

if not kb_loaded:
    st.error("""
    Knowledge base could not be loaded.
    Please check that the docs/energy_knowledge_base.txt
    file exists and try again.
    """)
    st.stop()

st.success("AI Advisor ready — knowledge base loaded successfully")

# ─── Example Questions ────────────────────────────────────────
st.subheader("Common Questions — Click to Ask")

example_questions = [
    "Why is my solar output lower than expected today?",
    "When is the best time to charge my battery tonight?",
    "How do I register for IESO demand response program?",
    "What are my NERC CIP cybersecurity requirements?",
    "How much is my carbon offset worth in Canadian dollars?",
    "What government grants am I eligible for?",
    "Should I upgrade my battery from 300 kWh to 500 kWh?",
    "What is the current Ontario electricity pricing schedule?",
    "How does frequency regulation earn me money?",
    "What is a Virtual Power Plant and how do I join one?"
]

cols = st.columns(2)
for i, question in enumerate(example_questions):
    with cols[i % 2]:
        if st.button(question, key=f"q_{i}"):
            st.session_state.selected_question = question

st.divider()

# ─── Chat Interface ───────────────────────────────────────────
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
                error_msg = """
                I encountered an error processing your question.
                Please check your internet connection and
                Groq API key and try again.
                """
                st.error(error_msg)

st.divider()

# ─── Knowledge Base Topics ────────────────────────────────────
st.subheader("Topics I Can Help With")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Canadian Electricity Markets**
    - Ontario IESO pricing and markets
    - Alberta AESO pool prices
    - BC Hydro time of use rates
    - How to join energy markets
    - Demand response programs
    """)

with col2:
    st.markdown("""
    **DER Operations**
    - Battery charging best practices
    - Solar panel troubleshooting
    - Wind turbine performance
    - Peak demand management
    - Net metering by province
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
st.caption("GreenGrid AI v1.0 — AI Advisor powered by LangChain + Groq + Llama 3.3 70B")

