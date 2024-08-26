from app.databases.dao.base_dao import BaseDAO
from app.models import SerialNumber


class SerialNumberDAO(BaseDAO):
    model = SerialNumber