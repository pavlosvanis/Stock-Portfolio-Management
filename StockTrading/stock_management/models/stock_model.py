from dataclasses import dataclass
import logging
import os
from stock_management.utils.logger import configure_logger
import requests
from datetime import datetime
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
configure_logger(logger)
load_dotenv()

# todo: replace 'change_to_your_key' with your actual API KEY
api_key = os.getenv("API_KEY")
if not api_key:
        raise ValueError("Did not get API_KEY, recheck .env to see if you entered your api key for AlphaVantage")
url = "https://www.alphavantage.co/query"


@dataclass
class Stock:
    """
        Represents a stock with its symbol, name, price, price change, and P/E ratio.

        Attributes:
            symbol (str): The stock's ticker symbol.
            name (str): The name of the company.
            price (float): Current stock price.
            price_change (float): Daily price change compared to yesterday.
            pe_ratio (float): Price-to-earnings ratio.
    """

    symbol: str
    name: str
    price: float
    price_change: float  # Increase in price compared to yesterday
    pe_ratio: float  # Price-to-Earnings ratio

    def __post_init__(self):
        if self.price < 0:
            raise ValueError(f"Price must be non-negative, got {self.price}")
        if self.price_change < 0:
            raise ValueError(f"Price change must be non-negative, got {self.price_change}")
        if self.pe_ratio < 0:
            raise ValueError(f"P/E ratio must be non-negative, got {self.pe_ratio}")


def lookup_stock(symbol: str) -> dict:
    """
    Get detailed information about a specific stock.

    Args:
        symbol (str): The stock's symbol.

    Returns:
        dict: A dictionary containing the stock's symbol, name, exchange, company description, P/E ratio,
         52 Week High, 52 Week Low, fetched from the Alpha Vantage API. The fields P/E ratio, 52 Week High, 52 Week Low
         might not be available in which case "N/A" will be their value.

    Raises:
        ValueError: If the stock symbol is invalid.
        Exception: If there is an issue with the API request.
    """

    overview_parameters = {
        'function': 'OVERVIEW',
        'symbol': symbol,
        'apikey': api_key
    }

    overview_response = requests.get(url, params=overview_parameters)
    if overview_response.status_code != 200:
        raise Exception(f"API request failed with status code {overview_response.status_code}.")

    overview_data = overview_response.json()

    if not overview_data or "Symbol" not in overview_data:
        raise ValueError(f"The stock symbol: {symbol} is invalid. Please check the symbol and try again.")

    stock_info = {'Symbol': overview_data.get("Symbol"), 'Name': overview_data.get("Name"),
                  'Exchange': overview_data.get("Exchange"),
                  'Description': overview_data.get("Description"),
                  'P/E Ratio': overview_data.get("PERatio", "N/A"),
                  '52 Week High': overview_data.get("52WeekHigh", "N/A"),
                  '52 Week Low': overview_data.get("52WeekLow", "N/A")}

    return stock_info


def get_price_details(symbol: str) -> dict:
    """
    Get the latest market price, price change and percentage change of a specific stock.

    Args:
        symbol (str): The stock's symbol.

    Returns:
        dict: A dictionary containing the current price of a stock, the change in price and percentage
        change from the previous day. If any of the fields is not available, its value will be "N/A".

    Raises:
        ValueError: If the stock symbol is invalid.
        Exception: If there is an issue with the API request.
    """

    global_parameters = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': api_key
    }

    global_response = requests.get(url, params=global_parameters)
    if global_response.status_code != 200:
        raise Exception(f"API request failed with status code {global_response.status_code}.")

    global_data = global_response.json()
    global_quote = global_data.get("Global Quote", {})

    if not global_quote:
        raise ValueError(f"The stock symbol: {symbol} is invalid. Please check the symbol and try again.")

    stock_price_details = {'Current Price': global_quote.get("05. price", "N/A"),
                           'Price Change': global_quote.get("09. change", "N/A"),
                           'Change Percentage': global_quote.get("10. change percent", "N/A")}

    return stock_price_details


def fetch_historical_data(symbol: str, start_date: str, end_date: str) -> list[dict]:
    """
    Get historical price data for a stock within a specified date range.

    Args:
        symbol (str): The stock's ticker symbol.
        start_date (str): The start date for historical data (e.g., `YYYY-MM-DD`).
        end_date (str): The end date for historical data (e.g., `YYYY-MM-DD`).

    Returns:
        list[dict]: A list of dictionaries containing the date, open price,
                    close price, high, low values and trading volume of that day for the stock. If any of the values
                    is unavailable its default value will be "N/A".

    Raises:
        ValueError: -If the symbol is invalid .
                    -If the date format is invalid (not in `YYYY-MM-DD` format).
                    -If no historical data is found for the given symbol or date range.

        Exception: If there is an issue with the API request.
    """

    # Validate date format
    try:
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("The date format you provided is invalid. Please use 'YYYY-MM-DD'.")

    historical_parameters = {
        'function': 'TIME_SERIES_DAILY_ADJUSTED',
        'symbol': symbol,
        'apikey': api_key
    }

    response = requests.get(url, params=historical_parameters, timeout=20)

    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}.")

    data = response.json()

    if "Error Message" in data: #invalid symbol
        raise ValueError(f"The stock symbol: {symbol} is invalid. Please check the symbol again.")

    time_series = data.get("Time Series (Daily)", {})

    if not time_series: #no data in the response
        raise ValueError(f"No historical data found for the stock symbol: {symbol}.")

    # Filter data based on date range
    historical_data = []
    for date, daily_data in time_series.items():
        if start_date <= date <= end_date:
            historical_data.append({
                'date': date,
                'open': daily_data.get("1. open", "N/A"),
                'close': daily_data.get("4. close", "N/A"),
                'high': daily_data.get("2. high", "N/A"),
                'low': daily_data.get("3. low", "N/A"),
                'volume': daily_data.get("6. volume", "N/A")
            })

    return historical_data







