import yfinance as yf 
import pandas as pd
data = yf.download("AAPL","TSLA","MSFT","NVDA",period="10y")
print(data["Close"])
delta = data["Close"].diff()
print(delta)
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)
print(gain)
print(loss)
avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()
print(avg_gain)
print(avg_loss)
rs= avg_gain/avg_loss
print(rs)
rsi = 100-(100/(1+rs))
data["RSI"]=rsi
print(data[["Close","RSI"]])
data["Signal"]=0
data["MA"]=data["Close"].rolling(window=20).mean()
for i in range(len(data)):
 rsi = data["RSI"].iloc[i].item()
 close = data["Close"].iloc[i].item()
 ma = data["MA"].iloc[i].item()
 if not pd.isna(rsi) and not pd.isna(ma):
  if i > 0:  # important for previous value

    prev_rsi = data["RSI"].iloc[i-1].item()
    signal=0
    # BUY
    if prev_rsi < 35 and rsi > 35 and (rsi - prev_rsi)>5:
        data.loc[data.index[i], "Signal"] = 1

    # SELL
    elif prev_rsi > 65 and rsi < 65 and (prev_rsi - rsi)>5:
        data.loc[data.index[i], "Signal"] = -1
    if signal == 1 and close < ma:
        continue

    if signal == -1 and close > ma:
        continue
    signal = data.loc[data.index[i],"Signal"]     
data["Return"]= data["Close"].pct_change()
data["Strategy"]=data["Signal"].shift(1)*data["Return"]
total_profit= data["Strategy"].sum()
print("Total Profit:", total_profit)
print(data["Signal"].value_counts())
print("Total Return:", data["Strategy"].sum())
print("Total Trades:",(data["Signal"]!= 0).sum())
print("Winning Trades:",(data["Strategy"]>0).sum())
print("Losing Trades:",(data["Strategy"]<0).sum())
risk = 0.01
reward = 0.02
results = []
data["EMA"]= data["Close"].ewm(span=50).mean()
capital = 10000
equity_curve = []
for i in range(1,len(data)-1):
  if data["RSI"].iloc[i-1].item()<30 and data["RSI"].iloc[i].item()>30 and data["Close"].iloc[i].item()>data["EMA"].iloc[i].item():
   entry = data["Close"].iloc[i].item()
   sl= entry*(1-risk)
   tp= entry*(1+ 2*risk)
   for j in range(i+1, len(data)):
    low= data["Low"].iloc[j].item()
    high= data["High"].iloc[j].item()
    if low <= sl:
        profit = -risk
        capital*= (1+profit)
        equity_curve.append(capital)
        break
    elif high>=tp:
     profit = 2*risk
     capital*= (1+profit)
     equity_curve.append(capital)
     break
  elif data["RSI"].iloc[i-1].item()>70 and data["RSI"].iloc[i].item()<70 and data["Close"].iloc[i].item()<data["EMA"].iloc[i].item():
    entry = data["Close"].iloc[i].item()
    sl = entry * (1 + risk)
    tp = entry * (1- 2*risk)
    for j in range(i+1, len(data)):
        low = data["Low"].iloc[j].item()
        high = data["High"].iloc[j].item()
        # SL hit
        if high >= sl:
            profit = -risk
            capital *= (1 + profit)
            equity_curve.append(capital)
            break  # profit
        elif low<=tp:
             profit = 2*risk
             capital *= (1 + profit)
             equity_curve.append(capital) # loss
             break
if len(equity_curve) == 0:
    print("No trades executed")
    exit()
wins = 0
losses = 0

for i in range(1, len(equity_curve)):
    if equity_curve[i] > equity_curve[i-1]:
        wins += 1
    else:
        losses += 1
total = len(equity_curve)
win_rate = wins/total if total>0 else 0
print("Total Trades:",total)
print("Wins:",wins)
print("Losses:",losses)
print("Win Rate:",win_rate) 
import matplotlib.pyplot as plt
peak = equity_curve[0] 
drawdowns = []
for value in equity_curve:
  if value>peak:
    peak = value
  dd= (peak-value)/peak
  drawdowns.append(dd)
  max_dd = max(drawdowns)  
print("Max Drawdown:",max_dd) 
plt.plot(equity_curve) 
plt.title("Equity Curve")
plt.xlabel("Trades")
plt.ylabel("Capital")
plt.show()  
print((data["RSI"] < 30).sum())
print((data["RSI"] > 70).sum())