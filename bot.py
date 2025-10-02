import os
import argparse
import logging
from dotenv import load_dotenv
from binance.client import Client
from binance_service import BinanceService

class BasicBot:
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.client = Client(api_key, api_secret, testnet=testnet)
        self.client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
        self.service = BinanceService(self.client)
        self.service.check_connection()

    def execute_trade(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None, stop_price: float = None):
        logging.info(f"Bot Engine: Processing {order_type} trade for {symbol}...")
        return self.service.place_order(symbol, side, order_type, quantity, price, stop_price)

    def check_info(self, check_type: str, asset: str = None, symbol: str = None, order_id: int = None):
        if check_type == 'balance':
            return self.service.get_balance(asset)
        elif check_type == 'order':
            if not symbol or not order_id:
                raise ValueError("Symbol and Order ID are required to check order status.")
            return self.service.get_order_status(symbol, order_id)
        return None

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("trading_bot.log"),
            logging.StreamHandler()
        ]
    )

    parser = argparse.ArgumentParser(description="A CLI-based Binance Futures Trading Bot.")
    subparsers = parser.add_subparsers(dest='command', help='Main command', required=True)

    trade_parser = subparsers.add_parser('trade', help='Place a trade order.')
    trade_subparsers = trade_parser.add_subparsers(dest='order_type', help='Type of trade order', required=True)

    market_parser = trade_subparsers.add_parser('MARKET', help='Place a market order.')
    market_parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTCUSDT)')
    market_parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='Order side')
    market_parser.add_argument('--quantity', required=True, type=float, help='Order quantity')

    limit_parser = trade_subparsers.add_parser('LIMIT', help='Place a limit order.')
    limit_parser.add_argument('--symbol', required=True, help='Trading symbol')
    limit_parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='Order side')
    limit_parser.add_argument('--quantity', required=True, type=float, help='Order quantity')
    limit_parser.add_argument('--price', required=True, type=float, help='Limit price')

    stop_market_parser = trade_subparsers.add_parser('STOP_MARKET', help='Place a stop-loss market order.')
    stop_market_parser.add_argument('--symbol', required=True, help='Trading symbol')
    stop_market_parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='Order side')
    stop_market_parser.add_argument('--quantity', required=True, type=float, help='Order quantity')
    stop_market_parser.add_argument('--stop-price', required=True, type=float, help='Stop price to trigger the order')

    check_parser = subparsers.add_parser('check', help='Check account or order information.')
    check_subparsers = check_parser.add_subparsers(dest='check_type', help='Type of information to check', required=True)

    balance_parser = check_subparsers.add_parser('balance', help='Check account balance.')
    balance_parser.add_argument('--asset', help='Specific asset to check (e.g., USDT). Shows all if omitted.')

    order_parser = check_subparsers.add_parser('order', help='Check a specific order\'s status.')
    order_parser.add_argument('--symbol', required=True, help='Symbol of the order')
    order_parser.add_argument('--order-id', required=True, type=int, help='The ID of the order to check')

    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv('BINANCE_TESTNET_API_KEY')
    api_secret = os.getenv('BINANCE_TESTNET_API_SECRET')
    if not api_key or not api_secret:
        logging.critical("API keys not found in .env file. Please create it and add your keys.")
        return

    try:
        bot = BasicBot(api_key=api_key, api_secret=api_secret)
    except Exception as e:
        logging.critical(f"Failed to initialize bot. Exiting. Error: {e}")
        return

    result = None
    if args.command == 'trade':
        result = bot.execute_trade(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=getattr(args, 'price', None),
            stop_price=getattr(args, 'stop_price', None)
        )
    elif args.command == 'check':
        result = bot.check_info(
            check_type=args.check_type,
            asset=getattr(args, 'asset', None),
            symbol=getattr(args, 'symbol', None),
            order_id=getattr(args, 'order_id', None)
        )

    if result is not None:
        print("\n--- Operation Successful ---")
        if args.command == 'check' and args.check_type == 'balance' and not result:
            print("No assets with a non-zero balance found.")
        else:
            print(result)
    else:
        print("\n--- Operation Failed ---")
        print("Please check trading_bot.log for detailed error information.")

if __name__ == "__main__":
    main()
