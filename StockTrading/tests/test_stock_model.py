import pytest

from stock_management.models.stock_model import (
    lookup_stock,
    get_price_details,
    fetch_historical_data
)


# --------------------------------------FIXTURES START----------------------------------------------------------------

# Fixture for successful API responses
@pytest.fixture
def mock_successful_api_response(mocker):
    """Mocks successful API responses for different Alpha Vantage functions."""

    def mock_response(url, params=None, **kwargs):
        if params['function'] == 'OVERVIEW':  # call OVERVIEW from Alpha Vantage API
            # mock response for 'lookup_stock'
            return mocker.Mock(status_code=200, json=lambda: {
                "Symbol": params['symbol'],
                "Name": "Test Company",
                "Exchange": "NASDAQ",
                "Description": "Test description",
                "PERatio": "15.5",
                "52WeekHigh": "100.0",
                "52WeekLow": "50.0"
            })
        elif params['function'] == 'GLOBAL_QUOTE':  # call GLOBAL_QUOTE from Alpha Vantage API
            # mock response for 'get_price_details'
            return mocker.Mock(status_code=200, json=lambda: {
                "Global Quote": {
                    "05. price": "90.0",
                    "09. change": "+1.5",
                    "10. change percent": "+1.65%"
                }
            })
        elif params[
            'function'] == 'TIME_SERIES_DAILY_ADJUSTED':  # call TIME_SERIES_DAILY_ADJUSTED from Alpha Vantage API
            # mock response for 'fetch_historical_data'
            return mocker.Mock(status_code=200, json=lambda: {
                "Time Series (Daily)": {
                    "2024-12-08": {
                        "1. open": "85.0",
                        "2. high": "90.0",
                        "3. low": "84.0",
                        "4. close": "89.0",
                        "6. volume": "1500000"
                    },
                    "2024-12-07": {
                        "1. open": "88.0",
                        "2. high": "90.0",
                        "3. low": "87.0",
                        "4. close": "85.0",
                        "6. volume": "1300000"
                    }
                }
            })

    return mock_response


# Fixture for invalid symbol response
@pytest.fixture
def mock_invalid_symbol_response(mocker):
    """Mocks API responses for invalid stock symbols."""

    def invalid_symbol_response(url, params=None, **kwargs):
        if params['function'] == 'OVERVIEW':
            return mocker.Mock(status_code=200, json=lambda: {})  # OVERVIEW returns empty response for invalid symbol
        elif params['function'] == 'GLOBAL_QUOTE':
            return mocker.Mock(status_code=200, json=lambda: {
                "Global Quote": {}})  # GLOBAL QUOTE returns empty Global Quote for invalid symbol
        elif params['function'] == 'TIME_SERIES_DAILY_ADJUSTED':
            return mocker.Mock(status_code=200, json=lambda: {
                "Error Message": "Invalid API call. Please retry or visit the documentation for valid API endpoints."
                # TIME_SERIES_DAILY_ADJUSTED returns this error message for invalid symbol
            })

    return invalid_symbol_response


# Fixture for faulty API connection
@pytest.fixture
def mock_faulty_api_response(mocker):
    """Mocks API responses for faulty API connections."""

    def faulty_response(url, params=None, **kwargs):
        return mocker.Mock(status_code=500, json=lambda: {})  # Simulate server error

    return faulty_response


# --------------------------------------FIXTURES END----------------------------------------------------------------


# ---------------------------------------- lookup_stock tests -----------------------------------------------------
def test_successful_lookup_stock(mocker, mock_successful_api_response):
    """Tests successful lookup of stock"""

    mocker.patch('requests.get', side_effect=mock_successful_api_response)

    result = lookup_stock("GOOGL")

    assert result['Symbol'] == "GOOGL"
    assert result['Name'] == "Test Company"
    assert result['Exchange'] == "NASDAQ"
    assert result['Description'] == "Test description"
    assert result['P/E Ratio'] == "15.5"
    assert result['52 Week High'] == "100.0"
    assert result['52 Week Low'] == "50.0"


def test_lookup_stock_invalid_symbol(mocker, mock_invalid_symbol_response):
    """Tests failed lookup of stock because of invalid symbol raises ValueError"""

    mocker.patch('requests.get', side_effect=mock_invalid_symbol_response)

    with pytest.raises(ValueError, match="The stock symbol: INVALID is invalid"):
        lookup_stock("INVALID")


def test_lookup_stock_faulty_API(mocker, mock_faulty_api_response):
    """Tests failed lookup of stock because of faulty API connection raises Exception"""

    mocker.patch('requests.get', side_effect=mock_faulty_api_response)

    with pytest.raises(Exception, match="API request failed with status code 500"):
        lookup_stock("GOOGL")


