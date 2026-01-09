from ib_insync import *
import pandas as pd
import time
import logging

# Create IB instance
ib = IB()

def connect_to_ibkr():
    """Connects to the IBKR Gateway (Scans ports 7496, 7497, 4001, 4002)"""
    print("Attempting to connect to IBKR Gateway...")
    
    ports = [7496, 7497, 4001, 4002]
    util.logToConsole(level=logging.INFO)
    
    for port in ports:
        print(f"Connecting to {port}...")
        try:
            # Increased timeout to 10s to give time for manual manual acceptance if needed
            ib.connect('127.0.0.1', port, clientId=998, timeout=10)
            print(f"Successfully connected on port {port}!")
            return True
        except Exception as e:
            print(f"Failed on {port}: {e}")
            
    print("All connection attempts failed.")
    print("Ensure Docker is running and fully logged in (check http://localhost:6080)")
    return False

def fetch_data(symbol_str):
    """Fetches historical data for a given symbol"""
    if not ib.isConnected():
        print("IB is not connected.")
        return

    print(f"\nFetching data for {symbol_str}...")
    
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
        print(f"Retrieved {len(df)} records.")
        print(df.head())
        
        # Save to CSV for convenience
        filename = f"{symbol_str}_history.csv"
        df.to_csv(filename, index=False)
        print(f"Saved to {filename}")
    else:
        print("No data found.")

def print_account_details():
    """Prints account summary information"""
    print("\nFetching Account Summary...")
    # accountSummary returns a list of AccountSummary objects
    # Tags: NetLiquidation, TotalCashValue, SettledCash, BuyingPower, etc.
    summary = ib.accountSummary()
    
    found_data = False
    for item in summary:
        if item.tag in ['NetLiquidation', 'TotalCashValue', 'BuyingPower', 'AvailableFunds']:
            print(f"{item.tag}: {item.value} {item.currency}")
            found_data = True
            
    if not found_data:
        print("No summary data received. (Wait a moment for data to stream or check permissions)")
        
    print(f"Managed Accounts: {ib.managedAccounts()}")

if __name__ == "__main__":
    if connect_to_ibkr():
        # Fetch Account Data
        print_account_details()
        
        # Example: Fetch Apple stock data
        fetch_data('AAPL')
        
        # Keep the script running to receive events if needed, 
        # or disconnect if just a one-off pull
        # ib.sleep(1) 
        ib.disconnect()
        print("\nDisconnected.")
