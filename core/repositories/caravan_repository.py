from core.models import Caravan

class CaravanRepository:
    def get_by_id(self, caravan_id: int) -> Caravan:
        pass

    def find_available(self, start_date, end_date, capacity: int):
        pass
