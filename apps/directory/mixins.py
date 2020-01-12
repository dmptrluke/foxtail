from django.db.models import QuerySet, Value
from django.db.models.functions import NullIf

from braces.views import OrderableListMixin


class SortableDirectoryMixin(OrderableListMixin):
    """
    A modified version of the django-braces OrderableListMixin that makes two changes:

    * Allows for ordering by multiple columns at once using ~ as a joiner.
    * Always sorts rows with NULL and BLANK fields at the end.
    """

    def get_ordered_queryset(self, queryset: QuerySet = None):
        """
        Augments ``QuerySet`` with order_by statement if possible

        :param QuerySet queryset: ``QuerySet`` to ``order_by``
        :return: QuerySet
        """
        get_order_by = self.request.GET.get("order_by")

        if get_order_by in self.get_orderable_columns():
            self.order_by = get_order_by
        else:
            self.order_by = self.get_orderable_columns_default()

        self.ordering = self.request.GET.get("ordering", self.get_ordering_default())

        _order = []
        for column in self.order_by.split('~'):
            if self.request.GET.get("ordering", self.ordering) == "desc":
                _order.append(NullIf(column, Value('')).desc(nulls_last=True))
            else:
                _order.append(NullIf(column, Value('')).asc(nulls_last=True))

        return queryset.order_by(*_order)
