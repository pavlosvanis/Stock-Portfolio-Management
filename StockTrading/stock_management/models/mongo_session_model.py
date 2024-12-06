import logging
from typing import Any, List

from stock_management.clients.mongo_client import sessions_collection
from stock_management.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


def login_user(user_id: int, user_profile_model) -> None:
    """
    Load the user's stocks from MongoDB into the UserProfile's stock list.

    Checks if a session document exists for the given `user_id` in MongoDB.
    If it exists, clears any current stocks in `user_profile_model` and loads
    the stored stocks from MongoDB into `user_profile_model`.

    If no session is found, it creates a new session document for the user
    with an empty stock list in MongoDB.

    Args:
        user_id (int): The ID of the user whose session is to be loaded.
        user_profile_model (UserProfile): An instance of `UserProfile` where 
                                          the user's stocks will be loaded.
    """
    logger.info("Attempting to log in user with ID %d.", user_id)
    session = sessions_collection.find_one({"user_id": user_id})

    if session:
        logger.info("Session found for user ID %d. Loading stocks into UserProfile.", user_id)
        user_profile_model.clear_all_stock()

        stocks = session.get("current_stock_holding", {})
        for symbol, quantity in stocks.items():
            logger.debug("Loading stock: %s, quantity: %d", symbol, quantity)
            user_profile_model.add_stock_to_holding(symbol, quantity)

        user_profile_model.update_cash_balance(session.get("cash_balance", 0.0))
        logger.info("Stock holdings and cash balance successfully loaded for user ID %d.", user_id)
    else:
        logger.info("No session found for user ID %d. Creating a new session with empty stock list.", user_id)
        sessions_collection.insert_one({"user_id": user_id, "current_stock_holding": {}, "cash_balance": 0.0})
        logger.info("New session created for user ID %d.", user_id)

def logout_user(user_id: int, user_profile_model) -> None:
    """
    Store the current stocks from the UserProfile back into MongoDB.

    Retrieves the current stocks from `user_profile_model` and attempts to store them in
    the MongoDB session document associated with the given `user_id`. If no session
    document exists for the user, raises a `ValueError`.

    After saving the stocks to MongoDB, the stocks list in `user_profile_model` is
    cleared to ensure a fresh state for the next login.

    Args:
        user_id (int): The ID of the user whose session data is to be saved.
        user_profile_model (UserProfile): An instance of `UserProfile` from 
                                          which the user's current combatants 
                                          are retrieved.

    Raises:
        ValueError: If no session document is found for the user in MongoDB.
    """
    logger.info("Attempting to log out user with ID %d.", user_id)
    stocks = user_profile_model.get_portfolio()
    cash_balance = user_profile_model.cash_balance

    logger.debug("Current stock holdings for user ID %d: %s", user_id, stocks)
    logger.debug("Current cash balance for user ID %d: %f", user_id, cash_balance)

    result = sessions_collection.update_one(
        {"user_id": user_id},
        {"$set": {"current_stock_holding": stocks, "cash_balance": cash_balance}},
        upsert=False
    )

    if result.matched_count == 0:
        logger.error("No session found for user ID %d. Logout failed.", user_id)
        raise ValueError(f"User with ID {user_id} not found for logout.")

    logger.info("Stocks successfully saved for user ID %d. Clearing UserProfile stocks.", user_id)
    user_profile_model.clear_all_stock()
    logger.info("UserProfile stocks cleared for user ID %d.", user_id)