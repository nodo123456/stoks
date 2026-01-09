# Connect Initiated: IBKR Docker Setup Guide

This guide documents how to set up a Dockerized Interactive Brokers (IBKR) Gateway that persists authentication and settings across restarts, and how to connect to it using Python.

## 1. Prerequisites
-   **Docker Desktop** installed and running.
-   **Python 3.9+** (recommended).
-   **IBKR Paper Trading Account** credentials.

## 2. Project Structure
Ensure your project has the following structure:
```
/project-root
  ├── docker-compose.yml   # Defines the IBKR container
  ├── .env                 # Stores sensitive credentials (TWS_USERID, etc.)
  ├── requirements.txt     # Python dependencies (ib_insync, pandas)
  ├── connect_ibkr.py      # Python client script
  └── ibkr_config/         # Local folder for persisting TWS settings (Auto-created)
```

## 3. Configuration

### `.env` File
Create a `.env` file with your credentials:
```bash
TWS_USERID=your_paper_username
TWS_PASSWORD=your_paper_password
TRADING_MODE=paper
VNC_SERVER_PASSWORD=password
```

### `docker-compose.yml`
Ensure the `volumes` section is enabled to save settings to your local machine:
```yaml
services:
  ibkr:
    image: ghcr.io/extrange/ibkr:latest
    container_name: ibkr-gateway
    environment:
      - USERNAME=${TWS_USERID}
      - PASSWORD=${TWS_PASSWORD}
      - TRADING_MODE=${TRADING_MODE:-paper}
      - VNC_SERVER_PASSWORD=${VNC_SERVER_PASSWORD:-password}
    ports:
      - "7497:7497"  # API Port
      - "6080:6080"  # VNC (GUI) Port
    volumes:
      - ./ibkr_config:/root/Jts # CRITICAL: Persists settings
```

## 4. Initial Setup (The "One-Time" Fix)
This step is only required the **first time** you set this up or if you wipe the `ibkr_config` folder.

1.  **Start Docker**:
    ```bash
    docker-compose up -d
    ```
2.  **Access VNC**:
    Open your browser to `http://localhost:6080`.
    Password: `password` (or whatever you set in `.env`).

3.  **Handle Popups**:
    -   Wait for the login to complete.
    -   Dismiss any "Market Data" or "Safety" popups.

4.  **Configure API (Crucial!)**:
    -   In the TWS window, go to **File > Global Configuration > API > Settings**.
    -   **Enable ActiveX and Socket Clients**: CHECKED.
    -   **Allow connections from localhost only**: **UNCHECKED**.
    -   **Trusted IPs**:
        -   Click "Create" and add `0.0.0.0` (This allows Docker network connections).
        -   Alternatively, add your specific Docker Gateway IP if `0.0.0.0` feels too permissive, but `0.0.0.0` is easiest for local dev.
    -   Click **Apply** and **OK**.

**Note on Persistence**: Because we mounted the volume (`./ibkr_config`), these settings are now saved to your hard drive. You can restart the container without losing them.

## 5. Connecting with Python

### Install Dependencies
```bash
pip install -r requirements.txt
```
*(Requires `ib_insync` and `pandas`)*

### Run the Script
```bash
python connect_ibkr.py
```

### Connection Code Snippet
The script connects to port `7497` (typical for Paper Trading) or `7496` (Live Trading).
```python
from ib_insync import *
ib = IB()
# Connect to the local Docker container on port 7497 (Paper)
ib.connect('127.0.0.1', 7497, clientId=1)
```

## 6. Troubleshooting

### "Connection reset by peer" / "Timeout"
-   **Cause**: TWS is running but blocking the connection.
-   **Fix**:
    1.  Check `http://localhost:6080`. Is there a popup blocking the screen? Close it.
    2.  Check API Settings: Is "Allow connections from localhost only" **unchecked**?
    3.  Did you add `0.0.0.0` to Trusted IPs?

### Container Crashes on Start
-   **Cause**: Incorrect permissions on the mounted volume.
-   **Fix**:
    ```bash
    chmod -R 777 ibkr_config/
    docker-compose restart
    ```

### Settings Not Saving
-   **Cause**: The `volumes` section in `docker-compose.yml` is commented out or missing.
-   **Fix**: Uncomment it and ensure `ibkr_config` exists.
