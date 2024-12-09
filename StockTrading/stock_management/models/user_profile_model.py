
import logging
from typing import Dict, List
import sqlite3
from stock_management.utils.logger import configure_logger
from stock_management.utils.sql_utils import get_db_connection

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
   
        


    def __init__(self, cash_balance=0):
        """
        Initializes the UserProfile with the given user details, an empty stock holding,
        and an empty liked stock list.

        Args:
            user_id (int): The unique identifier for the user.
            username (str): The user's name.
            cash_balance (float): The user's starting cash balance. Defaults to 0.0.
        """

        self.cash_balance = cash_balance
        
        if self.cash_balance < 0:
            raise ValueError("Cash balance must be non-negative")

        self.user_id = 0
        self.username = ""
        self.current_stock_holding: Dict[str, int] = {}

    def get_portfolio(user_id: int) -> Dict[str, int]:
        """
        Retrieves the user's current stock portfolio.

        Args:
            user_id (int): The ID of the user whose portfolio is being retrieved.

        Returns:
            Dict[str, int]: A dictionary containing stock symbols and the quantities
            that the user holds for each stock.
         """
        try:
        # Assuming you have a function get_db_connection() that returns a database connection
         with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT stock_symbol, quantity 
                    FROM portfolio 
                    WHERE user_id = ? AND deleted = 0
                """, (user_id,))
            
                rows = cursor.fetchall()
            
                if not rows:
                    logger.info("No portfolio found for user ID %s", user_id)
                    return {}
            
                portfolio = {row[0]: row[1] for row in rows}
                logger.info("Retrieved portfolio for user ID %s: %s", user_id, portfolio)
                return portfolio

        except sqlite3.Error as e:
            logger.error("Database error: %s", str(e))
            raise e

    def add_stock_to_portfolio(user_id: int, symbol: str, quantity: int) -> None:
        """
        Adds a stock to the user's holdings or updates the quantity if it already exists.
        This method is used when the user buys a new stock.

        Args:
            user_id (int): The ID of the user whose portfolio is being updated.
            symbol (str): The stock's ticker symbol.
            quantity (int): The number of shares to add.
        """
        try:
            if quantity <= 0:
                raise ValueError("Quantity must be greater than 0.")

            with get_db_connection() as conn:
                cursor = conn.cursor()
            
                # Check if the stock already exists in the user's portfolio
                cursor.execute("""
                    SELECT quantity 
                    FROM portfolio 
                    WHERE user_id = ? AND stock_symbol = ? AND deleted = 0
                """, (user_id, symbol))
            
                row = cursor.fetchone()
            
                if row:
                    # Update the quantity if the stock already exists
                    new_quantity = row[0] + quantity
                    cursor.execute("""
                        UPDATE portfolio 
                        SET quantity = ? 
                        WHERE user_id = ? AND stock_symbol = ? AND deleted = 0
                    """, (new_quantity, user_id, symbol))
                    logger.info("Updated stock %s for user ID %s. New quantity: %s", symbol, user_id, new_quantity)
                else:
                    # Insert a new stock entry if it doesn't exist
                    cursor.execute("""
                        INSERT INTO portfolio (user_id, stock_symbol, quantity, deleted)
                        VALUES (?, ?, ?, 0)
                    """, (user_id, symbol, quantity))
                    logger.info("Added stock %s for user ID %s with quantity: %s", symbol, user_id, quantity)
            
                conn.commit()

        except sqlite3.Error as e:
            logger.error("Database error while adding stock: %s", str(e))
            raise e
        except ValueError as ve:
            logger.error("Value error: %s", str(ve))
            raise ve


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
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Get all holdings
                cursor.execute("SELECT stock_symbol, quantity FROM portfolio WHERE user_id = ? AND deleted = 0", (self.user_id,))
                holdings = cursor.fetchall()
            
                total_earnings = 0.0

                for symbol, quantity in holdings:
                    # Get today's and yesterday's stock prices
                    today_price = self.get_stock_price(symbol, "today")
                    yesterday_price = self.get_stock_price(symbol, "yesterday")

                    # Calculate earnings
                    total_earnings += (today_price - yesterday_price) * quantity

                return total_earnings

        except Exception as e:
            logger.error("Error calculating today's earnings: %s", str(e))
            raise e
    

    def remove_stock_from_holding(self, symbol: str, quantity: int) -> None:
        """
        Removes or reduces the quantity of a stock in the user's holdings.
        This method is used when the user sells of the stock in the holdings.

        Args:
            symbol (str): The stock's ticker symbol.
            quantity (int): The number of shares to remove.
        """
        try:
            if quantity < 1:
                raise ValueError("Quantity must be greater than 0.")

            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Check if the stock exists
                cursor.execute("SELECT quantity FROM portfolio WHERE user_id = ? AND stock_symbol = ? AND deleted = 0", (self.user_id, symbol))
                row = cursor.fetchone()

                if not row:
                    raise ValueError(f"Stock {symbol} does not exist in holdings.")
            
                current_quantity = row[0]

                if quantity > current_quantity:
                    raise ValueError(f"Cannot remove {quantity} shares. Only {current_quantity} shares available.")

                if quantity == current_quantity:
                    # Remove the stock completely
                    cursor.execute("UPDATE portfolio SET deleted = 1 WHERE user_id = ? AND stock_symbol = ?", (self.user_id, symbol))
                else:
                    # Reduce the quantity
                    cursor.execute("UPDATE portfolio SET quantity = quantity - ? WHERE user_id = ? AND stock_symbol = ?", (quantity, self.user_id, symbol))

                conn.commit()

        except Exception as e:
            logger.error("Error removing stock: %s", str(e))
            raise e

    def update_cash_balance(self, amount: float) -> None:
        """
        Updates the user's cash balance by adding or subtracting the given amount.
        Corresponds to the situation when the user retrieves and add money into the
        account.

        Args:
            amount (float): The amount to add or subtract from the balance.
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Update the cash balance
                cursor.execute("UPDATE users SET cash_balance = cash_balance + ? WHERE id = ?", (amount, self.user_id))
                conn.commit()

        except Exception as e:
            logger.error("Error updating cash balance: %s", str(e))
            raise e

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
        try:
            if quantity < 1:
                raise ValueError("Quantity must be at least 1.")

            # Get stock price
            stock_price = self.get_stock_price(symbol)

            # Calculate total cost
            total_cost = stock_price * quantity

            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Check user cash balance
                cursor.execute("SELECT cash_balance FROM users WHERE id = ?", (self.user_id,))
                row = cursor.fetchone()

                if not row or row[0] < total_cost:
                    raise ValueError("Insufficient funds to buy the stock.")

                # Deduct from cash balance
                cursor.execute("UPDATE users SET cash_balance = cash_balance - ? WHERE id = ?", (total_cost, self.user_id))

                # Add stock to portfolio
                self.add_stock_to_portfolio(self.user_id, symbol, quantity)

                conn.commit()

        except Exception as e:
            logger.error("Error buying stock: %s", str(e))
            raise e


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
        try:
            if quantity < 1:
                raise ValueError("Quantity must be at least 1.")

            # Get stock price
            stock_price = self.get_stock_price(symbol)

            # Calculate total revenue
            total_revenue = stock_price * quantity

            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Check if the stock exists
                cursor.execute("SELECT quantity FROM portfolio WHERE user_id = ? AND stock_symbol = ? AND deleted = 0", (self.user_id, symbol))
                row = cursor.fetchone()

                if not row or row[0] < quantity:
                    raise ValueError("Not enough shares to sell.")

                # Reduce stock quantity
                self.remove_stock_from_holding(symbol, quantity)

                # Add to cash balance
                cursor.execute("UPDATE users SET cash_balance = cash_balance + ? WHERE id = ?", (total_revenue, self.user_id))

                conn.commit()

        except Exception as e:
            logger.error("Error selling stock: %s", str(e))
            raise e

    def clear_all_stock(self) -> None:
        """
        Clear all stocks
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Mark all stocks as deleted
                cursor.execute("UPDATE portfolio SET deleted = 1 WHERE user_id = ?", (self.user_id,))
                conn.commit()

        except Exception as e:
            logger.error("Error clearing all stocks: %s", str(e))
            raise e