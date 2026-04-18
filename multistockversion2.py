import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

stocks = ["AAPL", "TSLA", "MSFT", "NVDA", "GOOG"]

total_capital = 10000
capital_per_stock = total_capital / len(stocks)

portfolio_results = []
results_summary = []

for stock in stocks:

    print("\n====================")
    print("Running for:", stock)

    data = yf.download(stock, period="5y")

    if data.empty:
        print("No data for", stock)
        continue

    data.columns = data.columns.droplevel(1)

    # ===== RSI =====
    delta = data["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    data["RSI"] = 100 - (100 / (1 + rs))

    # ===== EMA =====
    data["EMA"] = data["Close"].ewm(span=50).mean()

    capital = capital_per_stock
    equity_curve = []

    risk = 0.01
    in_trade = False

    for i in range(1, len(data) - 2):

        if in_trade:
            continue

        # ===== BUY =====
        if (
            data["RSI"].iloc[i-1] < 30
            and data["RSI"].iloc[i] > 30
            and data["Close"].iloc[i] > data["EMA"].iloc[i]
        ):

            entry = data["Close"].iloc[i+1]  # FIXED (no lookahead)
            sl = entry * (1 - risk)
            tp = entry * (1 + 2*risk)

            in_trade = True

            for j in range(i+1, len(data)):
                low = data["Low"].iloc[j]
                high = data["High"].iloc[j]

                if low <= sl:
                    capital *= (1 - risk)
                    equity_curve.append(capital)
                    in_trade = False
                    break

                elif high >= tp:
                    capital *= (1 + 2*risk)
                    equity_curve.append(capital)
                    in_trade = False
                    break

        # ===== SELL =====
        elif (
            data["RSI"].iloc[i-1] > 70
            and data["RSI"].iloc[i] < 70
            and data["Close"].iloc[i] < data["EMA"].iloc[i]
        ):

            entry = data["Close"].iloc[i+1]  # FIXED
            sl = entry * (1 + risk)
            tp = entry * (1 - 2*risk)

            in_trade = True

            for j in range(i+1, len(data)):
                low = data["Low"].iloc[j]
                high = data["High"].iloc[j]

                if high >= sl:
                    capital *= (1 - risk)
                    equity_curve.append(capital)
                    in_trade = False
                    break

                elif low <= tp:
                    capital *= (1 + 2*risk)
                    equity_curve.append(capital)
                    in_trade = False
                    break

    # ===== RESULTS =====
    total = len(equity_curve)

    if total == 0:
        print("No trades executed")
        continue

    wins = sum(
        1 for i in range(1, len(equity_curve))
        if equity_curve[i] > equity_curve[i-1]
    )
    losses = total - wins

    win_rate = wins / total if total > 0 else 0

    print("Final Capital:", capital)
    print("Total Trades:", total)
    print("Wins:", wins)
    print("Losses:", losses)
    print("Win Rate:", win_rate)

    # ===== FILTER BAD STOCKS =====
    if win_rate < 0.4:
        print("Skipping bad stock:", stock)
        continue

    results_summary.append({
        "Stock": stock,
        "Final Capital": capital,
        "Trades": total,
        "Win Rate": win_rate
    })

    portfolio_results.append(capital)

# ===== AFTER LOOP =====

if len(portfolio_results) == 0:
    print("No good stocks found.")
    exit()

df = pd.DataFrame(results_summary)

print("\n===== FINAL SUMMARY =====")
print(df)

actual_invested = capital_per_stock * len(portfolio_results)
total_final_capital = sum(portfolio_results)

print("\n====== PORTFOLIO RESULT ======")
print("Initial Capital:", actual_invested)
print("Final Capital:", total_final_capital)
print("Total Return:", (total_final_capital - actual_invested) / actual_invested)

# ===== PLOT =====
valid_stocks = df["Stock"].tolist()

plt.bar(valid_stocks, portfolio_results)
plt.title("Portfolio Final Capital per Stock")
plt.xlabel("Stocks")
plt.ylabel("Capital")
plt.show()