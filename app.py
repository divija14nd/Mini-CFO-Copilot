import streamlit as st
import pandas as pd
from agent.planner import run_agent
from agent.tools import _load_and_prepare_data
from agent.pdf_export import create_single_report_pdf, create_conversation_pdf

# --- Page Configuration ---
st.set_page_config(page_title="CFO Copilot", page_icon="📊", layout="wide")

# --- Custom CSS for Aesthetics ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: #ffffff; /* Plain white background */
    }
    
    .st-emotion-cache-1y4p8pa {
        padding: 2rem; /* Main container padding */
    }

    h1 {
        font-weight: 700;
        color: #1e3a8a; /* Dark Blue */
        text-align: left;
    }
    
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    .stChatMessage {
        background-color: #ffffff;
        border-radius: 0.75rem;
        padding: 1.25rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        border: 2px solid #d1d5db;
        border-left-width: 5px;
    }

    .st-emotion-cache-4k6c94 { 
        border-left-color: #d1d5db;
    }

    .st-emotion-cache-1dj0hjr {
        border-left-color: #22c55e;
    }
    
    .stApp div[data-testid="stChatInput"] {
        background: transparent !important;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    div[data-testid="stChatInput"] > div {
         border-radius: 0.75rem;
         border: 1px solid #d1d5db;
         background-color: #ffffff;
    }

    .stDownloadButton>button {
         background-color: #166534;
         color: white;
         border-radius: 0.5rem;
    }
    .stDownloadButton>button:hover {
         background-color: #14532d;
         color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- Main App ---
st.title("📊 CFO Copilot")
st.write("Welcome! Ask me questions about your monthly financials.")

# --- Load Data ---
@st.cache_data
def load_data():
    files = {
        'actuals': 'fixtures/actuals.csv',
        'budget': 'fixtures/budget.csv',
        'cash': 'fixtures/cash.csv',
        'fx': 'fixtures/fx.csv'
    }
    return _load_and_prepare_data(files)

data_frames = load_data()

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar ---
with st.sidebar:
    st.header("📋 Export")
    st.write("Download your conversation history as a PDF.")
    if st.session_state.messages:
        conversation_pdf_bytes = create_conversation_pdf(st.session_state.messages)
        st.download_button(
            label="Download Conversation",
            data=conversation_pdf_bytes,
            file_name="cfo_copilot_conversation.pdf",
            mime="application/pdf",
        )
    else:
        st.info("No conversation to export yet.")
    st.markdown("---")
    st.subheader("About")
    st.write("This Copilot is designed to answer your company's financial questions using CSV data.")

# --- Display Chat History ---
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "figure" in message and message["figure"] is not None:
            st.pyplot(message["figure"])
            if message["role"] == 'assistant':
                pdf_bytes = create_single_report_pdf(message["content"], message["figure"])
                st.download_button(
                    label="Export Answer",
                    data=pdf_bytes,
                    file_name=f"cfo_report_{i}.pdf",
                    mime="application/pdf",
                    key=f"download_{i}"
                )
        elif message["role"] == 'assistant' and message.get('content') and "Sorry" not in message['content']:
             pdf_bytes = create_single_report_pdf(message["content"], None)
             st.download_button(
                    label="Export Answer",
                    data=pdf_bytes,
                    file_name=f"cfo_report_{i}.pdf",
                    mime="application/pdf",
                    key=f"download_{i}_no_fig"
                )

# --- Chat Input ---
if prompt := st.chat_input("e.g., Show me the revenue trend for the last 6 months"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            summary, figure = run_agent(prompt, data_frames)
            st.markdown(summary)
            if figure:
                st.pyplot(figure)
            assistant_message = {"role": "assistant", "content": summary, "figure": figure}
            st.session_state.messages.append(assistant_message)
            if summary and "Sorry" not in summary:
                 pdf_bytes = create_single_report_pdf(summary, figure)
                 st.download_button(
                    label="Export Answer",
                    data=pdf_bytes,
                    file_name="cfo_report_latest.pdf",
                    mime="application/pdf",
                    key="download_latest"
                )

