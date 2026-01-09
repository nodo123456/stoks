from ib_insync import *
import pandas as pd
import time
import logging

import os

from datetime import datetime

# Create IB instance
ib = IB()

def setup_logging():
    """Configures logging to file and console"""
    os.makedirs("db/logs", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"db/logs/run_{timestamp}.log"
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler() # Keep console output as well
        ]
    )
    logging.info("Logging initialized. Writing to %s", log_file)

def connect_to_ibkr():
    """Connects to the IBKR Gateway (Scans ports 7496, 7497, 4001, 4002)"""
    host = os.environ.get('IBKR_HOST', '127.0.0.1')
    logging.info(f"Attempting to connect to IBKR Gateway at {host}...")
    
    ports = [7496, 7497, 4001, 4002]
    # Disable default ib_insync logging to console (since we handle it via root logger now)
    # util.logToConsole(level=logging.INFO) 
    
    max_retries = 30
    for i in range(max_retries):
        for port in ports:
            logging.info(f"Connecting to {host}:{port} (Attempt {i+1}/{max_retries})...")
            try:
                # Increased timeout to 10s to give time for manual manual acceptance if needed
                ib.connect(host, port, clientId=998, timeout=10)
                logging.info(f"Successfully connected on port {port}!")
                return True
            except Exception as e:
                logging.warning(f"Failed on {port}: {e}")
        
        logging.info("Waiting 5 seconds before retrying...")
        time.sleep(5)
            
    logging.error("All connection attempts failed.")
    return False

def fetch_data(symbol_str):
    """Fetches historical data for a given symbol"""
    if not ib.isConnected():
        logging.error("IB is not connected.")
        return

    logging.info(f"Fetching data for {symbol_str}...")
    
    # Define contract (Stock)
    # NOTE: You can change 'SMART' to a specific exchange if needed
    contract = Stock(symbol_str, 'SMART', 'USD')
    
    # Request historical data
    bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr='30 D',
        barSizeSetting='1 day',
        whatToShow='MIDPOINT',
        useRTH=True
    )
    
    if bars:
        # Convert to DataFrame
        df = util.df(bars)
        logging.info(f"Retrieved {len(df)} records.")
        
        # Ensure db directory exists
        os.makedirs("db", exist_ok=True)
        
        filename = f"db/{symbol_str}_history.csv"
        df.to_csv(filename, index=False)
        logging.info(f"Saved to {filename}")
    else:
        logging.warning("No data found.")

def print_and_save_account_details():
    """Prints account summary information and saves balance to file"""
    logging.info("Fetching Account Summary...")
    # accountSummary returns a list of AccountSummary objects
    # Tags: NetLiquidation, TotalCashValue, SettledCash, BuyingPower, etc.
    summary = ib.accountSummary()
    
    found_data = False
    balance_info = ""
    
    for item in summary:
        if item.tag in ['NetLiquidation', 'TotalCashValue', 'BuyingPower', 'AvailableFunds']:
            line = f"{item.tag}: {item.value} {item.currency}"
            logging.info(line)
            balance_info += line + "\n"
            found_data = True
            
    if not found_data:
        logging.warning("No summary data received. (Wait a moment for data to stream or check permissions)")
    else:
        # Save to file
        os.makedirs("db", exist_ok=True)
        with open("db/balance.txt", "w") as f:
            f.write(balance_info)
        logging.info("Saved balance info to db/balance.txt")
        
    logging.info(f"Managed Accounts: {ib.managedAccounts()}")

if __name__ == "__main__":
    setup_logging()
    if connect_to_ibkr():
        # Fetch Account Data
        print_and_save_account_details()
        
        # Example: Fetch Apple stock data
        fetch_data('AAPL')
        
        # Keep the script running to receive events if needed, 
        # or disconnect if just a one-off pull
        # ib.sleep(1) 
        ib.disconnect()
        logging.info("Disconnected.")
