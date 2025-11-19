from datetime import date

class PricingStrategy:
    def calculate_price(self, caravan, start_date: date, end_date: date) -> float:
        raise NotImplementedError

class StandardPricingStrategy(PricingStrategy):
    def calculate_price(self, caravan, start_date: date, end_date: date) -> float:
        # Simple pricing: $100 per day
        num_days = (end_date - start_date).days + 1
        return num_days * 100.0
