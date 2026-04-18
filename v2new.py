import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ================= SETTINGS =================
stocks = ["AAPL", "TSLA", "MSFT", "NVDA", "GOOG"]
total_capital = 10000
capital_per_stock = total_capital / len(stocks)

risk = 0.01
spread = 0.0002
fee = 0.001

# ================= FUNCTIONS =================

def get_data(stock):
    data = yf.download(stock, period="5y")
    if data.empty:
        return None
    data.columns = data.columns.droplevel(1)
    return data

def calculate_indicators(data):
    delta = data["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    data["RSI"] = 100 - (100 / (1 + rs))

    data["EMA"] = data["Close"].ewm(span=50).mean()
    return data

def run_strategy(data, capital):
    equity_curve = []
    in_trade = False
    trade_count = 0

    for i in range(5, len(data) - 2):

        if in_trade:
            continue

        # ===== V2.1 BUY STRATEGY =====
        if (
            data["EMA"].iloc[i] > data["EMA"].iloc[i-5] and   # Uptrend
            data["Close"].iloc[i] > data["EMA"].iloc[i] and   # Above EMA
            data["RSI"].iloc[i-1] < 40 and data["RSI"].iloc[i] > 40 and
            data["Close"].iloc[i] > data["Close"].iloc[i-1]   # Momentum
        ):

            entry = data["Close"].iloc[i+1] + spread
            sl = entry * (1 - risk)
            tp = entry * (1 + 1.8*risk)  # UPDATED TP

            in_trade = True
            trade_count += 1

            for j in range(i+1, len(data)):
                low = data["Low"].iloc[j]
                high = data["High"].iloc[j]

                if low <= sl:
                    capital *= (1 - risk - fee)
                    equity_curve.append(capital)
                    in_trade = False
                    break

                elif high >= tp:
                    capital *= (1 + 1.8*risk - fee)
                    equity_curve.append(capital)
                    in_trade = False
                    break

    return capital, equity_curve, trade_count

def evaluate_performance(equity_curve):
    if len(equity_curve) < 2:
        return 0, 0

    eq = pd.Series(equity_curve)
    returns = eq.pct_change().dropna()

    if returns.std() == 0 or len(returns) < 2:
        sharpe = 0
    else:
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252)

    max_dd = (eq.cummax() - eq).max()

    return sharpe, max_dd

# ================= MAIN =================

portfolio_results = []
results_summary = []

for stock in stocks:

    print("\n====================")
    print("Running for:", stock)

    data = get_data(stock)
    if data is None:
        continue

    data = calculate_indicators(data)

    final_capital, equity_curve, trade_count = run_strategy(data, capital_per_stock)

    if len(equity_curve) == 0:
        print("No trades executed")
        continue

    total = len(equity_curve)

    wins = sum(
        1 for i in range(1, len(equity_curve))
        if equity_curve[i] > equity_curve[i-1]
    )
    win_rate = wins / total

    sharpe, max_dd = evaluate_performance(equity_curve)

    print("Final Capital:", round(final_capital, 2))
    print("Trades Taken:", trade_count)
    print("Win Rate:", round(win_rate, 2))
    print("Sharpe Ratio:", round(sharpe, 2))
    print("Max Drawdown:", round(max_dd, 2))

    if win_rate < 0.4:
        print("Skipping bad stock:", stock)
        continue

    results_summary.append({
        "Stock": stock,
        "Final Capital": final_capital,
        "Trades": total,
        "Win Rate": win_rate,
        "Sharpe": sharpe,
        "Max Drawdown": max_dd
    })

    portfolio_results.append(final_capital)

# ================= FINAL =================

if len(portfolio_results) == 0:
    print("No good stocks found.")
    exit()

df = pd.DataFrame(results_summary)

print("\n===== FINAL SUMMARY =====")
print(df)

df.to_csv("results_v2_1.csv", index=False)

actual_invested = capital_per_stock * len(portfolio_results)
total_final_capital = sum(portfolio_results)

print("\n====== PORTFOLIO RESULT ======")
print("Initial Capital:", actual_invested)
print("Final Capital:", round(total_final_capital, 2))
print("Total Return:", round((total_final_capital - actual_invested) / actual_invested, 2))

# ===== PLOT =====
valid_stocks = df["Stock"].tolist()

plt.bar(valid_stocks, portfolio_results)
plt.title("Portfolio Final Capital per Stock (V2.1)")
plt.xlabel("Stocks")
plt.ylabel("Capital")
plt.show()
