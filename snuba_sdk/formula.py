from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Optional, Sequence, Union, Any

from snuba_sdk.aliased_expression import AliasedExpression
from snuba_sdk.column import Column
from snuba_sdk.conditions import BooleanCondition, Condition, ConditionGroup
from snuba_sdk.expressions import Expression, InvalidExpressionError, list_type
from snuba_sdk.timeseries import Timeseries


class InvalidArithmeticError(InvalidExpressionError):
    pass


class InvalidFormulaError(InvalidExpressionError):
    pass


class ArithmeticOperator(Enum):
    PLUS = "plus"
    MINUS = "minus"
    MULTIPLY = "multiply"
    DIVIDE = "divide"


@dataclass(frozen=True)
class Formula(Expression):
    operator: str
    parameters: Optional[
        Sequence[
            Union[Formula, Timeseries, float, int]
        ]
    ] = None
    filters: Optional[ConditionGroup] = None
    groupby: Optional[list[Column | AliasedExpression]] = None

    def validate(self) -> None:
        if not isinstance(self.operator, str):
            raise InvalidFormulaError(f"formula '{self.operator}' must be a string")
        if self.operator == "":
            raise InvalidFormulaError("operator cannot be empty")
        if self.operator not in [op.value for op in ArithmeticOperator]:
            raise InvalidFormulaError(
                f"operator '{self.operator}' is not supported"
            )

        if self.parameters is not None:
            if not isinstance(self.parameters, Sequence):
                raise InvalidFormulaError(
                    f"parameters of formula {self.operator} must be a Sequence"
                )
            for param in self.parameters:
                if not isinstance(param, (Formula, Timeseries, float, int)):
                    raise InvalidFormulaError(
                        f"parameter '{param}' of formula {self.operator} is an invalid type"
                    )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Formula):
            return False

        return (
            self.operator == other.operator
            and self.parameters == other.parameters
            and self.filters == other.filters
            and self.groupby == other.groupby
        )

    def _replace(self, field: str, value: Any) -> Formula:
        new = replace(self, **{field: value})
        return new

    def set_filters(self, filters: ConditionGroup | None) -> Formula:
        if filters is not None and not list_type(
            filters, (BooleanCondition, Condition)
        ):
            raise InvalidFormulaError("filters must be a list of Conditions")
        return self._replace("filters", filters)

    def set_groupby(
        self, groupby: list[Column | AliasedExpression] | None
    ) -> Formula:
        if groupby is not None and not list_type(groupby, (Column, AliasedExpression)):
            raise InvalidFormulaError("groupby must be a list of Columns")
        return self._replace("groupby", groupby)
