from dataclasses import dataclass
import logging
from stock_management.utils.logger import configure_logger
from stock_management.utils.sql_utils import get_db_connection

logger = logging.getLogger(__name__)
configure_logger(logger)

@dataclass
class Stock:
    symbol: str
    name: str
    price: float
    price_change: float  # Increase in price compared to yesterday
    pe_ratio: float      # Price-to-Earnings ratio

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
        dict: A dictionary containing the stock's current price, price change,
              P/E ratio, exchange rate, historical data, and company details
              fetched from the Alpha Vantage API.

    Raises:
        ValueError: If the stock symbol is invalid.
        Exception: If there is an issue with the API or database.
    """
    pass


def get_current_price(symbol: str) -> float:
    """
    Get the latest market price of a specific stock.

    Args:
        symbol (str): The stock's symbol.

    Returns:
        float: The current market price of the stock.

    Raises:
        ValueError: If the stock symbol is invalid.
        Exception: If there is an issue with the API or database.
    """
    pass



def fetch_historical_data(symbol: str, start_date: str, end_date: str) -> list[dict]:
    """
    Get historical price data for a stock within a specified date range.

    Args:
        symbol (str): The stock's ticker symbol.
        start_date (str): The start date for historical data (e.g., `YYYY-MM-DD`).
        end_date (str): The end date for historical data (e.g., `YYYY-MM-DD`).

    Returns:
        list[dict]: A list of dictionaries containing the date, open price,
                    close price, high, and low values for the stock.

    Raises:
        ValueError: If the symbol or date range is invalid.
        Exception: If there is an issue with the API or database.
    """
    pass


def get_stock_by_symbol(symbol: str) -> Stock:
    """
    Retrieves detailed stock information from the database by its symbol.

    Args:
        symbol (str): The stock's ticker symbol.

    Returns:
        Stock: The Stock object representing the requested stock.

    Raises:
        ValueError: If the stock symbol is invalid or not found.
        Exception: If there is an issue with the database.
    """
    pass
