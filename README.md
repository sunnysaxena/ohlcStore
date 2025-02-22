# Market Data Repository

This repository is designed to fetch and store OHLC (Open, High, Low, Close) data from the Fyers API and save it into multiple databases (MySQL, InfluxDB, and TimescaleDB) for efficient storage, retrieval, and analysis.
 
### Key Features:
* Stores 1-minute and 1-day interval OHLC data.
* Covers NIFTY 50, Bank NIFTY, Midcap NIFTY, and FINNIFTY indices.
* Supports multiple databases:
  * MySQL (Relational storage, structured queries)
  * InfluxDB (Time-series optimized storage)
  * TimescaleDB (PostgreSQL extension for scalable time-series data)
* Enables backtesting and data analysis for algorithmic trading.

This project serves as a data pipeline for traders and analysts who need accurate historical market data for strategy development, risk management, and performance evaluation.

### Installation:
1. Clone the repository:
   ```bash
   git clone git@github.com:sunnysaxena/ohlcStore.git
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
3. Set up the databases:
   * MySQL: Create a database and table using the `mysql.sql` script.
   * InfluxDB: Create a database using the InfluxDB CLI.
   * TimescaleDB: Create a hypertable using the `timescaledb.sql` script.
4. Set up the Fyers API:
   * Create an account on the Fyers website and generate API keys.
   * Create a `credentials.ini` and `.env` file in the `config` directory.
   * Update the database credentials and API key in the `.env` and `credentials.ini` file.

5. Generate the required API token.
    * Run the `generate_token.py` script to generate the API token.
    * Update the token in the `credentials.ini` file.

6. Run the data ingestion script end of the day to fetch and store the OHLC data.
   ```bash
    python update_tables_1m.py
    python update_tables_1D.py
   
### Usage:
* Run the data ingestion script to fetch and store the OHLC data.
* Use SQL queries to analyze the data stored in the databases.
* Integrate the data with trading algorithms for backtesting and live trading.
* Modify the script to fetch data for specific indices or time intervals.
* Automate the data ingestion process using cron jobs or schedulers.
* Use stored data for backtesting, technical analysis, or strategy optimization.
* Visualize the data using tools like Grafana, Tableau, or Matplotlib.

### Contributing
Feel free to submit issues, feature requests, or contribute by opening pull requests.

### License
This project is licensed under the MIT License. See the LICENSE file for details.
