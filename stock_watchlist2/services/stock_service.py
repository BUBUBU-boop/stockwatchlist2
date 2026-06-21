import yfinance as yf


def ticker_exists(ticker):
    try:
        stock = yf.Ticker(ticker)

        info = stock.info

        return bool(info)

    except Exception:
        return False


def get_stock_data(ticker):
    stock = yf.Ticker(ticker)

    history = stock.history(period="2d")

    info = stock.info

    current_price = float(history["Close"].iloc[-1])

    previous_close = float(history["Close"].iloc[-2])

    change = current_price - previous_close

    change_percent = (
        (change / previous_close) * 100
        if previous_close
        else 0
    )

    currency = info.get("currency", "")

    currency_symbol_map = {
        "USD": "$",
        "JPY": "¥"
    }

    currency_symbol = currency_symbol_map.get(
        currency,
        currency
    )

    return {
        "ticker": ticker,
        "name": info.get("shortName", ticker),
        "current_price": current_price,
        "previous_close": previous_close,
        "change": change,
        "change_percent": change_percent,
        "high": info.get("dayHigh"),
        "low": info.get("dayLow"),
        "open": info.get("open"),
        "currency": currency,
        "currency_symbol": currency_symbol
    }

def get_chart_data(ticker, period):
    period_map = {
        "1m": "1mo",
        "3m": "3mo",
        "1y": "1y"
    }

    history = yf.Ticker(ticker).history(
        period=period_map.get(period, "3mo")
    )

    labels = [
        index.strftime("%Y-%m-%d")
        for index in history.index
    ]

    prices = [
        float(price)
        for price in history["Close"].tolist()
    ]

    return {
        "labels": labels,
        "prices": prices
    }