# Retail Intelligence: Sales & Business Intelligence Dashboard

## Project overview
An interactive analytics dashboard that transforms retail order-line data into business performance insights. It supports exploration of revenue, profit, order volume, average order value, profit margin, regional results, product performance, customer segments, and discount-profit patterns.

## Business questions
1. How are revenue and profit changing over time?
2. Which regions and product groups contribute most to sales and profit?
3. Which sub-categories/products are loss-making?
4. How do discounts relate to observed profit?
5. Which customer segments contribute most to profit?

## Dataset and attribution
Dataset: Sample Superstore transaction data.  
Source: https://github.com/valiotti/plotly-superstore/blob/main/superstore.csv  
Raw CSV used by the app: https://raw.githubusercontent.com/valiotti/plotly-superstore/main/superstore.csv  
Alternative source: https://www.kaggle.com/datasets/vivek468/superstore-dataset-final

The dashboard attempts to load the CSV from the raw public source. For offline use, download the CSV and save it beside `app.py` as `superstore.csv`.

## Tech stack
- Python
- Pandas for data preparation and aggregation
- Streamlit for interactive dashboard
- Plotly Express for interactive charts

## Data preparation
- Standardize column labels by trimming whitespace
- Convert order dates and numeric measures to appropriate data types
- Remove rows missing essential date/sales/profit/quantity values
- Remove duplicate rows
- Exclude negative sales and non-positive quantities
- Derive order month and profit margin for analysis

Data-cleaning choices are documented in `app.py`. Inspect source data and assess the impact of these rules if adapting this project for real business use.

## Dashboard sections
1. Executive Overview: headline KPIs, monthly sales, regional sales/profit and category performance
2. Product & Profitability: sub-category profit, discount-profit relationship, best revenue products and lowest-profit products
3. Business Insights: regional margins, filter-responsive findings and suggested actions
Global filters: date, region, category, customer segment. Filtered data can be downloaded as CSV.

## Run locally
1. Install Python 3.10+.
2. Open this folder in VS Code.
3. In the terminal, run:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   streamlit run app.py
   ```

   If PowerShell blocks activation, use `python -m pip install -r requirements.txt` and `.venv\Scripts\python -m streamlit run app.py` after creating the environment, or run commands in Command Prompt.

4. The browser should open the dashboard at the local Streamlit address.

## Repository structure
- `app.py` — complete dashboard and analysis logic
- `requirements.txt` — Python dependencies
- `README.md` — setup and documentation
- `Project_Report.pdf` — project report template; complete the observed-results section using your running dashboard screenshots

## Limitations
- The dataset is historical and based on its source context; results are not guaranteed to generalize to other businesses or markets.
- A correlation between discounts and profit does not prove discounting caused a profit change.
- Profit is used as provided in the dataset; accounting definitions and costs should be verified before operational use.
- This is descriptive analytics, not a forecasting or churn model.

## Responsible interpretation
Recommendations are investigation priorities, not causal claims. Verify with business owners and test proposed changes before implementation.
