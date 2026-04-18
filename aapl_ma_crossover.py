from pathlib import Path
from tempfile import gettempdir

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf


TICKER = "AAPL"
PERIOD = "10y"
SHORT_WINDOW = 50
LONG_WINDOW = 200
CACHE_DIR = Path(gettempdir()) / "yfinance_cache"
TRADING_DAYS_PER_YEAR = 252


def download_data(ticker: str, period: str) -> pd.DataFrame:
    CACHE_DIR.mkdir(exist_ok=True)
    yf.set_tz_cache_location(str(CACHE_DIR))
    data = yf.download(ticker, period=period, auto_adjust=False, progress=False)

    if data.empty:
        raise ValueError(f"No data returned for {ticker}.")

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    return data


def build_strategy(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()
    df["50_MA"] = df["Close"].rolling(window=SHORT_WINDOW).mean()
    df["200_MA"] = df["Close"].rolling(window=LONG_WINDOW).mean()

    crossover_up = (df["50_MA"] > df["200_MA"]) & (
        df["50_MA"].shift(1) <= df["200_MA"].shift(1)
    )
    crossover_down = (df["50_MA"] < df["200_MA"]) & (
        df["50_MA"].shift(1) >= df["200_MA"].shift(1)
    )

    df["Signal"] = 0
    df.loc[crossover_up, "Signal"] = 1
    df.loc[crossover_down, "Signal"] = -1

    df["Position"] = 0
    df.loc[df["Signal"] == 1, "Position"] = 1
    df.loc[df["Signal"] == -1, "Position"] = 0
    df["Position"] = df["Position"].replace(0, pd.NA).ffill().fillna(0)

    df["Daily_Return"] = df["Close"].pct_change().fillna(0)
    df["Buy_Hold_Return"] = df["Daily_Return"]
    df["Strategy_Return"] = df["Position"].shift(1).fillna(0) * df["Daily_Return"]
    df["Cumulative_Buy_Hold_Return"] = (1 + df["Buy_Hold_Return"]).cumprod() - 1
    df["Cumulative_Strategy_Return"] = (1 + df["Strategy_Return"]).cumprod() - 1

    return df


def calculate_sharpe_ratio(returns: pd.Series) -> float:
    volatility = returns.std()
    if volatility == 0 or pd.isna(volatility):
        return 0.0
    return (returns.mean() / volatility) * (TRADING_DAYS_PER_YEAR**0.5)


def print_performance_metrics(df: pd.DataFrame) -> None:
    strategy_total_return = df["Cumulative_Strategy_Return"].iloc[-1]
    buy_hold_total_return = df["Cumulative_Buy_Hold_Return"].iloc[-1]
    strategy_sharpe = calculate_sharpe_ratio(df["Strategy_Return"])
    buy_hold_sharpe = calculate_sharpe_ratio(df["Buy_Hold_Return"])
    buy_count = int((df["Signal"] == 1).sum())
    sell_count = int((df["Signal"] == -1).sum())

    print(f"Ticker: {TICKER}")
    print(f"Period: {PERIOD}")
    print(f"Buy signals: {buy_count}")
    print(f"Sell signals: {sell_count}")
    print("Final Performance Metrics")
    print(f"Strategy total return: {strategy_total_return:.2%}")
    print(f"Buy-and-hold total return: {buy_hold_total_return:.2%}")
    print(f"Excess return vs buy-and-hold: {strategy_total_return - buy_hold_total_return:.2%}")
    print(f"Strategy Sharpe ratio: {strategy_sharpe:.2f}")
    print(f"Buy-and-hold Sharpe ratio: {buy_hold_sharpe:.2f}")
    print(
        df[
            [
                "Close",
                "Daily_Return",
                "Buy_Hold_Return",
                "Strategy_Return",
                "Cumulative_Buy_Hold_Return",
                "Cumulative_Strategy_Return",
            ]
        ].tail(10)
    )


def plot_signals(df: pd.DataFrame, ticker: str) -> None:
    buys = df[df["Signal"] == 1]
    sells = df[df["Signal"] == -1]

    fig, (ax_price, ax_returns) = plt.subplots(
        2, 1, figsize=(14, 10), sharex=True, height_ratios=[3, 2]
    )

    ax_price.plot(df.index, df["Close"], label="Close Price", linewidth=1.3)
    ax_price.plot(df.index, df["50_MA"], label="50-Day MA", linewidth=1.1)
    ax_price.plot(df.index, df["200_MA"], label="200-Day MA", linewidth=1.1)

    ax_price.scatter(
        buys.index,
        buys["Close"],
        label="Buy Signal",
        marker="^",
        color="green",
        s=100,
    )
    ax_price.scatter(
        sells.index,
        sells["Close"],
        label="Sell Signal",
        marker="v",
        color="red",
        s=100,
    )

    ax_price.set_title(f"{ticker} Moving Average Crossover Strategy")
    ax_price.set_ylabel("Price (USD)")
    ax_price.legend()
    ax_price.grid(alpha=0.3)

    ax_returns.plot(
        df.index,
        df["Cumulative_Strategy_Return"],
        label="Strategy Cumulative Return",
        linewidth=1.3,
    )
    ax_returns.plot(
        df.index,
        df["Cumulative_Buy_Hold_Return"],
        label="Buy-and-Hold Cumulative Return",
        linewidth=1.3,
    )
    ax_returns.set_xlabel("Date")
    ax_returns.set_ylabel("Cumulative Return")
    ax_returns.legend()
    ax_returns.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()


def main() -> None:
    data = download_data(TICKER, PERIOD)
    strategy_df = build_strategy(data)
    print_performance_metrics(strategy_df)
    plot_signals(strategy_df, TICKER)


if __name__ == "__main__":
    main()
