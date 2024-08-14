from logging import getLogger
from typing import Any

from pydantic import BaseModel

logger = getLogger(__name__)


class FilterToQueryMapper:
    field_map: dict[str | tuple[str, ...], Any] = {}
    body_filters: BaseModel
    context: dict[str, Any]

    def __init__(self, body_filters: BaseModel, context: dict[str, Any] | None = None):
        self.body_filters = body_filters
        self.context = context or {}

    def filter_params(self):
        filter_list = []
        for fields, field_map_value in self.field_map.items():
            if isinstance(fields, str):
                fields = (fields,)

            if not all([field in self.body_filters.model_fields.keys() for field in fields]):
                logger.warning(
                    f"fields {fields} does not exists in model {self.body_filters.__class__.__name__}",
                )
                continue

            if not field_map_value:
                logger.warning(f"field_map_value {field_map_value} for fields {fields} is falsy")
                continue

            body_filters_dict = self.body_filters.model_dump()
            body_filters_values = [body_filters_dict[field] for field in fields]
            filter_list += self._get_filter_list(body_filters_values, field_map_value)
        return filter_list

    def _get_filter_list(
        self,
        values: list[Any],
        map_value: Any,
    ) -> list[Any]:
        if callable(map_value):
            if not all(values):
                return []
            result = map_value(self, *values)
            if isinstance(result, list):
                return result
            if result is not None:
                return [
                    result,
                ]
            return []
        filter_list = []
        for value in values:
            if value is None:
                continue
            if isinstance(value, list):
                filter_list.append(map_value.in_(value))
            else:
                filter_list.append(map_value == value)
        return filter_list
