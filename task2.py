import yfinance as yf
data = yf.download("AAPL",period="5D")
print(data["Close"])
data["Return"]= data["Close"].pct_change()
print(data[["Close","Return"]])
for i in range(len(data)):
    date = data.index[i]
    value= data["Return"].iloc[i]
if value>0 :
    print("Buy")
elif value<0 :
    print("Sell")
