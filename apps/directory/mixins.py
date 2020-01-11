from braces.views import OrderableListMixin


class MultipleOrderableListMixin(OrderableListMixin):
    def get_ordered_queryset(self, queryset=None):
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
                _order.append("-" + column)
            else:
                _order.append(column)

        return queryset.order_by(*_order)
