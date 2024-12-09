# CS411FinalProject

### Lookup Stock

**Description**:

Retrieves detailed information about a specific stock using its ticker symbol. This includes the stock's symbol, name, exchange, company description, P/E ratio, 52 Week High, 52 Week Low, fetched from the Alpha Vantage API

**Route Name and Path**: '/api/lookup-stock/<symbol>'

**Request Format**: 
  *GET Parameters:* - 'symbol' (string): The ticker symbol of the stock (e.g.: 'NVDA' for NVIDIA Corporation).

**Response Format**

  *JSON Keys and Value Types:*

    status: string
    data: dictionary
      Symbol: string
      Name: string
      Exchange: string
      Description: string
      P/E Ratio: string
      52 Week High: string
      52 Week Low: string
  

**Examples**

  *Request:*
    curl -X GET http://127.0.0.1:5000/api/lookup-stock/NVDA
  

  *Success Example Response:*
    {
    "status": "success",
        "data": {
            "Symbol": "NVDA",
            "Name": "NVIDIA Corporation",
            "Exchange": "NASDAQ",
            "Description": ""Designs and manufactures GPUs..."",
            "P/E Ratio": "95.4",
            "52 Week High": "480.0",
            "52 Week Low": "180.0"
        }
     }
        
  *Error Example Response:*
   {
    "status": "error",
    "data": {
        "error": "The stock symbol: INVALID is invalid. Please check the symbol and try again."
    }
   }

### Get Price Details

**Description**:

Retrieves the latest market price details for a specific stock using its ticker symbol. This includes the current price, price change, and percentage change from the previous day, fetched from the Alpha Vantage API.

**Route Name and Path**: '/api/get-price-details/<symbol>'

**Request Format**: 
  *GET Parameters:* - 'symbol' (string): The ticker symbol of the stock (e.g.: 'NVDA' for NVIDIA Corporation).

**Response Format**

  *JSON Keys and Value Types:*

    status: string
    data: dictionary
      Current Price: string  
      Price Change: string  
      Change Percentage: string  
      
**Examples**

  *Request:*
    curl -X GET http://127.0.0.1:5000/api/get-price-details/AMZN
  

  *Success Example Response:*
   {
    "status": "success",
    "data": {
        "Current Price": "142.44",
        "Price Change": "-2.64",
        "Change Percentage": "-1.81%"
    }
   }
        
  *Error Example Response:*
   {
    "status": "error",
    "data": {
        "error": "The stock symbol: INVALID is invalid. Please check the symbol and try again."
    }
   }

### Fetch Historical Data

**Description**:

Fetches historical price data for a stock within a specified date range. The data includes open, close, high, low prices, and trading volume for each day in the range, fetched from the Alpha Vantage API.

**Route Name and Path**: '/api/fetch-historical-data/<string:symbol>/<string:start_date>/<string:end_date>'

**Request Format**: 
  *GET Parameters:* - 'symbol' (string): The ticker symbol of the stock (e.g.: 'NVDA' for NVIDIA Corporation).
                    - 'start_date' (string): The start date for the specified range in YYYY-MM-DD format.
                    - 'end_date' (string): The end date for the specified range in YYYY-MM-DD format.
                 
**Response Format**

  *JSON Keys and Value Types:*

    status: string
    data: list of dictionaries
      date: string  
      open: string  
      close: string  
      high: string  
      low: string  
      volume: string  
      
**Examples**

  *Request:*
    curl -X GET http://127.0.0.1:5000/api/stocks/NVDA/historical/2024-01-01/2024-12-31
  
  *Success Example Response:*

    {
    "status": "success",
    "data": [
        {
            "date": "2024-12-30",
            "open": "175.0",
            "close": "180.0",
            "high": "185.0",
            "low": "170.0",
            "volume": "1500000"
        },
        {
            "date": "2024-12-29",
            "open": "170.0",
            "close": "175.0",
            "high": "180.0",
            "low": "165.0",
            "volume": "1200000"
        }
    ]
}

        
  *Error Example Response:*
   
    {
    "status": "error",
    "data": {
        "error": "The stock symbol: INVALID is invalid. Please check the symbol again."
    }
}

    

    


  
    






