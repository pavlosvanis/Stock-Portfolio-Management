#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
# check_db() {
#   echo "Checking database connection..."
#   curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
#   if [ $? -eq 0 ]; then
#     echo "Database connection is healthy."
#   else
#     echo "Database check failed."
#     exit 1
#   fi
# }

##########################################################
#
# User Session Management Smoke Test
#
##########################################################



# Create User
create_user() {
  username=$1
  password=$2

  echo "Creating user: $username..."
  response=$(curl -s -X POST "$BASE_URL/create-user" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"$username\", \"password\": \"$password\"}")

  if echo "$response" | grep -q '"status": "user added"'; then
    echo "User created successfully: $response"
  else
    echo "Failed to create user. Response: $response"
    exit 1
  fi
}

# Delete User
delete_user() {
  username=$1

  echo "Deleting user: $username..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-user" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"$username\"}")

  if echo "$response" | grep -q '"status": "user deleted"'; then
    echo "User deleted successfully: $response"
  else
    echo "Failed to delete user. Response: $response"
    exit 1
  fi
}

# Login User
login_user() {
  username=$1
  password=$2

  echo "Logging in user: $username..."
  response=$(curl -s -X POST "$BASE_URL/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"$username\", \"password\": \"$password\"}")

  if echo "$response" | grep -q '"message":'; then
    echo "User logged in successfully: $response"
  else
    echo "Failed to log in user. Response: $response"
    exit 1
  fi
}

# Logout User
logout_user() {
  username=$1

  echo "Logging out user: $username..."
  response=$(curl -s -X POST "$BASE_URL/logout" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"$username\"}")

  if echo "$response" | grep -q '"message":'; then
    echo "User logged out successfully: $response"
  else
    echo "Failed to log out user. Response: $response"
    exit 1
  fi
}

# Update Password
update_password() {
  username=$1
  old_password=$2
  new_password=$3

  echo "Updating password for user: $username..."
  response=$(curl -s -X POST "$BASE_URL/update-password" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"$username\", \"old_password\": \"$old_password\", \"new_password\": \"$new_password\"}")

  if echo "$response" | grep -q '"message":'; then
    echo "Password updated successfully: $response"
  else
    echo "Failed to update password. Response: $response"
    exit 1
  fi
}

##########################################################
#
# Stock Data Management Smoke Test
#
##########################################################

# Lookup Stock
lookup_stock() {
  symbol=$1

  echo "Looking up stock: $symbol..."
  response=$(curl -s -X GET "$BASE_URL/lookup-stock/$symbol")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Stock lookup successful: $response"
  else
    echo "Failed to lookup stock. Response: $response"
    exit 1
  fi
}

# Get Stock Price Details
get_price_details() {
  symbol=$1

  echo "Getting price details for stock: $symbol..."
  response=$(curl -s -X GET "$BASE_URL/get-price-details/$symbol")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Price details retrieved successfully: $response"
  else
    echo "Failed to retrieve price details. Response: $response"
    exit 1
  fi
}

# Fetch Historical Data
fetch_historical_data() {
  symbol=$1
  start_date=$2
  end_date=$3

  echo "Fetching historical data for stock: $symbol from $start_date to $end_date..."
  response=$(curl -s -X GET "$BASE_URL/fetch-historical-data/$symbol/$start_date/$end_date")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Historical data retrieved successfully: $response"
  else
    echo "Failed to retrieve historical data. Response: $response"
    exit 1
  fi
}

##########################################################
#
# User Profile Smoke Test
#
##########################################################


# Check Portfolio
get_portfolio() {
  echo "Getting user portfolio..."
  response=$(curl -s -X GET "$BASE_URL/get-portfolio")
  if echo "$response" | grep -q '"status": "Get portfolio successful"'; then
    echo "Portfolio retrieved successfully."
    echo "$response" | jq .
  else
    echo "Failed to retrieve portfolio. Response: $response"
    exit 1
  fi
}

# Get Total Values
get_total_values() {
  echo "Getting total portfolio values..."
  response=$(curl -s -X GET "$BASE_URL/get-total-values")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Total values retrieved successfully."
    echo "$response" | jq .
  else
    echo "Failed to retrieve total values. Response: $response"
    exit 1
  fi
}

# Add Stock
add_stock() {
  symbol=$1
  quantity=$2
  bought_price=$3

  echo "Adding $quantity shares of $symbol at $bought_price to portfolio..."
  response=$(curl -s -X POST "$BASE_URL/add-stock" \
    -H "Content-Type: application/json" \
    -d "{\"symbol\": \"$symbol\", \"quantity\": $quantity, \"bought_price\": $bought_price}")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Stock added successfully."
  else
    echo "Failed to add stock. Response: $response"
    exit 1
  fi
}

# Remove Stock
remove_stock() {
  symbol=$1
  quantity=$2

  echo "Removing $quantity shares of $symbol from portfolio..."
  response=$(curl -s -X POST "$BASE_URL/remove-stock" \
    -H "Content-Type: application/json" \
    -d "{\"symbol\": \"$symbol\", \"quantity\": $quantity}")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Stock removed successfully."
  else
    echo "Failed to remove stock. Response: $response"
    exit 1
  fi
}

# Update Cash Balance
update_cash_balance() {
  amount=$1

  echo "Updating cash balance by $amount..."
  response=$(curl -s -X POST "$BASE_URL/update-cash" \
    -H "Content-Type: application/json" \
    -d "{\"amount\": $amount}")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Cash balance updated successfully."
    echo "$response" | jq .
  else
    echo "Failed to update cash balance. Response: $response"
    exit 1
  fi
}

# Clear Portfolio
clear_portfolio() {
  echo "Clearing the portfolio..."
  response=$(curl -s -X POST "$BASE_URL/clear-portfolio")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Portfolio cleared successfully."
  else
    echo "Failed to clear portfolio. Response: $response"
    exit 1
  fi
}

# Buy Stock
buy_stock() {
  symbol=$1
  quantity=$2

  echo "Buying $quantity shares of $symbol..."
  response=$(curl -s -X POST "$BASE_URL/buy-stock" \
    -H "Content-Type: application/json" \
    -d "{\"symbol\": \"$symbol\", \"quantity\": $quantity}")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Stock bought successfully."
  else
    echo "Failed to buy stock. Response: $response"
    exit 1
  fi
}

# Sell Stock
sell_stock() {
  symbol=$1
  quantity=$2

  echo "Selling $quantity shares of $symbol..."
  response=$(curl -s -X POST "$BASE_URL/sell-stock" \
    -H "Content-Type: application/json" \
    -d "{\"symbol\": \"$symbol\", \"quantity\": $quantity}")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Stock sold successfully."
  else
    echo "Failed to sell stock. Response: $response"
    exit 1
  fi
}


# Health checks
check_health
check_db


create_user "testuser" "testpassword"
login_user "testuser" "testpassword"
update_password "testuser" "testpassword" "newpassword"
logout_user "testuser"
lookup_stock "AAPL"
get_price_details "AAPL"
# fetch_historical_data "AAPL" "2023-01-01" "2023-12-31"
delete_user "testuser"

# Smoke Test Execution


get_portfolio
get_total_values
add_stock "AAPL" 10 150.25
remove_stock "AAPL" 5
update_cash_balance 5000.00
clear_portfolio
buy_stock "GOOGL" 2
sell_stock "GOOGL" 2


echo "All tests passed successfully!"
