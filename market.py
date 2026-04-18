import yfinance as yf

data = yf.download("EURUSD=X", period="10d")

data["MA"] = data["Close"].rolling(window=3).mean()

# Last two values
last_price = data["Close"].iloc[-1].item()
prev_price = data["Close"].iloc[-2].item()

last_ma = data["MA"].iloc[-1].item()
prev_ma = data["MA"].iloc[-2].item()

print("Last Price:", last_price)
print("Last MA:", last_ma)

# Crossover logic
if prev_price < prev_ma and last_price > last_ma:
    print("BUY signal 📈 (Crossover UP)")
elif prev_price > prev_ma and last_price < last_ma:
    print("SELL signal 📉 (Crossover DOWN)")
else:
    print("No clear signal ❌")
    data["Signal"] = 0

data["Signal"] = 0

data["Signal"] = 0

for i in range(1, len(data)):
    if data["Close"].iloc[i].item() > data["MA"].iloc[i].item():
        data.loc[data.index[i], "Signal"] = 1
    else:
        data.loc[data.index[i], "Signal"] = -1

print(data[["Close", "MA", "Signal"]])