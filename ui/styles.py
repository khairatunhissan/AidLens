import streamlit as st


def apply_styles():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #dfe4ee;
        }
        .title-text {
            font-size: 28px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 10px;
        }
        .card {
            background: white;
            border: 1px solid #d1d5db;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 16px;
        }
        .inner-card {
            background: #f8fafc;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 14px;
            height: 100%;
        }
        .metric-label {
            font-size: 14px;
            font-weight: 600;
            color: #374151;
            margin-bottom: 8px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: 800;
            color: #111827;
        }
        .metric-sub {
            font-size: 13px;
            font-weight: 600;
            color: #15803d;
            margin-top: 6px;
        }
        .summary-list {
            font-size: 14px;
            color: #111827;
            line-height: 1.7;
            padding-left: 18px;
            margin: 0;
        }
        .help-box {
            background: #f8fafc;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 12px 14px;
            margin-top: 10px;
            font-size: 13px;
            color: #374151;
            line-height: 1.5;
        }
        .bar-row {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 14px;
        }
        .bar-label {
            width: 125px;
            font-size: 14px;
            color: #111827;
        }
        .bar-bg {
            flex: 1;
            height: 12px;
            background: #d1d5db;
            border-radius: 999px;
            overflow: hidden;
        }
        .bar-fill-blue {height: 100%; background: #3b82f6;}
        .bar-fill-green {height: 100%; background: #22c55e;}
        .bar-fill-pink {height: 100%; background: #ec4899;}
        .bar-fill-orange {height: 100%; background: #f59e0b;}
        .bar-fill-gray {height: 100%; background: #64748b;}
        .bar-pct {
            width: 42px;
            text-align: right;
            font-size: 13px;
            color: #111827;
        }
        .compare-box-orange {
            background: #f7dfcc;
            border-radius: 6px;
            padding: 14px;
            text-align: center;
            font-weight: 700;
            color: #9a3412;
        }
        .compare-box-green {
            background: #d7f5d7;
            border-radius: 6px;
            padding: 14px;
            text-align: center;
            font-weight: 700;
            color: #15803d;
        }

        /* Main content text only */
        .block-container h1,
        .block-container h2,
        .block-container h3,
        .block-container h4,
        .block-container p,
        .block-container label {
            color: #111827;
        }

        /* Fix Generate Result button */
        div.stButton > button:first-child {
            background-color: #0f172a !important;
            color: #ffffff !important;
            border: 1px solid #0f172a !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }

        div.stButton > button:first-child:hover {
            background-color: #1e293b !important;
            color: #ffffff !important;
            border: 1px solid #1e293b !important;
        }

        div.stButton > button:first-child p,
        div.stButton > button:first-child span,
        div.stButton > button:first-child div {
            color: #ffffff !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )