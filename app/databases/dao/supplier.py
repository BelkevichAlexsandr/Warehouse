from app.databases.dao.base_dao import BaseDAO
from app.models import Supplier


class SupplierDAO(BaseDAO):
    model = Supplier
