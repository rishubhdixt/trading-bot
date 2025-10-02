import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException

class BinanceService:
    def __init__(self, client: Client):
        self.client = client

    def check_connection(self):
        try:
            self.client.futures_account()
            logging.info("Binance API connection successful.")
        except BinanceAPIException as e:
            logging.error(f"Binance API connection failed: {e}")
            raise

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None, stop_price: float = None):
        try:
            params = {
                'symbol': symbol,
                'side': side.upper(),
                'type': order_type.upper(),
                'quantity': quantity
            }
            if order_type.upper() in ['LIMIT', 'STOP_LIMIT', 'TAKE_PROFIT_LIMIT']:
                if not price:
                    raise ValueError(f"Price is required for {order_type} orders.")
                params['price'] = price
                params['timeInForce'] = 'GTC'
            if order_type.upper() in ['STOP_MARKET', 'STOP_LIMIT', 'TAKE_PROFIT_MARKET', 'TAKE_PROFIT_LIMIT']:
                if not stop_price:
                    raise ValueError(f"Stop Price is required for {order_type} orders.")
                params['stopPrice'] = stop_price
            logging.info(f"Placing order with params: {params}")
            order = self.client.futures_create_order(**params)
            logging.info(f"Successfully placed {order_type} order. Response: {order}")
            return order
        except (BinanceAPIException, ValueError) as e:
            logging.error(f"Failed to place {order_type} order for {symbol}: {e}")
            return None

    def get_balance(self, asset: str = None):
        try:
            balances = self.client.futures_account_balance()
            if asset:
                for balance in balances:
                    if balance['asset'].upper() == asset.upper():
                        return balance
                return None
            else:
                return {item['asset']: float(item['balance']) for item in balances if float(item['balance']) != 0}
        except BinanceAPIException as e:
            logging.error(f"Failed to get account balance: {e}")
            return None

    def get_order_status(self, symbol: str, order_id: int):
        try:
            status = self.client.futures_get_order(symbol=symbol, orderId=order_id)
            return status
        except BinanceAPIException as e:
            logging.error(f"Failed to get status for order {order_id}: {e}")
            return None
