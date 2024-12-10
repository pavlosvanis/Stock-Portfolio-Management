import pytest
from stock_management.models.user_profile_model import UserProfile
from stock_management.models.stock_model import get_price_details, lookup_stock
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_user():
    """
    Fixture to provide a mock UserProfile instance for testing.
    """
    user_profile_model = UserProfile(cash_balance=1000.0)
    user_profile_model.user_id = 1
    user_profile_model.username = "test_user"
    user_profile_model.current_stock_holding = {
        "NVDA": (10, 150.0)  # 10 shares with an average price of $150.0
    }
    return user_profile_model

@pytest.fixture
def mock_get_price_details(mocker):
    """
    Mock the get_price_details function.
    """
    return mocker.patch("stock_management.models.user_profile_model.get_price_details", return_value={
        "Current Price": "200.0"
    })

@pytest.fixture
def mock_lookup_stock(mocker):
    """
    Mock the lookup_stock function.
    """
    return mocker.patch("stock_management.models.user_profile_model.lookup_stock", return_value={
        "P/E Ratio": "15.0",
        "52 Week High": "250.0",
        "52 Week Low": "100.0",
        "Description": "Test Company",
        "Exchange": "NASDAQ",
        "Name": "NVIDIA Corp."
    })

##########################################################
# Portfolio Management
##########################################################
def test_get_holding_stocks(mock_user):
    """
    Test the get_holding_stocks method
    """
    expected_holdings = { "NVDA": (10, 150.0) }

    holdings = mock_user.get_holding_stocks()
    assert holdings == expected_holdings


def test_get_cash_balance(mock_user):
    """
    Test the get_cash_balance method
    """
    expected_balance = 1000.0
    balance = mock_user.get_cash_balance()
    assert balance == expected_balance

def test_get_portfolio(mock_user, mock_get_price_details, mock_lookup_stock):
    """
    Test getting the user's stock portfolio.
    """

    portfolio = mock_user.get_portfolio()
    assert portfolio["NVDA"]["quantity"] == 10
    assert portfolio["NVDA"]["average_purchase_price"] == 150.0
    assert portfolio["NVDA"]["current_market_price"] == 200.0
    assert portfolio["NVDA"]["P/E Ratio"] == "15.0"
    assert portfolio["NVDA"]["52 Week High"] == "250.0"
    assert portfolio["NVDA"]["52 Week Low"] == "100.0"
    assert portfolio["NVDA"]["Company Description"] == "Test Company"
    assert portfolio["NVDA"]["Exchange"] == "NASDAQ"
    assert portfolio["NVDA"]["Name"] == "NVIDIA Corp."

    mock_get_price_details.assert_called_once_with("NVDA")
    mock_lookup_stock.assert_called_once_with("NVDA")

def test_get_current_total_values(mock_user, mock_get_price_details):
    """
    Test calculating the user's current total portfolio value.
    """
    total_values = mock_user.get_current_total_values()


    assert total_values["total_stock_value"] == 2000.0
    assert total_values["cash_balance"] == 1000.0
    assert total_values["total_portfolio_value"] == 3000.0

    mock_get_price_details.assert_called_once_with("NVDA")


def test_add_stock_to_portfolio(mock_user):
    """
    Test adding stock to the portfolio.
    """
    mock_user.add_stock_to_portfolio("NVDA", 5, 180.0)
    assert mock_user.current_stock_holding["NVDA"] == (15, 160.0)

    mock_user.add_stock_to_portfolio("TSLA", 10, 300.0)
    assert mock_user.current_stock_holding["TSLA"] == (10, 300.0)


def test_remove_stock_from_holding(mock_user):
    """
    Test removing stock from the user's holdings.
    """
    mock_user.remove_stock_from_holding("NVDA", 5)
    assert mock_user.current_stock_holding["NVDA"] == (5, 150.0)

    mock_user.remove_stock_from_holding("NVDA", 5)
    assert "NVDA" not in mock_user.current_stock_holding

    with pytest.raises(ValueError):
        mock_user.remove_stock_from_holding("NVDA", 1)

def test_update_cash_balance(mock_user):
    """
    Test updating the user's cash balance.
    """
    mock_user.update_cash_balance(500)
    assert mock_user.cash_balance == 1500.0

    mock_user.update_cash_balance(-200)
    assert mock_user.cash_balance == 1300.0

    with pytest.raises(ValueError):
        mock_user.update_cash_balance(-2000)

def test_clear_all_stock_and_balance(mock_user):
    """
    Test clearing all stock holdings and balance.
    """
    mock_user.clear_all_stock_and_balance()
    assert mock_user.current_stock_holding == {}
    assert mock_user.cash_balance == 0.0


##########################################################
# Stock Trading
##########################################################

def test_buy_stock(mock_user, mock_get_price_details):
    """
    Test buying shares of a stock.
    """
    mock_user.buy_stock("NVDA", 5)

    assert mock_user.current_stock_holding["NVDA"] == (15, 2500/15)
    assert mock_user.cash_balance == 0.0

    mock_get_price_details.assert_called_once_with("NVDA")

def test_buy_stock_insufficient_balance(mock_user, mock_get_price_details):
    """
    Test buying shares of a stock with insufficient funds.
    """

    mock_user.cash_balance = 500.0

    with pytest.raises(ValueError, match="Insufficient funds to buy the stock."):
        mock_user.buy_stock("NVDA", 5)

    assert mock_user.current_stock_holding["NVDA"] == (10, 150.0)
    assert mock_user.cash_balance == 500.0

    mock_get_price_details.assert_called_once_with("NVDA")


def test_sell_stock(mock_user, mock_get_price_details):
    """
    Test selling shares of a stock.
    """
    mock_user.sell_stock("NVDA", 5)

    assert mock_user.current_stock_holding["NVDA"] == (5, 150.0)
    assert mock_user.cash_balance == 2000.0

    mock_get_price_details.assert_called_once_with("NVDA")


def test_sell_stock_insufficient_shares(mock_user):
    """
    Test error when selling more shares than available.
    """
    with pytest.raises(ValueError):
        mock_user.sell_stock("NVDA", 20)


def test_buy_stock_insufficient_funds(mock_user, mock_get_price_details):
    """
    Test error when buying stock with insufficient funds.
    """
    mock_user.cash_balance = 100.0

    with pytest.raises(ValueError):
        mock_user.buy_stock("NVDA", 5)
