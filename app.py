st.markdown("""
<style>
.main {
    background-color: #0e1117;
    color: white;
}
h1, h2, h3 {
    color: #00ffcc;
}
.stMetric {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

st.set_page_config(page_title="Quant Backtester", layout="wide")

# ------------------ TITLE ------------------
st.title("📊 Quant Trading Backtesting Tool")
st.markdown("Test your strategy in seconds — no coding required 🚀")

# ------------------ SIDEBAR ------------------
st.sidebar.header("⚙️ Strategy Settings")

stock = st.sidebar.selectbox(
    "Select Stock",
    ["AAPL", "TSLA", "MSFT", "NVDA", "GOOG"]
)

rsi_period = st.sidebar.slider("RSI Period", 5, 30, 14)
ema_short = st.sidebar.slider("EMA Short", 5, 50, 20)
ema_long = st.sidebar.slider("EMA Long", 20, 200, 50)

stop_loss = st.sidebar.slider("Stop Loss (%)", 1, 10, 3)
take_profit = st.sidebar.slider("Take Profit (%)", 1, 20, 6)

run_button = st.sidebar.button("🚀 Run Backtest")

# ------------------ FUNCTIONS ------------------
def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def backtest(df):
    df['EMA_S'] = df['Close'].ewm(span=ema_short).mean()
    df['EMA_L'] = df['Close'].ewm(span=ema_long).mean()
    df['RSI'] = calculate_rsi(df['Close'], rsi_period)

    df['Signal'] = 0
    df.loc[(df['EMA_S'] > df['EMA_L']) & (df['RSI'] < 70), 'Signal'] = 1

    df['Returns'] = df['Close'].pct_change()
    df['Strategy'] = df['Signal'].shift(1) * df['Returns']

    return df

# ------------------ MAIN ------------------
if run_button:
    data = yf.download(stock, start="2020-01-01")

    df = backtest(data)

    cumulative = (1 + df['Strategy']).cumprod()

    sharpe = (df['Strategy'].mean() / df['Strategy'].std()) * np.sqrt(252)
    win_rate = (df['Strategy'] > 0).mean()

    drawdown = (cumulative / cumulative.cummax() - 1).min()

    # ------------------ METRICS ------------------
    col1, col2, col3 = st.columns(3)

    col1.metric("Sharpe Ratio", f"{sharpe:.2f}")
    col2.metric("Win Rate", f"{win_rate:.2%}")
    col3.metric("Max Drawdown", f"{drawdown:.2%}")

    # ------------------ CHART ------------------
    st.subheader("📈 Equity Curve")

    fig, ax = plt.subplots()
    ax.plot(cumulative)
    ax.set_title("Strategy Performance")

    st.pyplot(fig)

else:
    st.info("👈 Set parameters and click 'Run Backtest'")