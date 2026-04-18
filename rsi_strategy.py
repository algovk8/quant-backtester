# RSI = speed of price movement
import yfinance as yf 
import pandas as pd
data = yf.download("AAPL",period="5y")
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
for i in range(len(data)-1):
  signal = data["Signal"].iloc[i]
  if signal == 1 :
   entry = data["Close"].iloc[i].item()
   sl= entry*(1-risk)
   tp= entry*(1+0.015)
   max_price = entry
   for j in range(i+1, len(data)):
    low= data["Low"].iloc[j].item()
    high= data["High"].iloc[j].item()
    if high > max_price:
        max_price = high

    # trailing SL (lock profit)
    if max_price >= entry * 1.01:
        sl = entry  # break-even

    if low <= sl:
        results.append(-1)
        break
    elif high>=tp:
     results.append(2)
     break
  elif signal == -1:
   entry = data["Close"].iloc[i].item()
   sl= entry*(1+0.015)
   tp= entry*(1-reward)
   for j in range (i+1,len(data)):
    low= data["Low"].iloc[j].item()
    high= data["High"].iloc[j].item()
    if high>=sl:
     results.append(-1)
     break
    elif low<=tp:
     results.append(2)
     break
Wins = results.count(2)
losses = results.count(-1)
total = len(results)
win_rate = Wins/total if total>0 else 0
print("Total Trades:",total)
print("Wins:",Wins)
print("Losses:",losses)
print("Win Rate:",win_rate) 
