import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class UserProfile:
    """
    A class to manage a user's profile, including cash balance, stock holdings,
    and their liked stock list.
    """

    def __init__(self, user_id: int, username: str, cash_balance: float = 0.0):
        """
        Initializes the UserProfile with the given user details, an empty stock holding,
        and an empty liked stock list.

        Args:
            user_id (int): The user's unique ID.
            username (str): The username of the user.
            cash_balance (float): The initial cash balance of the user.
        """
        if cash_balance < 0:
            raise ValueError("Cash balance must be non-negative")
        
        self.user_id = user_id
        self.username = username
        self.cash_balance = cash_balance
        # Dict[<symbol>, (<quantity>, <bought_price>)]
        self.current_stock_holding: Dict[str, Tuple[int, float]] = {}

    def get_holding_stocks(self) -> Dict[str, Tuple[int, float]]:
        """Returns the user's current stock holdings."""
        return self.current_stock_holding

    def get_cash_balance(self) -> float:
        """Returns the user's current cash balance."""
        return self.cash_balance

    def add_stock_to_portfolio(self, symbol: str, quantity: int, bought_price: float) -> None:
        """
        Adds a stock to the user's holdings or updates the quantity if it already exists.

        Args:
            symbol (str): The stock's ticker symbol.
            quantity (int): The number of shares to add.
            bought_price (float): The price at which the stock was purchased.
        """
        if quantity < 1 or bought_price < 0:
            raise ValueError("Quantity must be positive, and price must be non-negative.")

        if symbol in self.current_stock_holding:
            current_quantity, average_price = self.current_stock_holding[symbol]
            total_quantity = current_quantity + quantity
            # Calculate weighted average price
            new_average_price = ((current_quantity * average_price) + (quantity * bought_price)) / total_quantity
            self.current_stock_holding[symbol] = (total_quantity, new_average_price)
        else:
            self.current_stock_holding[symbol] = (quantity, bought_price)

        logger.info("Added or updated stock %s: %d shares at an average price of %.2f.", symbol, quantity, bought_price)

    def remove_stock_from_holding(self, symbol: str, quantity: int) -> None:
        """
        Removes or reduces the quantity of a stock in the user's holdings.

        Args:
            symbol (str): The stock's ticker symbol.
            quantity (int): The number of shares to remove.
        """
        if symbol not in self.current_stock_holding:
            raise ValueError(f"Stock {symbol} does not exist in holdings.")
        if quantity < 1:
            raise ValueError("Quantity must be greater than 0.")

        current_quantity, bought_price = self.current_stock_holding[symbol]
        if quantity > current_quantity:
            raise ValueError(f"Cannot remove {quantity} shares. Only {current_quantity} shares available.")

        if quantity == current_quantity:
            del self.current_stock_holding[symbol]
        else:
            self.current_stock_holding[symbol] = (current_quantity - quantity, bought_price)

        logger.info("Removed %d shares of stock %s.", quantity, symbol)

    def update_cash_balance(self, amount: float) -> None:
        """
        Updates the user's cash balance by adding or subtracting the given amount.

        Args:
            amount (float): The amount to add or subtract from the balance.
        """
        if self.cash_balance + amount < 0:
            raise ValueError("Insufficient funds.")
        self.cash_balance += amount
        logger.info("Cash balance updated by %.2f. New balance: %.2f.", amount, self.cash_balance)

    def buy_stock(self, symbol: str, quantity: int, stock_price: float) -> None:
        """
        Allows the user to buy shares of a stock.

        Args:
            symbol (str): The stock's ticker symbol.
            quantity (int): The number of shares to purchase.
            stock_price (float): The price per share of the stock.

        Raises:
            ValueError: If the quantity is less than 1, stock price is invalid, or
                        the user has insufficient funds.
        """
        if quantity < 1 or stock_price <= 0:
            raise ValueError("Quantity must be at least 1, and stock price must be positive.")
        total_cost = quantity * stock_price
        if total_cost > self.cash_balance:
            raise ValueError("Insufficient funds to buy the stock.")
        
        self.update_cash_balance(-total_cost)
        self.add_stock_to_portfolio(symbol, quantity, stock_price)
        logger.info("Bought %d shares of %s at %.2f each.", quantity, symbol, stock_price)

    def sell_stock(self, symbol: str, quantity: int, stock_price: float) -> None:
        """
        Allows the user to sell shares of a stock.

        Args:
            symbol (str): The stock's ticker symbol.
            quantity (int): The number of shares to sell.
            stock_price (float): The price per share of the stock.

        Raises:
            ValueError: If the quantity is less than 1, stock price is invalid, or
                        the user does not hold enough shares of the stock.
        """
        if quantity < 1 or stock_price <= 0:
            raise ValueError("Quantity must be at least 1, and stock price must be positive.")
        
        self.remove_stock_from_holding(symbol, quantity)
        total_revenue = quantity * stock_price
        self.update_cash_balance(total_revenue)
        logger.info("Sold %d shares of %s at %.2f each.", quantity, symbol, stock_price)

    def clear_all_stock_and_balance(self) -> None:
        """Clear all stocks and set balance to 0.0."""
        self.current_stock_holding = {}
        self.cash_balance = 0.0
        logger.info("All stock holdings cleared, and balance set to 0.")
