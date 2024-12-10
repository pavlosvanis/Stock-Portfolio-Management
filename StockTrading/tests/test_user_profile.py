import pytest
from stock_management.models.user_profile_model import UserProfile


@pytest.fixture
def mock_user():
    """
    Fixture to provide a mock UserProfile instance for testing.
    """
    return UserProfile(user_id=1, username="test_user", cash_balance=1000.0)


##########################################################
# Portfolio Management
##########################################################

def test_get_portfolio(mock_user):
    """
    Test getting the user's stock portfolio.
    """
    mock_user.current_stock_holding = {"AAPL": 10, "TSLA": 5}
    portfolio = mock_user.get_portfolio()
    
    assert portfolio == {"AAPL": 10, "TSLA": 5}, "Portfolio does not match expected values."


def test_add_stock_to_holding(mock_user):
    """
    Test adding stock to the user's holdings.
    """
    mock_user.current_stock_holding = {"AAPL": 10}
    mock_user.add_stock_to_holding("AAPL", 5)
    mock_user.add_stock_to_holding("TSLA", 8)
    
    assert mock_user.current_stock_holding == {"AAPL": 15, "TSLA": 8}, "Stock holdings not updated correctly."


def test_remove_stock_from_holding(mock_user):
    """
    Test removing or reducing stock quantity from the user's holdings.
    """
    mock_user.current_stock_holding = {"AAPL": 10}
    
    mock_user.remove_stock_from_holding("AAPL", 5)
    assert mock_user.current_stock_holding == {"AAPL": 5}, "Stock quantity not reduced correctly."
    
    mock_user.remove_stock_from_holding("AAPL", 5)
    assert "AAPL" not in mock_user.current_stock_holding, "Stock not removed when quantity reaches zero."
    
    with pytest.raises(ValueError):
        mock_user.remove_stock_from_holding("AAPL", 1)


##########################################################
# Cash Management
##########################################################

def test_update_cash_balance(mock_user):
    """
    Test updating the user's cash balance.
    """
    mock_user.update_cash_balance(500)
    assert mock_user.cash_balance == 500, "Cash balance not updated correctly."

    mock_user.update_cash_balance(-100)
    assert mock_user.cash_balance == 400, "Cash balance not subtracted correctly."


##########################################################
# Stock Trading
##########################################################

def test_buy_stock(mock_user, mocker):
    """
    Test buying shares of a stock.
    """
    mock_user.cash_balance = 1000.0
    mock_stock_price_api = mocker.patch("stock_management.api.get_stock_price", return_value=50)

    mock_user.buy_stock("AAPL", 10)

    assert mock_user.current_stock_holding["AAPL"] == 10, "Stock not added correctly."
    assert mock_user.cash_balance == 500.0, "Cash balance not updated correctly."
    mock_stock_price_api.assert_called_once_with("AAPL")


def test_sell_stock(mock_user, mocker):
    """
    Test selling shares of a stock.
    """
    mock_user.current_stock_holding = {"AAPL": 10}
    mock_user.cash_balance = 100.0
    mock_stock_price_api = mocker.patch("stock_management.api.get_stock_price", return_value=50)

    mock_user.sell_stock("AAPL", 5)

    assert mock_user.current_stock_holding["AAPL"] == 5, "Stock quantity not updated correctly."
    assert mock_user.cash_balance == 350.0, "Cash balance not updated correctly."


def test_sell_stock_insufficient_shares(mock_user):
    """
    Test error when attempting to sell more shares than the user holds.
    """
    mock_user.current_stock_holding = {"AAPL": 2}

    with pytest.raises(ValueError):
        mock_user.sell_stock("AAPL", 5)


def test_buy_stock_insufficient_funds(mock_user, mocker):
    """
    Test error when attempting to buy stock with insufficient funds.
    """
    mock_user.cash_balance = 100.0
    mocker.patch("stock_management.api.get_stock_price", return_value=50)

    with pytest.raises(ValueError):
        mock_user.buy_stock("AAPL", 3)


##########################################################
# Database Updates
##########################################################

def test_buy_stock_updates_database(mock_user, mocker):
    """
    Test that buying stock updates the database with the correct stock symbol and quantity.
    """
    mock_user.cash_balance = 1000.0
    mocker.patch("stock_management.api.get_stock_price", return_value=50)

    mock_user.update_database = mocker.MagicMock()
    mock_user.buy_stock("AAPL", 10)

    mock_user.update_database.assert_called_once_with("AAPL", 10)


def test_sell_stock_updates_database(mock_user, mocker):
    """
    Test that selling stock updates the database by removing the stock or reducing its quantity.
    """
    mock_user.current_stock_holding = {"AAPL": 10}
    mocker.patch("stock_management.api.get_stock_price", return_value=50)

    mock_user.update_database = mocker.MagicMock()
    mock_user.sell_stock("AAPL", 5)

    mock_user.update_database.assert_called_once_with("AAPL", 5)
