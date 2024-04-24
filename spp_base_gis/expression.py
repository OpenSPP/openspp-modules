from odoo.models import BaseModel
from odoo.osv import expression
from odoo.osv.expression import TERM_OPERATORS
from odoo.tools import SQL

from .fields import GeoField
from .operators import Operator

GIS_OPERATORS = list(Operator.OPERATION_TO_RELATION.keys())

term_operators_list = list(TERM_OPERATORS)
for op in GIS_OPERATORS:
    term_operators_list.append(op)

expression.TERM_OPERATORS = tuple(term_operators_list)

original__leaf_to_sql = expression.expression._expression__leaf_to_sql


class CustomExpression(expression.expression):
    def __leaf_to_sql(self, leaf: tuple, model: BaseModel, alias: str) -> SQL:
        """
        The function `__leaf_to_sql` processes a leaf tuple to generate a SQL query for a GeoField in a
        BaseModel.

        :param leaf: The `leaf` parameter is a tuple containing three elements: the left operand, the
        comparison operator, and the right operand
        :type leaf: tuple
        :param model: The `model` parameter in the given code snippet refers to an instance of a
        BaseModel class. It is used to access fields and their properties within the model. The
        BaseModel class likely represents a data model or entity in the application, and it contains
        information about the fields and their types that are used to
        :type model: BaseModel
        :param alias: The `alias` parameter in the `__leaf_to_sql` method is a string that represents an
        alias for the table in the SQL query. It is used to specify a shorthand name for the table in
        the query to make the query more readable and to avoid naming conflicts when joining multiple
        tables in a
        :type alias: str
        :return: The code snippet provided is a method named `__leaf_to_sql` that takes in parameters
        `leaf` (a tuple), `model` (an instance of `BaseModel`), and `alias` (a string), and returns an
        object of type `SQL`.
        """
        if isinstance(leaf, list | tuple):
            left, operator, right = leaf
            field = model._fields.get(left)
            if field and isinstance(field, GeoField):
                if operator in GIS_OPERATORS:
                    operator_obj = Operator(field)
                    return operator_obj.domain_query(operator, right)

        return original__leaf_to_sql(self, leaf, model, alias)


expression.expression._expression__leaf_to_sql = CustomExpression._CustomExpression__leaf_to_sql
