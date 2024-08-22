import requests
import pandas as pd
import time
from datetime import datetime
from io import StringIO
from .exceptions import InvalidTypeError

class FinancialScraper:
    def __init__(self, stock_id, start_date, end_date):
        """
        Initializes a FinancialScraper object with the given stock_id, start_date, and end_date.

        Args:
            stock_id (str): The ID of the stock to scrape.
            start_date (str or datetime): The start date of the period to scrape.
            end_date (str or datetime): The end date of the period to scrape.

        Raises:
            ValueError: If start_date is later than end_date.
        """
        self.stock_id = stock_id
        self.start_date = self._parse_date(start_date)
        self.end_date = self._parse_date(end_date)
        self._validate_date_range()

    def _parse_date(self, date):
        """Parses the input date into a datetime object."""
        return datetime.strptime(date, '%Y-%m-%d') if isinstance(date, str) else date

    def _validate_date_range(self):
        """Validates that the start date is not later than the end date."""
        if self.start_date > self.end_date:
            raise ValueError("start_date must be earlier than end_date")

    def _generate_quarters(self):
        """
        Generates a list of quarters based on the start and end dates.

        Returns:
            list: A list of tuples where each tuple represents a quarter (year, season).
        """
        quarters = []
        current_date = self.start_date

        while current_date <= self.end_date:
            year, season = current_date.year, self._get_season(current_date.month)
            quarters.append((year, season))
            current_date = self._advance_to_next_quarter(current_date, season)

        return quarters

    @staticmethod
    def _get_season(month):
        """Returns the season (1-4) based on the month."""
        return (month - 1) // 3 + 1

    @staticmethod
    def _advance_to_next_quarter(current_date, season):
        """Advances the date to the beginning of the next quarter."""
        return datetime(year=current_date.year + (season == 4), month=1 if season == 4 else season * 3 + 1, day=1)

    def fetch_financial_data(self, year, season):
        """
        Fetches the financial data for a given year and season.

        Args:
            year (int): The year for which to fetch financial data.
            season (int): The season (1 for Q1, 2 for Q2, etc.) for which to fetch financial data.

        Returns:
            str: The financial data as a string.
        """
        url = f'https://mops.twse.com.tw/server-java/t164sb01?step=1&CO_ID={self.stock_id}&SYEAR={year}&SSEASON={season}&REPORT_ID=C#'
        response = requests.post(url)
        response.encoding = 'big5'
        return response.text

    def parse_financial_data(self, html, statement_type):
        """
        Parses the HTML financial data into a DataFrame.

        Args:
            html (str): The HTML string of the financial data.
            statement_type (str): The type of financial statement to parse.

        Returns:
            pandas.DataFrame: A DataFrame containing the financial data with the first two columns as the index.

        Raises:
            InvalidTypeError: If the statement type is invalid.
        """
        statement_types = {'資產負債表': 0, '綜合損益表': 1, '現金流量表': 2}
        if statement_type not in statement_types:
            raise InvalidTypeError(f"Invalid statement type: {statement_type}")

        df = pd.read_html(StringIO(html))[statement_types[statement_type]]
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel()

        df = df.iloc[:, :3].set_index(df.columns[:2].tolist())
        df.columns = ['season']

        return df

    def get_financial_statements(self, statement_type=None):
        """
        Fetches and combines financial data for all quarters within the specified date range.

        Args:
            statement_type (str): The type of financial statement to fetch and parse.

        Returns:
            pandas.DataFrame: A DataFrame containing combined financial data for the specified date range.
        """
        all_data, index_df = {}, None

        for year, season in self._generate_quarters():
            print(f"Fetching data for {year} Q{season}...")
            html = self.fetch_financial_data(year, season)
            time.sleep(5)
            df = self.parse_financial_data(html, statement_type)
            df.columns = [f"{year}Q{season}"]

            if index_df is None:
                index_df = df.index
            else:
                index_df = index_df.union(df.index)

            all_data[f"{year}Q{season}"] = df

        combined_df = pd.concat(all_data.values(), axis=1, join='outer').reindex(index_df).dropna(how='all')
        return combined_df
