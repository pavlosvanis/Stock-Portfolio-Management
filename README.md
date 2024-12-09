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
      {
        "error": "The stock symbol: INVALID_SYMBOL is invalid. Please check the symbol and try again."
      }
  
    






