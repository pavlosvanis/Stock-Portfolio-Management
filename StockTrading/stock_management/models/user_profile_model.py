import logging
from typing import Dict, Tuple, Any
from stock_management.models.stock_model import get_price_details, lookup_stock

logger = logging.getLogger(__name__)

class UserProfile:
    """
    A class to manage a user's profile, including cash balance, stock holdings,
    and their liked stock list.
    """

    def __init__(self, cash_balance: float = 0.0):
        """
        Initializes the UserProfile with the given user details, an empty stock holding,
        and an empty liked stock list.
        """
        if cash_balance < 0:
            raise ValueError("Cash balance must be positive")
        
        self.user_id = None
        self.username = ""
        self.cash_balance = cash_balance
        # Dict[<symbol>, (<quantity>, <bought_price>)]
        self.current_stock_holding: Dict[str, Tuple[int, float]] = {}

    def get_holding_stocks(self) -> Dict[str, Tuple[int, float]]:
        """Returns the user's current stock holdings."""
        return self.current_stock_holding

    def get_cash_balance(self) -> float:
        """Returns the user's current cash balance."""
        return self.cash_balance
    
    def get_portfolio(self) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed information about the user's current stock portfolio.

        Returns:
            Dict[str, Dict[str, Any]]: A dictionary where each key is a stock symbol and the value is
            another dictionary containing the stock's quantity, average purchase price, current market price,
            and additional details such as P/E ratio, 52-week high, 52-week low, and company description that
            are included in the lookup_stock method in stock_model.
        """
        portfolio = {}
        for symbol, (quantity, bought_price) in self.current_stock_holding.items():
            try:
                price_details = get_price_details(symbol)
                current_price = float(price_details.get('Current Price', 0.0))
            
                stock_details = lookup_stock(symbol)
                pe_ratio = stock_details.get('P/E Ratio', "N/A")
                week_high = stock_details.get('52 Week High', "N/A")
                week_low = stock_details.get('52 Week Low', "N/A")
                description = stock_details.get('Description', "N/A")
                exchange = stock_details.get('Exchange', "N/A")
                name = stock_details.get('Name', "N/A")

                portfolio[symbol] = {
                    "quantity": quantity,
                    "average_purchase_price": bought_price,
                    "current_market_price": current_price,
                    "P/E Ratio": pe_ratio,
                    "52 Week High": week_high,
                    "52 Week Low": week_low,
                    "Company Description": description,
                    "Exchange": exchange,
                    "Name": name
                }
            except Exception as e:
                logger.warning("Failed to fetch details for stock %s: %s", symbol, str(e))
                raise e

        return portfolio

    def get_current_total_values(self) -> Dict[str, float]:
        """
        Calculates the current total value of the user's portfolio and the balance.

        Returns:
            Dict[str, float]: A dictionary containing the total value of stocks, cash balance, and overall total value.
        """
        total_stock_value = 0.0
        for symbol, (quantity, _) in self.current_stock_holding.items():
            try:
                stock_details = get_price_details(symbol)
                current_price = float(stock_details.get('Current Price', 0.0))
                total_stock_value += quantity * current_price
            except Exception as e:
                logger.warning("Failed to get current price for stock %s: %s", symbol, str(e))
                raise e

        total_value = total_stock_value + self.cash_balance
        logger.info("Portfolio values: Stocks: %.2f, Cash: %.2f, Total: %.2f", total_stock_value, self.cash_balance, total_value)
        return {
            "total_stock_value": total_stock_value,
            "cash_balance": self.cash_balance,
            "total_portfolio_value": total_value
        }

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

    def buy_stock(self, symbol: str, quantity: int) -> None:
        """
        Allows the user to buy shares of a stock.

        Args:
            symbol (str): The stock's symbol.
            quantity (int): The number of shares to purchase.

        Raises:
            ValueError: If the quantity is less than 1, the stock symbol is invalid, or
                        the user has insufficient funds.
        """
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")
    
        try:
            stock_details = get_price_details(symbol)
            stock_price = float(stock_details.get("Current Price", 0.0))

            if stock_price <= 0:
                raise ValueError(f"Invalid stock price retrieved for {symbol}: {stock_price}")
        
            total_cost = quantity * stock_price
            if total_cost > self.cash_balance:
                raise ValueError("Insufficient funds to buy the stock.")

            self.update_cash_balance(-total_cost)

            # Change average price
            if symbol in self.current_stock_holding:
                current_quantity, average_price = self.current_stock_holding[symbol]
                new_quantity = current_quantity + quantity
                new_average_price = ((current_quantity * average_price) + (quantity * stock_price)) / new_quantity
                self.current_stock_holding[symbol] = (new_quantity, new_average_price)
            else:
                self.current_stock_holding[symbol] = (quantity, stock_price)
            
            self.add_stock_to_portfolio(symbol, quantity, stock_price)
            logger.info("Bought %d shares of %s at the price of %.2f. Total cost: %.2f.", quantity, symbol, stock_price, total_cost)

        except ValueError as vale:
            logger.error("Error buying %s: %s", symbol, str(vale))
            raise vale
        except Exception as e:
            logger.error("Unexpected error while buying %s: %s", symbol, str(e))
            raise e

    def sell_stock(self, symbol: str, quantity: int) -> None:
        """
        Allows the user to sell shares of a stock.

        Args:
            symbol (str): The stock's symbol.
            quantity (int): The number of shares to sell.

        Raises:
            ValueError: If the quantity is less than 1, the stock symbol is invalid, or
                        the user does not hold enough shares of the stock.
        """
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")
    
        try:
            stock_details = get_price_details(symbol)
            stock_price = float(stock_details.get("Current Price", 0.0))
        
            # Sell process
            self.remove_stock_from_holding(symbol, quantity)
            total_sold = quantity * stock_price
            self.update_cash_balance(total_sold)
            logger.info("Succesfully sold %d shares of %s at the price of %.2f. Total values sold: %.2f.", quantity, symbol, stock_price, total_sold)

        except ValueError as vale:
            logger.error("Error selling stock %s: %s", symbol, str(vale))
            raise vale
        except Exception as e:
            logger.error("Unexpected error while selling stock %s: %s", symbol, str(e))
            raise e


    def clear_all_stock_and_balance(self) -> None:
        """Clear all stocks and set balance to 0.0."""
        self.current_stock_holding = {}
        self.cash_balance = 0.0
        logger.info("All stock holdings cleared, and balance set to 0.")