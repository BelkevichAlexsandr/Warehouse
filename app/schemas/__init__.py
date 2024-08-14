from typing import TypeAlias

from annotated_types import Ge, Le
from typing_extensions import Annotated

ID_INT: TypeAlias = Annotated[int, Ge(1), Le(2147483647)]