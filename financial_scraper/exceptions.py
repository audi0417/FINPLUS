class FinancialScraperError(Exception):
    pass

class InvalidTypeError(FinancialScraperError):
    def __init__(self, message="Invalid financial statement type."):
        self.message = message
        super().__init__(self.message)