import logging
from typing import Dict, List
from stock_management.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


class UserProfile:
    """
    A class to manage a user's profile, including cash balance, stock holdings,
    and their liked stock list.

    Attributes:
        user_id (int): The unique identifier for the user.
        username (str): The user's name.
        cash_balance (float): The user's available cash balance.
        current_stock_holding (Dict[str, int]): A dictionary mapping stock symbols to quantities owned.
    """

    def __init__(self):
        """
        Initializes the UserProfile with the given user details, an empty stock holding,
        and an empty liked stock list.

        Args:
            user_id (int): The unique identifier for the user.
            username (str): The user's name.
            cash_balance (float): The user's starting cash balance. Defaults to 0.0.
        """
        self.cash_balance = 0,0
        self.current_stock_holding: Dict[str, int] = {}

    def get_portfolio(self) -> Dict[str, int]:
        """
        Retrieves the user's current stock portfolio.

        Returns:
            Dict[str, int]: A dictionary containing stock symbols and the quantity
            that the user hold for each of the stock.
        """
        pass

    def add_stock_to_holding(self, symbol: str, quantity: int) -> None:
        """
        Adds a stock to the user's holdings or updates the quantity if it already exists.
        This method is used when the user buy a new stock.

        Args:
            symbol (str): The stock's ticker symbol.
            quantity (int): The number of shares to add.
        """
        pass

    def get_today_earnings_to_holding(self) -> float:
        """
        Calculates today's earnings from the user's stock holdings.

        The earnings are simply computed based on the total stock price difference 
        between yesterday's and today's cumulative prices in the user's holdings.

        Returns:
            float: The total earnings from today's stock price changes.

        Raises:
            Exception: If there is an issue retrieving stock prices or calculating earnings.
        """
        pass
    

    def remove_stock_from_holding(self, symbol: str, quantity: int) -> None:
        """
        Removes or reduces the quantity of a stock in the user's holdings.
        This method is used when the user sells of the stock in the holdings.

        Args:
            symbol (str): The stock's ticker symbol.
            quantity (int): The number of shares to remove.
        """
        pass

    def update_cash_balance(self, amount: float) -> None:
        """
        Updates the user's cash balance by adding or subtracting the given amount.
        Corresponds to the situation when the user retrieves and add money into the
        account.

        Args:
            amount (float): The amount to add or subtract from the balance.
        """
        pass

    def buy_stock(self, symbol: str, quantity: int) -> None:
        """
        Allows the user to buy shares of a stock.

        Updates the user's portfolio by adding the specified quantity of the stock
        and deducts the total cost (price × quantity) from the user's cash balance.

        Args:
            symbol (str): The stock's ticker symbol.
            quantity (int): The number of shares to purchase.

        Raises:
            ValueError: If the quantity is less than 1, the stock symbol is invalid, or
                        the user has insufficient funds.
            Exception: If there is an issue retrieving stock prices or updating the portfolio.
        """
        pass


    def sell_stock(self, symbol: str, quantity: int) -> None:
        """
        Allows the user to sell shares of a stock.

        Updates the user's portfolio by reducing the specified quantity of the stock
        and adds the total revenue (price × quantity) to the user's cash balance.

        Args:
            symbol (str): The stock's ticker symbol.
            quantity (int): The number of shares to sell.

        Raises:
            ValueError: If the quantity is less than 1, the stock symbol is invalid, or
                        the user does not hold enough shares of the stock.
            Exception: If there is an issue retrieving stock prices or updating the portfolio.
        """
        pass

    def clear_all_stock(self) -> None:
        """
        Clear all stocks
        """