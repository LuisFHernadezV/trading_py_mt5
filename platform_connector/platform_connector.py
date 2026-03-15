from dataclasses import dataclass
import MetaTrader5 as mt5
import os
from dotenv import load_dotenv, find_dotenv


@dataclass
class PlatformConnector:
    symbols: list[str]

    def __post_init__(self) -> None:

        load_dotenv(find_dotenv())
        self._inicialize_platform()
        # Comprobamos que el tipo de cuenta sea real
        self._live_account_warning()
        # Añadimos los símbolos a la lista de símbolos del marketwatch
        self._add_symbols_to_marketwatch(self.symbols)
        # Imprimimos la información de la cuenta
        self._print_account_info()

        # Comprobamos que el algoritmo de trading este habilitado
        self._check_algo_trading_enabled()

    def _inicialize_platform(self) -> None:
        """
        Initialize the platform


        """

        path = os.getenv("MT5_PATH")
        if path is None:
            raise Exception(f"Path not found {path=}")

        login = os.getenv("MT5_LOGIN")
        if login is None:
            raise Exception(f"Login not found {login=}")
        login = int(login)

        password = os.getenv("MT5_PASSWORD")
        if password is None:
            raise Exception(f"Password not found {password=}")

        server = os.getenv("MT5_SERVER")
        if server is None:
            raise Exception(f"Server not found {server=}")

        timeout = os.getenv("MT5_TIMEOUT")
        if timeout is None:
            timeout = 30
        else:
            timeout = int(timeout)

        portable = os.getenv("MT5_PORTABLE")
        if portable is None:
            portable = False
        else:
            portable = eval(portable)

        if mt5.initialize(
            path=path,
            login=login,
            password=password,
            server=server,
            timeout=timeout,
            portable=portable,
        ):
            print("Platform successfully initialized")
        else:
            raise Exception(f"Platform initialization failed {mt5.last_error()}")

    def _live_account_warning(self) -> None:

        account_info = mt5.account_info()

        if account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO:
            print("Account mode DEMO")
        elif account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_REAL:
            if (
                not input(
                    "Waring account type real do you want to continue? (y/n)"
                ).lower()
                == "y"
            ):
                mt5.shutdown()
                raise Exception("User cancelled")
        else:
            print("Account mode CONCURSO")

    def _check_algo_trading_enabled(self) -> None:
        if not mt5.terminal_info().trade_allowed:
            raise Exception("Trading not allowed")

    def _add_symbols_to_marketwatch(self, symbols: list[str]) -> None:
        # Comprobamos si el símbolo ya esta visible en el market watch
        # Si no lo esta lo añadimos
        for symbol in symbols:
            if not mt5.symbol_info(symbol):
                print(f"Symbol {symbol} not found {mt5.last_error()}")
                continue

            if not mt5.symbol_info(symbol).visible or mt5.symbol_info(symbol):
                if not mt5.symbol_select(symbol, True):
                    print(f"Symbol {symbol} not found {mt5.last_error()}")
                else:
                    print(f"Symbol {symbol} added to marketwatch")
            else:
                print(f"Symbol {symbol} already added to marketwatch")

    def _print_account_info(self) -> None:

        account_info: dict[str, str] = mt5.account_info()._asdict()

        print("--------- Account Info ---------")
        print(f"ID account: {account_info['login']}")
        print(f"Trader Name: {account_info['name']}")
        print(f"Broker: {account_info['company']}")
        print(f"Servidor: {account_info['server']}")
        print(f"Leverage: {account_info['leverage']}")
        print(f"Currency account: {account_info['currency']}")
        print(f"Balance Account {account_info['balance']}")
        print("--------------------------------")
