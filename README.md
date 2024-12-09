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
    data: object
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
        
  *Error Example Response:*
   
    "status": "error",
    "data": {
        "error": "The stock symbol: INVALID_SYMBOL is invalid. Please check the symbol and try again."
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
    data: object
      Current Price: string  
      Price Change: string  
      Change Percentage: string  
      
**Examples**

  *Request:*
    curl -X GET http://127.0.0.1:5000/api/get-price-details/AMZN
  

  *Success Example Response:*

    "status": "success",
    "data": {
        "Current Price": "135.0",
        "Price Change": "+2.5",
        "Change Percentage": "+1.87%"
    }

        
  *Error Example Response:*
   
    "status": "error",
    "data": {
        "error": "The stock symbol: INVALID_SYMBOL is invalid. Please check the symbol and try again."
    }

    


  
    






