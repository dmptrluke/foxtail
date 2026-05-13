class OrderedInlineFormSetMixin:
    """Assign sequential order values to orderable inline formset rows when needed."""

    order_field_name = 'order'

    def _active_ordered_forms(self):
        for form in self.forms:
            if not hasattr(form, 'cleaned_data') or not form.cleaned_data:
                continue
            if self.can_delete and self._should_delete_form(form):
                continue
            yield form

    def _assign_fallback_orders(self):
        for fallback_order, form in enumerate(self._active_ordered_forms()):
            order = form.cleaned_data.get(self.order_field_name)
            if order in (None, ''):
                order = fallback_order
                form.cleaned_data[self.order_field_name] = order
                setattr(form.instance, self.order_field_name, order)

    def clean(self):
        super().clean()
        self._assign_fallback_orders()

    def save(self, commit=True):
        self._assign_fallback_orders()
        return super().save(commit=commit)
