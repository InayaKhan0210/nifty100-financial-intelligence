# Nifty100 Financial Intelligence

## Overview

Nifty100 Financial Intelligence is a Python-based financial analytics project that extracts, validates, stores, and analyzes financial data of Nifty 100 companies. The project follows a modular ETL architecture and generates financial metrics that can be used for company analysis, investment research, and business intelligence applications.

The objective of this project is to demonstrate data engineering, financial analytics, and software engineering practices by building an end-to-end data pipeline from raw Excel datasets to processed analytical outputs.

---

## Objectives

The project aims to:

- Build a reusable ETL pipeline for financial datasets.
- Validate and normalize raw financial data.
- Store structured data in a relational SQLite database.
- Compute important financial metrics using Python.
- Generate processed datasets for reporting and visualization.
- Provide a scalable foundation for dashboards and analytical applications.

---

## Technology Stack

Programming Language

- Python 3.x

Libraries

- pandas
- sqlite3
- pathlib

Database

- SQLite

Development Environment

- Visual Studio Code
- Git
- GitHub

---

## Project Structure

```text
nifty100-financial-intelligence/

│── data/
│   ├── raw/
│   ├── processed/
│   └── database/

│── src/
│   ├── analytics/
│   ├── database/
│   └── etl/

│── requirements.txt
│── README.md
│── .gitignore
```

---

## ETL Pipeline

The ETL pipeline is responsible for importing, validating, and storing financial datasets.

### Data Loading

The loader module imports financial datasets from the raw data directory.

Datasets currently supported include:

- Companies
- Profit and Loss
- Balance Sheet
- Cash Flow
- Analysis
- Documents
- Pros and Cons
- Sectors
- Stock Prices
- Market Capitalization
- Financial Ratios
- Peer Groups

### Data Normalization

Normalization includes:

- Standardized company identifiers
- Standardized year formats
- Consistent dataset structure

### Data Validation

Validation currently performs:

- Required column validation
- Duplicate record detection

Validation reports are exported for further inspection.

---

## Database

Financial data is stored in SQLite.

Current database tables include:

- companies
- profitandloss
- balancesheet
- cashflow
- analysis
- documents
- prosandcons
- sectors
- stock_prices
- market_cap
- financial_ratios
- peer_groups

---

## Financial Analytics

The analytics module contains implementations of financial metrics.

### Currently Implemented

- Operating Profit
- Operating Profit Validation
- Operating Profit Margin
- Net Profit Margin

Calculated outputs are exported to the `data/processed` directory.

---

## Project Status

### Sprint 1

Completed

- Project setup
- ETL pipeline
- Data normalization
- Data validation
- SQLite schema
- Database loader

### Sprint 2

Completed

- Operating Profit
- Operating Profit Margin
- Net Profit Margin

---

## Planned Enhancements

The following financial metrics will be implemented in subsequent sprints.

- Return on Equity (ROE)
- Return on Capital Employed (ROCE)
- Debt-to-Equity Ratio
- Current Ratio
- Quick Ratio
- Revenue Growth
- Profit Growth
- Earnings Growth
- Financial Trend Analysis

Future enhancements will include:

- Interactive dashboard
- Company comparison
- Data visualization
- Automated reporting
- Financial scoring model

---

## Installation

Clone the repository.

```bash
git clone https://github.com/InayaKhan0210/nifty100-financial-intelligence.git
```

Navigate to the project directory.

```bash
cd nifty100-financial-intelligence
```

Create a virtual environment.

```bash
python -m venv .venv
```

Activate the environment.

Windows

```bash
.venv\Scripts\activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

## Author

Inaya Khan

Bachelor of Technology in Electronics and Computer Engineering

GitHub

https://github.com/InayaKhan0210