# ---------------------------------------------------get_price_details tests ------------------------------------------------------
def test_successful_get_price_details(mocker, mock_successful_api_response):
    """Tests successful retrieval of price details of a stock"""

    mocker.patch('requests.get', side_effect=mock_successful_api_response)

    result = get_price_details("AMZN")

    assert result['Current Price'] == "90.0"
    assert result['Price Change'] == "+1.5"
    assert result['Change Percentage'] == "+1.65%"


def test_get_price_details_invalid_symbol(mocker, mock_invalid_symbol_response):
    """Tests failed retrieval of price details of a stock because of invalid symbol raises ValueError"""

    mocker.patch('requests.get', side_effect=mock_invalid_symbol_response)

    with pytest.raises(ValueError, match="The stock symbol: INVALID is invalid"):
        get_price_details("INVALID")


def test_get_price_details_faulty_API(mocker, mock_faulty_api_response):
    """Tests failed retrieval of price details of a stock because of faulty API connection raises Exception"""

    mocker.patch('requests.get', side_effect=mock_faulty_api_response)

    with pytest.raises(Exception, match="API request failed with status code 500"):
        get_price_details("AMZN")


# ----------------------------------------------------- fetch_historical_data tests -------------------------------------------------
def test_successful_fetch_historical_data(mocker, mock_successful_api_response):
    """Tests successful fetching of historical data of a stock"""

    mocker.patch('requests.get', side_effect=mock_successful_api_response)

    result = fetch_historical_data("NVDA", "2024-12-07", "2024-12-08")

    assert len(result) == 2  # length of list must be 2 since we have 2 entries

    # first entry of list (2024-12-08)
    assert result[0]['date'] == "2024-12-08"
    assert result[0]['open'] == "85.0"
    assert result[0]['high'] == "90.0"
    assert result[0]['low'] == "84.0"
    assert result[0]['close'] == "89.0"
    assert result[0]['volume'] == "1500000"

    # second entry of list (2024-12-07)
    assert result[1]['date'] == "2024-12-07"
    assert result[1]['open'] == "88.0"
    assert result[1]['high'] == "90.0"
    assert result[1]['low'] == "87.0"
    assert result[1]['close'] == "85.0"
    assert result[1]['volume'] == "1300000"


def test_fetch_historical_data_invalid_date_format(mocker):
    """Tests failed fetching of historical data of a stock because of invalid date format raises ValueError before it makes a call to the Alpha Vantage API"""
    # we mock requests.get to ensure it is never called, although the error is raised before making a call
    mock_requests = mocker.patch('requests.get')

    with pytest.raises(ValueError, match="The date format you provided is invalid. Please use 'YYYY-MM-DD'."):
        fetch_historical_data("NVDA", "INVALID_DATE", "2024-12-08")

    # make sure that the API was indeed never called
    mock_requests.assert_not_called()


def test_fetch_historical_data_invalid_symbol(mocker, mock_invalid_symbol_response):
    """Tests failed fetching of historical data of a stock because of invalid symbol raises ValueError"""

    mocker.patch('requests.get', side_effect=mock_invalid_symbol_response)

    with pytest.raises(ValueError, match="The stock symbol: INVALID is invalid. Please check the symbol again."):
        fetch_historical_data("INVALID", "2024-12-07", "2024-12-08")


def test_fetch_historical_data_out_of_range(mocker, mock_successful_api_response):
    """Tests that trying to fetch historical data out of range returns empty list"""

    mocker.patch('requests.get', side_effect=mock_successful_api_response)

    result = fetch_historical_data("NVDA", "2024-12-10", "2024-12-15")
    assert len(result) == 0  # no data exist for these date so empty list should be returned


def test_fetch_historical_data_no_data_found(mocker):
    """Tests that if no historical data is found for the given symbol or date range a ValueError is raised"""

    mocker.patch('requests.get', return_value=mocker.Mock(status_code=200, json=lambda: {"Time Series (Daily)": {}}))

    with pytest.raises(ValueError, match="No historical data found for the stock symbol: NVDA."):
        fetch_historical_data("NVDA", "2024-12-01", "2024-12-07")


def test_fetch_historical_data_faulty_API(mocker, mock_faulty_api_response):
    """Tests failed fetching of historical data of a stock because of faulty API connection raises Exception"""

    mocker.patch('requests.get', side_effect=mock_faulty_api_response)

    with pytest.raises(Exception, match="API request failed with status code 500"):
        fetch_historical_data("AAPL", "2024-12-01", "2024-12-07")
