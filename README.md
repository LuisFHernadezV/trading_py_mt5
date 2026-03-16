# TradingPy

TradingPy is a Python-based trading framework that integrates various components to facilitate algorithmic trading. It provides functionalities for signal generation, order execution, risk management, and real-time notifications. This code is derived from the teachings of the [Trading con Python y MetaTrader 5](https://www.udemy.com/course/trading-con-python-y-metatrader-5/?referralCode=855DE347A9E8D6713F2A) course, which provided invaluable insights and guidance.

## Features

- **Signal Generation**: Utilize advanced algorithms like Moving Average Crossover to generate trading signals.
- **Order Execution**: Execute trades based on generated signals and current market conditions.
- **Risk Management**: Manage trading risks using customizable risk factors.
- **Real-Time Notifications**: Receive trading alerts and updates via Telegram notifications.

## Requirements

- Python 3.8+
- Telegram Bot Token and Chat ID for notifications

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/LuisFHernadezV/trading_py_mt5.git
   cd tradingpy
   ```

2. Set up a virtual environment:
   ```bash
   uv init
   uv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```bash
   uv sync
   ```

4. Set up environment variables for Telegram:
   Create a `.env` file at the root of the project and add your Telegram Token and Chat ID:
   ```env
   TELEGRAM_TOKEN=your_telegram_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

## Usage

1. Run the main script:
   ```bash
   uv run trading_app.py
   ```

This will initialize the trading system and start processing market data for the specified symbols.

## Contributing

We welcome contributions! Please fork the repository and submit a pull request for any enhancements, bug fixes, or new features.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

