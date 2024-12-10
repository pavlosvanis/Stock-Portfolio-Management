from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from werkzeug.exceptions import BadRequest, Unauthorized
from config import ProductionConfig

from stock_management.db import db
from stock_management.models import stock_model
from stock_management.models.user_profile_model import UserProfile
from stock_management.models.users_management_model import Users
from stock_management.models.mongo_session_model import login_user, logout_user

from stock_management.models.stock_model import (
    lookup_stock,
    get_price_details,
    fetch_historical_data
)

# Load environment variables from .env file
load_dotenv()


def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)  # Initialize db with app
    with app.app_context():
        db.create_all()  # Recreate all tables

    user_profile_model = UserProfile()

    ####################################################
    #
    # Healthchecks
    #
    ####################################################

    @app.route('/api/health', methods=['GET'])
    def healthcheck() -> Response:
        """
        Health check route to verify the service is running.

        Returns:
            JSON response indicating the health status of the service.
        """
        app.logger.info('Health check')
        return make_response(jsonify({'status': 'healthy'}), 200)

    ##########################################################
    #
    # Users Management
    #
    ##########################################################

    @app.route('/api/create-user', methods=['POST'])
    def create_user() -> Response:
        """
        Route to create a new user.

        Expected JSON Input:
            - username (str): The username for the new user.
            - password (str): The password for the new user.

        Returns:
            JSON response indicating the success of user creation.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the user to the database.
        """
        app.logger.info('Creating new user')
        try:
            # Get the JSON data from the request
            data = request.get_json()

            # Extract and validate required fields
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return make_response(jsonify({'error': 'Invalid input, both username and password are required'}), 400)

            # Call the User function to add the user to the database
            app.logger.info('Adding user: %s', username)
            Users.create_user(username, password)

            app.logger.info("User added: %s", username)
            return make_response(jsonify({'status': 'user added', 'username': username}), 201)
        except Exception as e:
            app.logger.error("Failed to add user: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/delete-user', methods=['DELETE'])
    def delete_user() -> Response:
        """
        Route to delete a user.

        Expected JSON Input:
            - username (str): The username of the user to be deleted.

        Returns:
            JSON response indicating the success of user deletion.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue deleting the user from the database.
        """
        app.logger.info('Deleting user')
        try:
            # Get the JSON data from the request
            data = request.get_json()

            # Extract and validate required fields
            username = data.get('username')

            if not username:
                return make_response(jsonify({'error': 'Invalid input, username is required'}), 400)

            # Call the User function to delete the user from the database
            app.logger.info('Deleting user: %s', username)
            Users.delete_user(username)

            app.logger.info("User deleted: %s", username)
            return make_response(jsonify({'status': 'user deleted', 'username': username}), 200)
        except Exception as e:
            app.logger.error("Failed to delete user: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/login', methods=['POST'])
    def login():
        """
        Route to log in a user and load their combatants.

        Expected JSON Input:
            - username (str): The username of the user.
            - password (str): The user's password.

        Returns:
            JSON response indicating the success of the login.

        Raises:
            400 error if input validation fails.
            401 error if authentication fails (invalid username or password).
            500 error for any unexpected server-side issues.
        """
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            app.logger.error("Invalid request payload for login.")
            raise BadRequest("Invalid request payload. 'username' and 'password' are required.")

        username = data['username']
        password = data['password']

        try:
            # Validate user credentials
            if not Users.check_password(username, password):
                app.logger.warning("Login failed for username: %s", username)
                raise Unauthorized("Invalid username or password.")

            # Get user ID
            user_id = Users.get_id_by_username(username)

            # Load user's combatants into the battle model
            login_user(user_id, user_profile_model)

            app.logger.info("User %s logged in successfully.", username)
            return jsonify({"message": f"User {username} logged in successfully."}), 200

        except Unauthorized as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            app.logger.error("Error during login for username %s: %s", username, str(e))
            return jsonify({"error": "An unexpected error occurred."}), 500

    @app.route('/api/logout', methods=['POST'])
    def logout():
        """
        Route to log out a user and save their combatants to MongoDB.

        Expected JSON Input:
            - username (str): The username of the user.

        Returns:
            JSON response indicating the success of the logout.

        Raises:
            400 error if input validation fails or user is not found in MongoDB.
            500 error for any unexpected server-side issues.
        """
        data = request.get_json()
        if not data or 'username' not in data:
            app.logger.error("Invalid request payload for logout.")
            raise BadRequest("Invalid request payload. 'username' is required.")

        username = data['username']

        try:
            # Get user ID
            user_id = Users.get_id_by_username(username)

            # Save user's combatants and clear the battle model
            logout_user(user_id, user_profile_model)

            app.logger.info("User %s logged out successfully.", username)
            return jsonify({"message": f"User {username} logged out successfully."}), 200

        except ValueError as e:
            app.logger.warning("Logout failed for username %s: %s", username, str(e))
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            app.logger.error("Error during logout for username %s: %s", username, str(e))
            return jsonify({"error": "An unexpected error occurred."}), 500

    @app.route('/api/update-password', methods=['POST'])
    def update_password():
        """
        Route to update a user's password.

        Expected JSON input:
            - username (str): The username of the user.
            - old_password (str): The user's current password for verification.
            - new_password (str): The user's new desired password.

        Returns:
            JSON response indicating success or failure of the password update.

        Raises:
            400 error if input validation fails.
            401 error if the old password is incorrect.
            500 error if there is an unexpected issue during the update.
        """
        app.logger.info('Attempting to update user password')
        try:
            data = request.get_json()
            username = data.get('username')
            old_password = data.get('old_password')
            new_password = data.get('new_password')

            if not username or not old_password or not new_password:
                app.logger.warning('Invalid input: Missing username, old_password, or new_password')
                return make_response(jsonify({'error': 'Username, old_password, and new_password are required'}), 400)

            # Verify the old password using verify_user_credentials
            app.logger.info('Verifying old password for username: %s', username)
            if not Users.check_password(username, old_password):
                app.logger.warning('Old password verification failed for username: %s', username)
                return make_response(jsonify({'error': 'Old password is incorrect'}), 401)

            app.logger.info('Updating password for username: %s', username)
            Users.update_password(username, new_password)
            app.logger.info('Password updated successfully for username: %s', username)
            return make_response(jsonify({'message': 'Password updated successfully'}), 200)

        except ValueError as e:
            app.logger.error('Password update failed for username %s: %s', username, str(e))
            return make_response(jsonify({'error': str(e)}), 400)
        except Exception as e:
            app.logger.error('Unexpected error during password update: %s', str(e))
            return make_response(jsonify({'error': 'An unexpected error occurred'}), 500)
    
    ##########################################################
    #
    # Stock infos
    #
    ##########################################################

    @app.route('/api/lookup-stock/<string:symbol>', methods=['GET'])
    def lookup_stock_route(symbol: str) -> Response:
        """
        Route to look up a stock (retrieving basic details) based on symbol.
        Path Parameters:
            - symbol (str): The stock's ticker symbol.
        Returns:
            JSON response with the stock basic details or an error message.
        """
        try:
            app.logger.info(f"Looking up stock with symbol: {symbol}")
            stock_basic_details = lookup_stock(symbol)
            return make_response(jsonify({"status": "success", "data": stock_basic_details}), 200)
        except ValueError as e:
            app.logger.error(f"Error looking up stock with symbol: {e}")
            return make_response(jsonify({"error": str(e)}), 400)
        except Exception as e:
            app.logger.error(f"Unexpected error: {e}")
            return make_response(jsonify({"error": "An unexpected error occurred"}), 500)

    @app.route('/api/get-price-details/<string:symbol>', methods=['GET'])
    def get_price_details_route(symbol: str) -> Response:
        """
        Route to get price details of a stock based on symbol.
        Path Parameters:
            - symbol (str): The stock's ticker symbol.
        Returns:
            JSON response with the stock price details or an error message.
        """
        try:
            app.logger.info(f"Getting price details for stock with symbol: {symbol}")
            stock_price_details = get_price_details(symbol)
            return make_response(jsonify({"status": "success", "data": stock_price_details}), 200)
        except ValueError as e:
            app.logger.error(f"Error getting price details for stock with symbol: {e}")
            return make_response(jsonify({"error": str(e)}), 400)
        except Exception as e:
            app.logger.error(f"Unexpected error: {e}")
            return make_response(jsonify({"error": "An unexpected error occurred"}), 500)

    @app.route('/api/fetch-historical-data/<string:symbol>/<string:start_date>/<string:end_date>', methods=['GET'])
    def fetch_historical_data_route(symbol: str, start_date: str, end_date: str) -> Response:
        """
        Route to fetch historical data of a stock based on symbol within a specified date range.
        Path Parameters:
            - symbol (str): The stock's ticker symbol.
            - start_date (str): The start date for historical data (e.g., `YYYY-MM-DD`).
            - end_date (str): The end date for historical data (e.g., `YYYY-MM-DD`).
        Returns:
            JSON response with the stock's historical data for the specified data range or an error message.
        """

        try:
            app.logger.info(
                f"Fetching historical data for stock with symbol: {symbol} between {start_date} and {end_date}.")
            stock_historical_data = fetch_historical_data(symbol, start_date, end_date)
            return make_response(jsonify({"status": "success", "data": stock_historical_data}), 200)
        except ValueError as e:
            app.logger.error(f"Error fetching historical data for stock with symbol: {e}")
            return make_response(jsonify({"error": str(e)}), 400)
        except Exception as e:
            app.logger.error(f"Unexpected error: {e}")
            return make_response(jsonify({"error": "An unexpected error occurred"}), 500)
    @app.route('/api/add-stock', methods=['POST'])
    def add_stock_to_portfolio_route():
        """
        Route to allow the user to add a stock to their portfolio.
        Path Parameters:
            None
        Body Parameters:
            - user_id (int): The unique ID of the user.
            - symbol (str): The stock's ticker symbol.
            - quantity (int): The number of shares to purchase.
            - bought_price (float): The price per share at which the stock was purchased.
        Returns:
            JSON response indicating whether the stock was successfully added or an error occurred.
        """
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            symbol = data.get('symbol')
            quantity = data.get('quantity')
            bought_price = data.get('bought_price')

            # Directly instantiate UserProfile for the provided user_id
            user_profile = UserProfile(user_id, "test_username")  # "test_username" as placeholder

            # Add stock to user's portfolio
            user_profile.add_stock_to_portfolio(symbol, quantity, bought_price)
            return jsonify({'status': 'Stock added successfully'})
        except ValueError as e:
            app.logger.error(f"Error adding stock to portfolio: {e}")
            return make_response(jsonify({'error': str(e)}), 400)
        except Exception as e:
            app.logger.error(f"Unexpected error while adding stock: {e}")
            return make_response(jsonify({'error': 'An unexpected error occurred'}), 500)

    @app.route('/api/remove-stock', methods=['POST'])
    def remove_stock_from_holding_route():
        """
        Route to allow the user to remove or reduce the quantity of a stock in their portfolio.
        Path Parameters:
            None
        Body Parameters:
            - user_id (int): The unique ID of the user.
            - symbol (str): The stock's ticker symbol.
            - quantity (int): The number of shares to remove.
        Returns:
            JSON response indicating whether the stock was successfully removed or an error occurred.
        """
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            symbol = data.get('symbol')
            quantity = data.get('quantity')

            # Directly instantiate UserProfile for the provided user_id
            user_profile = UserProfile(user_id, "test_username")  # "test_username" as placeholder

            # Remove stock from user's portfolio
            user_profile.remove_stock_from_holding(symbol, quantity)
            return jsonify({'status': 'Stock removed successfully'})
        except ValueError as e:
            app.logger.error(f"Error removing stock from holding: {e}")
            return make_response(jsonify({'error': str(e)}), 400)
        except Exception as e:
            app.logger.error(f"Unexpected error while removing stock: {e}")
            return make_response(jsonify({'error': 'An unexpected error occurred'}), 500)

    @app.route('/api/update-cash-balance', methods=['POST'])
    def update_cash_balance_route():
        """
        Route to update a user's cash balance by adding or subtracting an amount.
        Path Parameters:
            None
        Body Parameters:
            - user_id (int): The unique ID of the user.
            - amount (float): The amount to add or subtract from the balance.
        Returns:
            JSON response indicating whether the cash balance was updated or an error occurred.
        """
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            amount = data.get('amount')

            # Directly instantiate UserProfile for the provided user_id
            user_profile = UserProfile(user_id, "test_username")  # "test_username" as placeholder

            # Update the user's cash balance
            user_profile.update_cash_balance(amount)
            return jsonify({'status': 'Cash balance updated successfully'})
        except ValueError as e:
            app.logger.error(f"Error updating cash balance: {e}")
            return make_response(jsonify({'error': str(e)}), 400)
        except Exception as e:
            app.logger.error(f"Unexpected error while updating cash balance: {e}")
            return make_response(jsonify({'error': 'An unexpected error occurred'}), 500)

    @app.route('/api/buy-stock', methods=['POST'])
    def buy_stock():
        """
        Route to allow the user to buy a stock and add it to their portfolio.
        Path Parameters:
            None
        Body Parameters:
            - user_id (int): The unique ID of the user.
            - symbol (str): The stock's ticker symbol.
            - quantity (int): The number of shares to purchase.
            - stock_price (float): The price per share of the stock.
        Returns:
            JSON response indicating whether the stock was purchased or an error occurred.
        """
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            symbol = data.get('symbol')
            quantity = data.get('quantity')
            stock_price = data.get('stock_price')

            user_profile = UserProfile(user_id, "test_username")
            if not user_profile:
                app.logger.error(f"User not found for purchase: {user_id}")
                return make_response(jsonify({'error': 'User not found'}), 404)

            user_profile.buy_stock(symbol, quantity, stock_price)
            app.logger.info(f"User {user_id} bought {quantity} shares of {symbol} at {stock_price} each.")
            return jsonify({'status': 'Stock purchased successfully'})
        except Exception as e:
            app.logger.error(f"Error buying stock: {e}")
            return make_response(jsonify({'error': str(e)}), 400)


    @app.route('/api/sell-stock', methods=['POST'])
    def sell_stock():
        """
        Route to allow the user to sell a stock from their portfolio.
        Path Parameters:
            None
        Body Parameters:
            - user_id (int): The unique ID of the user.
            - symbol (str): The stock's ticker symbol.
            - quantity (int): The number of shares to sell.
            - stock_price (float): The price per share of the stock.
        Returns:
            JSON response indicating whether the stock was sold or an error occurred.
        """
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            symbol = data.get('symbol')
            quantity = data.get('quantity')
            stock_price = data.get('stock_price')

            user_profile = UserProfile(user_id, "test_username")
            if not user_profile:
                app.logger.error(f"User not found for sale: {user_id}")
                return make_response(jsonify({'error': 'User not found'}), 404)

            user_profile.sell_stock(symbol, quantity, stock_price)
            app.logger.info(f"User {user_id} sold {quantity} shares of {symbol} at {stock_price} each.")
            return jsonify({'status': 'Stock sold successfully'})
        except Exception as e:
            app.logger.error(f"Error selling stock: {e}")
            return make_response(jsonify({'error': str(e)}), 400)



    
    # TODO DELETE MEALS AND WHAT IS NOT NEEDED (CHECK THAT WE DONT DELETE DATABASE RELATED CODE THAT IF IT IS NEEDED)
    
    ##########################################################
    #
    # User Profile Operations
    #
    ##########################################################


    @app.route('/api/clear-combatants', methods=['POST'])
    def clear_combatants() -> Response:
        """
        Route to clear the list of combatants for the battle.

        Returns:
            JSON response indicating success of the operation.
        Raises:
            500 error if there is an issue clearing combatants.
        """
        try:
            app.logger.info('Clearing all combatants...')
            battle_model.clear_combatants()
            app.logger.info('Combatants cleared.')
            return make_response(jsonify({'status': 'combatants cleared'}), 200)
        except Exception as e:
            app.logger.error("Failed to clear combatants: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/get-combatants', methods=['GET'])
    def get_combatants() -> Response:
        """
        Route to get the list of combatants for the battle.

        Returns:
            JSON response with the list of combatants.
        """
        try:
            app.logger.info('Getting combatants...')
            combatants = battle_model.get_combatants()
            return make_response(jsonify({'status': 'success', 'combatants': combatants}), 200)
        except Exception as e:
            app.logger.error("Failed to get combatants: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/prep-combatant', methods=['POST'])
    def prep_combatant() -> Response:
        """
        Route to prepare a prep a meal making it a combatant for a battle.

        Parameters:
            - meal (str): The name of the meal

        Returns:
            JSON response indicating the success of combatant preparation.
        Raises:
            500 error if there is an issue preparing combatants.
        """
        try:
            data = request.json
            if not data or 'meal' not in data:
                return make_response(jsonify({'error': 'Meal name is required'}), 400)
            meal = data.get('meal')
            app.logger.info("Preparing combatant: %s", meal)

            if not meal:
                raise BadRequest('You must name a combatant')

            try:
                meal = Meals.get_meal_by_name(meal)
                battle_model.prep_combatant(meal)
                combatants = battle_model.get_combatants()
            except Exception as e:
                app.logger.error("Failed to prepare combatant: %s", str(e))
                return make_response(jsonify({'error': str(e)}), 500)
            return make_response(jsonify({'status': 'combatant prepared', 'combatants': combatants}), 200)

        except Exception as e:
            app.logger.error("Failed to prepare combatants: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)
    
    # Routes end here.
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
