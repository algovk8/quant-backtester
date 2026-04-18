import yfinance as yf 
data = yf.download("AAPL", period= "6mo")
print(data)
data["Return"]= data["Close"].pct_change()
data["MA"]=data["Close"].rolling(window=3).mean()
data["Signal"]=0
for i in range(len(data)):
    close =data["Close"].iloc[i].item()
    ma = data["MA"].iloc[i].item()
    ret = data["Return"].iloc[i].item()
    if close>ma and ret>0:
        data.loc[data.index[i],"Signal"]=1
    elif close<ma and ret<0:
        data.loc[data.index[i],"Signal"]=-1
data["Strategy"]=data["Signal"].shift(1)*data["Return"]
total_profit = data["Strategy"].sum()
print("Total Profit:", total_profit)
print(data[["Close","MA","Signal","Strategy"]])
    