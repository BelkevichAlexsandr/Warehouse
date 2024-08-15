from app.databases.dao.base_dao import BaseDAO
from app.models import Manufacturer


class ManufacturerDAO(BaseDAO):
    model = Manufacturer
