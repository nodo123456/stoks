# Connect Initiated: IBKR Docker Setup Guide

This guide documents how to set up a Dockerized Interactive Brokers (IBKR) Gateway that persists authentication and settings across restarts, and how to connect to it using Python.

## 1. Prerequisites
-   **Docker Desktop** installed and running.
-   **Python 3.9+** (recommended).
-   **IBKR Paper Trading Account** credentials.

## 2. Project Structure
The project is split into two microservices:
```
/stocks
  ├── gateway/
  │   ├── docker-compose.yml   # Runs the IBKR Gateway
  │   ├── .env                 # Credentials
  │   └── ibkr_config/         # Persisted settings
  │
  └── app/
      ├── docker-compose.yml   # Runs the Client App
      ├── Dockerfile
      ├── src/
      │   ├── connect_ibkr.py
      │   └── requirements.txt
      └── balance.txt          # Output file
```

## 3. Usage
We use a shared network (`trading-net`) so the app can talk to the gateway.

### One-Time Network Setup
```bash
docker network create trading-net
```

### Step 1: Start the Gateway
```bash
cd gateway
docker-compose up -d
```
*Wait for it to fully start (check http://localhost:6080).*

### Step 2: Start the App
```bash
cd ../app
docker-compose up --build -d
```
The app will connect automatically and save output to `app/db/`:
- `balance.txt`: Current account balance.
- `logs/run_YYYY-MM-DD_HH-MM-SS.log`: Detailed execution log for this specific run.




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
