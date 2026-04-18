import yfinance as yf
import pandas as pd

stocks = ["AAPL", "TSLA" , "MSFT" , "NVDA" , "GOOG"]
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
    # ===== YOUR EXISTING CODE START =====

    delta = data["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    data["RSI"] = 100 - (100 / (1 + rs))

    data["EMA"] = data["Close"].ewm(span=50).mean()

    capital = capital_per_stock
    equity_curve = []

    risk = 0.01

    for i in range(1, len(data)-1):

        # BUY
        if data["RSI"].iloc[i-1] < 30 and data["RSI"].iloc[i] > 30 and data["Close"].iloc[i] > data["EMA"].iloc[i]:

            entry = data["Close"].iloc[i]
            sl = entry * (1 - risk)
            tp = entry * (1 + 2*risk)

            for j in range(i+1, len(data)):
                low = data["Low"].iloc[j]
                high = data["High"].iloc[j]

                if low <= sl:
                    capital *= (1 - risk)
                    equity_curve.append(capital)
                    break

                elif high >= tp:
                    capital *= (1 + 2*risk)
                    equity_curve.append(capital)
                    break

        # SELL
        elif data["RSI"].iloc[i-1] > 70 and data["RSI"].iloc[i] < 70 and data["Close"].iloc[i] < data["EMA"].iloc[i]:

            entry = data["Close"].iloc[i]
            sl = entry * (1 + risk)
            tp = entry * (1 - 2*risk)

            for j in range(i+1, len(data)):
                low = data["Low"].iloc[j]
                high = data["High"].iloc[j]

                if high >= sl:
                    capital *= (1 - risk)
                    equity_curve.append(capital)
                    break

                elif low <= tp:
                    capital *= (1 + 2*risk)
                    equity_curve.append(capital)
                    break

    # ===== RESULTS =====

    total = len(equity_curve)

    if total == 0:
        print("No trades executed")
        continue

    wins = 0
    losses = 0

    for i in range(1, len(equity_curve)):
        if equity_curve[i] > equity_curve[i-1]:
            wins += 1
        else:
            losses += 1

    win_rate = wins / total if total > 0 else 0

    print("Final Capital:", capital)
    print("Total Trades:", total)
    print("Wins:", wins)
    print("Losses:", losses)
    print("Win Rate:", win_rate)
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
df = pd.DataFrame(results_summary)
print("\nFINAL SUMMARY:")
print(df)
total_final_capital = sum(portfolio_results)

print("\n====== PORTFOLIO RESULT ======")
print("Initial Capital:", total_capital)
print("Final Capital:", total_final_capital)
print("Total Return:", (total_final_capital - total_capital) / total_capital)
import matplotlib.pyplot as plt

plt.bar(stocks[:len(portfolio_results)], portfolio_results)
plt.title("Portfolio Final Capital per Stock")
plt.xlabel("Stocks")
plt.ylabel("Capital")
plt.show()