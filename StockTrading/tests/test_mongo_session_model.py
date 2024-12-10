import pytest

from stock_management.models.mongo_session_model import login_user, logout_user

@pytest.fixture
def sample_user_id():
    return 123  # Primary key for user

@pytest.fixture
def sample_stock_holdings():
    return {"NVDA": (10, 200.0),
            "TSLA": (20, 350.0)}


def test_login_user_creates_session_if_not_exists(mocker, sample_user_id):
    """Test login_user creates a session with no stock holdings if it does not exist."""
    mock_find = mocker.patch("stock_management.clients.mongo_client.sessions_collection.find_one", return_value=None)
    mock_insert = mocker.patch("stock_management.clients.mongo_client.sessions_collection.insert_one")
    mock_user_profile = mocker.Mock()

    login_user(sample_user_id, mock_user_profile)

    mock_find.assert_called_once_with({"user_id": sample_user_id})
    mock_insert.assert_called_once_with({"user_id": sample_user_id, "current_stock_holding": {}, "cash_balance": 0.0})
    mock_user_profile.clear_all_stock_and_balance.assert_not_called()
    mock_user_profile.add_stock_to_portfolio.assert_not_called()

def test_login_user_loads_stocks_if_session_exists(mocker, sample_user_id, sample_stock_holdings):
    """Test login_user loads stock holdings if session exists."""
    mock_find = mocker.patch(
        "stock_management.clients.mongo_client.sessions_collection.find_one",
        return_value={"user_id": sample_user_id, "current_stock_holding": sample_stock_holdings, "cash_balance": 10000.00}
    )
    mock_user_profile = mocker.Mock()

    login_user(sample_user_id, mock_user_profile)

    mock_find.assert_called_once_with({"user_id": sample_user_id})
    mock_user_profile.clear_all_stock_and_balance.assert_not_called()
    expected_calls = [mocker.call({symbol: info}) for symbol, info in sample_stock_holdings.items()]
    mock_user_profile.add_stock_to_portfolio.assert_has_calls(expected_calls)

def test_logout_user_updates_stock_holdings(mocker, sample_user_id, sample_stock_holdings):
    """Test logout_user updates the stock holdings list in the session."""
    mock_update = mocker.patch("stock_management.clients.mongo_client.sessions_collection.update_one", return_value=mocker.Mock(matched_count=1))
    
    mock_user_profile = mocker.Mock()
    mock_user_profile.get_holding_stocks.return_value = sample_stock_holdings
    mock_user_profile.get_cash_balance.return_value = 10000.0

    logout_user(sample_user_id, mock_user_profile)

    mock_update.assert_called_once_with({"user_id": sample_user_id}, {"$set": {"current_stock_holding": sample_stock_holdings, "cash_balance": 10000.0}}, upsert=False)
    mock_user_profile.clear_all_stock_and_balance.assert_called_once()

def test_logout_user_raises_value_error_if_no_user(mocker, sample_user_id, sample_stock_holdings):
    """Test logout_user raises ValueError if no session document exists."""
    mock_update = mocker.patch("stock_management.clients.mongo_client.sessions_collection.update_one", return_value=mocker.Mock(matched_count=0))
    mock_user_profile = mocker.Mock()
    mock_user_profile.get_holding_stocks.return_value = sample_stock_holdings
    mock_user_profile.get_cash_balance.return_value = 10000.0

    with pytest.raises(ValueError, match=f"User with ID {sample_user_id} not found for logout."):
        logout_user(sample_user_id, mock_user_profile)

    mock_update.assert_called_once_with({"user_id": sample_user_id}, {"$set": {"current_stock_holding": sample_stock_holdings, "cash_balance": 10000.0}}, upsert=False)