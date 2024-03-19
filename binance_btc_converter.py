import json
import time
from datetime import datetime
from binance.error import (
    ClientError,
    ServerError,
    ParameterRequiredError,
    ParameterValueError
)
from binance.spot import Spot

class BinanceWrapper:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.binance_client = Spot(api_key=api_key, api_secret=api_secret)

    def get_exchange_rate(self, symbol):
        """Get the exchange rate of Coins"""
        try:
            ticker = self.binance_client.ticker_price(symbol=symbol)
            rate = float(ticker['price'])
            return rate
        except (ClientError, ServerError, ParameterRequiredError, ParameterValueError) as e:
            print(f"Failed to get {symbol} rate. Exception: {e}")
            return None
        except ValueError as e:
            print(f"Invalid symbol: {symbol}. Exception: {e}")
            return None
        except KeyError as e:
            print(f"Unknown symbol: {symbol}. Exception: {e}")
            return None

    def get_binance_balance(self):
        """Get the balances of Binance Wallet"""
        try:
            balances = self.binance_client.account()
            return balances['balances']
        except (ClientError, ServerError, ParameterRequiredError, ParameterValueError) as e:
            print(f"Failed to get Binance balance. Exception: {e}")
            return None

    def get_deposits(self):
        """Get the Deposits"""
        all_deposits = []
        try:
            deposits = self.binance_client.deposit_history()
            all_deposits.extend(deposits)
        except (ClientError, ServerError, ParameterRequiredError, ParameterValueError) as e:
            print("Failed to retrieve deposit history:", e)
        finally:
            print("Anzahl der Einzahlungen:", len(all_deposits))
        return all_deposits

    def get_withdrawals(self):
        """Get the Withdrawals"""
        all_withdrawals = []
        try:
            withdrawals = self.binance_client.withdraw_history()
            all_withdrawals.extend(withdrawals)
        except (ClientError, ServerError, ParameterRequiredError, ParameterValueError) as e:
            print("Failed to retrieve withdrawal history:", e)
        finally:
            print("Anzahl der Auszahlungen:", len(all_withdrawals))
        return all_withdrawals


class Calculation:
    def __init__(self, binance_wrapper):
        self.binance_wrapper = binance_wrapper

    def calculate_total_balance_in_btc(self):
        """Calculate the total balance in BTC"""
        balances = self.binance_wrapper.get_binance_balance()
        total_balance_in_btc = 0.0
        if balances:
            for balance in balances:
                asset = balance['asset']
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                if total > 0:
                    print(f"{asset}: {total:.8f}")              
                    if asset == "BTC":
                        total_balance_in_btc += total
                    else:
                        symbol = f"{asset}BTC"
                        exchange_rate = self.binance_wrapper.get_exchange_rate(symbol)
                        if exchange_rate is not None:
                            value_in_btc = total * exchange_rate
                            total_balance_in_btc += value_in_btc
                        else:
                            print(f"Failed to get {symbol} rate. Skipping.")
        return total_balance_in_btc


def load_config(filename='config.json'):
    """Load API configuration from file"""
    with open(filename, encoding='utf-8') as f:
        return json.load(f)


if __name__ == "__main__":
    config = load_config()
    api_key = config['api_key']
    api_secret = config['api_secret']

    binance_wrapper = BinanceWrapper(api_key, api_secret)
    calculation_class = Calculation(binance_wrapper)
    total_balance_btc = calculation_class.calculate_total_balance_in_btc()
    print(f"Total Balance in BTC: {total_balance_btc}")