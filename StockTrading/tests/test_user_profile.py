from contextlib import contextmanager
import re
import sqlite3

import pytest

from stock_management.models.user_profile_model import UserProfile

######################################################
#
#    Fixtures
#
######################################################
@pytest.fixture
def mock_stock_price_api(mocker):
    # Mock the function or API call that fetches stock prices
    mock_response = mocker.patch("module_name.get_stock_price")
    mock_response.return_value = 150  # Set a fixed price for testing
    return mock_response

@pytest.fixture
def mock_user():
    """
    Fixture to provide a mock UserProfile instance for testing.
    """
    return UserProfile(user_id=1, username="test_user", cash_balance=1000.0)


######################################################
#
#    Tests for Portfolio Management
#
######################################################

def test_get_portfolio(mock_user):
    """
    Test getting the user's stock portfolio.

    Ensures the portfolio contains the correct stock symbols, and its corresponding 
    quantities, and current prices.

    Raises:
        AssertionError: If the portfolio does not match the expected structure or values.
    """
    mock_user.current_stock_holding = {"AAPL": 10, "TSLA": 5}
    portfolio = mock_user.get_portfolio()
    
    assert portfolio == {"AAPL": 10, "TSLA": 5}, "Portfolio does not match expected values"


def test_add_stock_to_holding(mock_user):
    """
    Test adding stock to the user's holdings.

    Ensures the stock is added correctly or its quantity is updated if it already exists.

    Raises:
        AssertionError: If the stock holding is not updated correctly.
    """
    mock_user.current_stock_holding = {"AAPL": 10}
    mock_user.add_stock_to_holding("AAPL", 5)
    mock_user.add_stock_to_holding("TSLA", 8)
    
    assert mock_user.current_stock_holding == {"AAPL": 15, "TSLA": 8}, "Stock holdings not updated correctly"


def test_remove_stock_from_holding(mock_user):
    """
    Test removing or reducing stock quantity from the user's holdings.

    Ensures the stock is removed or its quantity is updated correctly.

    Raises:
        ValueError: If the stock does not exist or the quantity to remove is invalid.
        AssertionError: If the stock holding is not updated correctly.
    """
    mock_user.current_stock_holding = {"AAPL": 10}
    
    mock_user.remove_stock_from_holding("AAPL", 5)
    assert mock_user.current_stock_holding == {"AAPL": 5}, "Stock quantity not reduced correctly"
    
    mock_user.remove_stock_from_holding("AAPL", 5)
    assert "AAPL" not in mock_user.current_stock_holding, "Stock not removed when quantity reaches zero"
    
    with pytest.raises(ValueError):
        mock_user.remove_stock_from_holding("AAPL", 1)


def test_get_today_earnings_to_holding(mock_user):
    """
    Test calculating today's earnings from stock holdings.

    Ensures the earnings calculation is accurate based on the price changes of the stocks.

    Raises:
        AssertionError: If the calculated earnings do not match the expected value.
        Exception: If there is an issue retrieving stock prices or performing calculations.
    """
    mock_user.current_stock_holding = {"AAPL": 10}
    mock_stock_price_api.return_value = 200  # Mock today's stock price

    earnings = mock_user.get_today_earnings_to_holding()
    assert earnings == (200 - 150) * 10, "Earnings calculation is incorrect."


######################################################
#
#    Tests for Cash Management
#
######################################################

def test_update_cash_balance(mock_user):
    """
    Test updating the user's cash balance.

    Ensures the cash balance is updated correctly when adding or subtracting funds.

    Raises:
        AssertionError: If the cash balance does not match the expected value.
    """
    mock_user.update_cash_balance(500)
    assert mock_user.cash_balance == 500, "Cash balance not updated correctly."

    mock_user.update_cash_balance(-100)
    assert mock_user.cash_balance == 400, "Cash balance not subtracted correctly."


######################################################
#
#    Tests for Stock Trading
#
######################################################

def test_buy_stock(mock_user):
    """
    Test buying shares of a stock.

    Ensures the stock is added to the portfolio, and the cash balance is reduced by the total cost.

    Raises:
        ValueError: If the quantity is less than 1, the stock symbol is invalid, or funds are insufficient.
        AssertionError: If the portfolio or cash balance is not updated correctly.
    """
    mock_user.cash_balance = 1000.0
    mock_stock_price_api.return_value = 50  # Mock stock price

    mock_user.buy_stock("AAPL", 10)

    assert mock_user.current_stock_holding["AAPL"] == 10, "Stock not added correctly."
    assert mock_user.cash_balance == 500.0, "Cash balance not updated correctly."
    mock_stock_price_api.assert_called_once_with("AAPL")


def test_sell_stock(mock_user):
    """
    Test selling shares of a stock.

    Ensures the stock is removed or its quantity reduced in the portfolio, and the cash balance is increased by the revenue.

    Raises:
        ValueError: If the quantity is less than 1, the stock symbol is invalid, or shares are insufficient.
        AssertionError: If the portfolio or cash balance is not updated correctly.
    """
    mock_user.current_stock_holding = {"AAPL": 10}
    mock_user.cash_balance = 100.0
    mock_stock_price_api.return_value = 50  # Mock stock price

    mock_user.sell_stock("AAPL", 5)

    assert mock_user.current_stock_holding["AAPL"] == 5, "Stock quantity not updated correctly."
    assert mock_user.cash_balance == 350.0, "Cash balance not updated correctly."


def test_sell_stock_insufficient_shares(mock_user):
    """
    Test error when attempting to sell more shares than the user holds.

    Ensures a ValueError is raised when the user does not hold enough shares to sell.

    Raises:
        ValueError: If the stock quantity is insufficient for the sale.
    """
    mock_user.current_stock_holding = {"AAPL": 2}

    with pytest.raises(ValueError):
        mock_user.sell_stock("AAPL", 5)


def test_buy_stock_insufficient_funds(mock_user):
    """
    Test error when attempting to buy stock with insufficient funds.

    Ensures a ValueError is raised when the user does not have enough cash to complete the transaction.

    Raises:
        ValueError: If the user's cash balance is insufficient for the purchase.
    """
    mock_user.cash_balance = 100.0
    mock_stock_price_api.return_value = 50  # Mock stock price

    with pytest.raises(ValueError):
        mock_user.buy_stock("AAPL", 3)


######################################################
#
#    Utility Tests
#
######################################################

def test_buy_stock_updates_database(mock_user):
    """
    Test that buying stock updates the database with the correct stock symbol and quantity.

    Verifies that the stock is added or its quantity is updated correctly in the database.

    Raises:
        AssertionError: If the database is not updated correctly.
    """
    pass


def test_sell_stock_updates_database(mock_user):
    """
    Test that selling stock updates the database by removing the stock or reducing its quantity.

    Verifies that the database is updated correctly after the sale.

    Raises:
        AssertionError: If the database is not updated correctly.
    """
    pass