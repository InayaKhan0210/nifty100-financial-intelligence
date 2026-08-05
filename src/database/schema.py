import sqlite3
from pathlib import Path

DB_PATH = Path("data/database/nifty100.db")


def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # =========================
    # Core Tables
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id TEXT PRIMARY KEY,
        company_name TEXT,
        sector TEXT,
        industry TEXT,
        market_cap REAL,
        current_price REAL,
        book_value REAL,
        roce_percentage REAL,
        roe_percentage REAL,
        face_value REAL,
        website TEXT,
        about_company TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profitandloss (
        company_id TEXT,
        year TEXT,
        sales REAL,
        expenses REAL,
        operating_profit REAL,
        opm_percentage REAL,
        other_income REAL,
        interest REAL,
        depreciation REAL,
        profit_before_tax REAL,
        tax_percentage REAL,
        net_profit REAL,
        eps REAL,
        dividend_payout REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS balancesheet (
        company_id TEXT,
        year TEXT,
        equity REAL,
        reserves REAL,
        borrowings REAL,
        other_liabilities REAL,
        total_liabilities REAL,
        fixed_assets REAL,
        investments REAL,
        other_assets REAL,
        total_assets REAL,
        cwip REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cashflow (
        company_id TEXT,
        year TEXT,
        operating_activity REAL,
        investing_activity REAL,
        financing_activity REAL,
        net_cash_flow REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis (
        company_id TEXT,
        metric TEXT,
        period TEXT,
        value TEXT,
        remarks TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        company_id TEXT,
        year TEXT,
        report_type TEXT,
        url TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prosandcons (
        company_id TEXT,
        type TEXT,
        description TEXT,
        source TEXT
    )
    """)

    # =========================
    # Supplementary Tables
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sectors (
        company_id TEXT,
        sector TEXT,
        industry TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_prices (
        company_id TEXT,
        date TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS market_cap (
        company_id TEXT,
        year TEXT,
        market_cap REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financial_ratios (
        company_id TEXT,
        year TEXT,
        ratio_name TEXT,
        ratio_value REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS peer_groups (
        company_id TEXT,
        peer_company TEXT
    )
    """)

    conn.commit()
    conn.close()

    print("Database created successfully.")


if __name__ == "__main__":
    create_database()