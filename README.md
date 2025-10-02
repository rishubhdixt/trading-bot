# Binance Futures Trading Bot

A simplified trading bot built in Python for Binance **USDT-M Futures Testnet**.  
This bot supports **Market**, **Limit**, and **Stop-Market** orders via a command-line interface (CLI).  
It is structured with a clean service layer (`BinanceService`) and bot controller (`BasicBot`) for reusability and maintainability.

---

## 🚀 Features
- Place **Market** and **Limit** orders on Binance Futures Testnet
- Supports both **BUY** and **SELL**
- **Stop-Market** order type implemented (bonus feature)
- Check account balances (specific asset or all)
- Check order status by symbol + order ID
- Robust **logging** (console + `trading_bot.log`)
- Structured **CLI** using `argparse`
- Error handling with clear logs

---


