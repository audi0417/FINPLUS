# FINPLUS/pricing/export_to_excel.py

import pandas as pd
from FINPLUS.crawler import StockPriceFetcher

class ExportToExcel:
    def __init__(self, fetcher: StockPriceFetcher):
        self.fetcher = fetcher

    def export(self, file_path: str, include_summary: bool = True):
        df = self.fetcher.to_dataframe()
        
        with pd.ExcelWriter(file_path) as writer:
            df.to_excel(writer, sheet_name='Stock Prices')

            if include_summary:
                summary = df.groupby('Stock').agg({'Close': ['mean', 'min', 'max']})
                summary.to_excel(writer, sheet_name='Summary')
