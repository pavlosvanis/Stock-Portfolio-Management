# CS411FinalProject

## Overview / Description
Our final project is a Stock Management app that is designed to manage users' stock trading activities. It integrates functionalities such as user authentication, portfolio management, real-time stock data retrieval through api keys, and 
session handling using Python, MongoDB, and SQLAlchemy.

The Stock Management app allows users to create accounts, securely log in, and manage their stock portfolios. Users can buy and sell the stocks while keeping track of real-time stock prices and historical data fetched via the AlphaVantage API. The application also include the functionality of viewing today's earnings with the holded stocks. Also, the app is capable of updating the deposit when the user deposit or withdraw money from the app. The application maintains user sessions using MongoDB, ensuring that stock holdings and account balances are saved and restored seamlessly. Additionally, the app also provides error handling procedures, user authentication, and password management (hashing) to ensure security and reliability. The app uses SQLAlchemy for database interactions and is containerized with Docker for ease of deployment.

## Requirements / Steps to run the application

- AlphaVantage API key: 
  You should replace the api_key variable: API_KEY in .env file with your real api key:
  API_KEY=your_actual_api_key_here

- Steps to run the application:

  Run the docker-compose.yml file given with steps:
  * docker-compose build    <- This should build the container
  * docker-compose up -d       <- This should run the container (remove "-d" if you want the log to be in the terminal)
  After that, you are able to access the application via: http://localhost:5000

  To close and delete the container:
  * docker-compose down

- Variables in .env:
  * API_KEY: The api key for AlphaVantage that will be used. You should replace it in .env with your own.

## Routes Description:

### Health Check

**Route**: /api/health-check
**Request Type**: GET
**Purpose**: Checks if the application is running and the server is healthy.
**Response Format**: JSON
**Success Response Example**:
  - Code: 200
  - Content: { "status": "healthy" }
**Example Request**:
GET /api/health-check
**Example Response**:
{ "status": "healthy" }

### Create User

**Route**: /api/create-user
**Request Type**: POST
**Purpose**: Creates a new user with a username and password.
**Request Body**:
  - username (String): The desired username.
  - password (String): The chosen password.
**Response Format**: JSON
**Success Response Example**:
  - Code: 201
  - Content: { "status": "user added", "username": "newuser123" }
**Example Request**:
{ "username": "newuser123", "password": "securepassword" }
**Example Response**:
{ "status": "user added", "username": "newuser123" }

### Delete User

**Route**: /api/delete-user
**Request Type**: DELETE
**Purpose**: Deletes a user account based on the username.
**Request Body**:
  - username (String): The username of the account to be deleted.
**Response Format**: JSON
**Success Response Example**:
  - Code: 200
  - Content: { "status": "user deleted", "username": "user123" }
**Example Request**:
{ "username": "user123" }
**Example Response**:
{ "status": "user deleted", "username": "user123" }

### Login

**Route**: /api/login
**Request Type**: POST
**Purpose**: Logs a user into the system.
**Request Body**:
  - username (String): The username of the account.
  - password (String): The corresponding password.
**Response Format**: JSON
**Success Response Example**:
  - Code: 200
  - Content: { "message": "User logged in successfully." }
**Example Request**:
{ "username": "user123", "password": "password123" }
**Example Response**:
{ "message": "User logged in successfully." }

### Logout

**Route**: /api/logout
**Request Type**: POST
**Purpose**: Logs a user out and saves their session data.
**Request Body**:
  - username (String): The username of the account.
  - Response Format: JSON
**Success Response Example**:
  - Code: 200
  - Content: { "message": "User logged out successfully." }
**Example Request**:
{ "username": "user123" }
**Example Response**:
{ "message": "User logged out successfully." }

### update_password

**Route**: /api/update-password
**Request Type**: POST
**Purpose**: Updates the password for an existing user.
**Request Body**:
  - username (String): The username of the account.
  - old_password (String): The current password for verification.
  - new_password (String): The new desired password.
**Response Format**: JSON
**Success Response Example**:
  - Code: 200
  - Content: { "message": "Password updated successfully." }
**Example Request**:
{ "username": "user123", "old_password": "oldpassword123", "new_password": "newpassword456" }
**Example Response**:
{ "message": "Password updated successfully." }

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
   ```
   {
    "status": "success",
    "data": {
        "Symbol": "NVDA",
        "Name": "NVIDIA Corporation",
        "Exchange": "NASDAQ",
        "Description": "Designs and manufactures GPUs...",
        "P/E Ratio": "95.4",
        "52 Week High": "480.0",
        "52 Week Low": "180.0"
    }
 ```

        
  *Error Example Response:*
   ```
   {
    "status": "error",
    "data": {
        "error": "The stock symbol: INVALID is invalid. Please check the symbol and try again."
    }
   }
  ```

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
   ```
   {
    "status": "success",
    "data": {
        "Current Price": "142.44",
        "Price Change": "-2.64",
        "Change Percentage": "-1.81%"
    }
   }
   ```
        
  *Error Example Response:*
   ```
   {
    "status": "error",
    "data": {
        "error": "The stock symbol: INVALID is invalid. Please check the symbol and try again."
    }
   }
   ```

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
  ```
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
  ```

        
  *Error Example Response:*
   ```
   {
    "status": "error",
    "data": {
        "error": "The stock symbol: INVALID is invalid. Please check the symbol again."
    }
   }
   ```

  ### More routes description for user_profile_model:

    

    


  
    






