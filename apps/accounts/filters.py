from django.contrib import admin

# using filter for giving the permission for soft delete model in admin


class SoftDeleteListFilter(admin.SimpleListFilter):
    title = "Trash Status"
    parameter_name = "is_deleted"

    def lookups(self, request, model_admin):
        return (
            (None, "Active"),
            ("all", "All"),
            ("1", "Trash (Deleted)"),
        )

    def choices(self, cl):
        for lookup, title in self.lookups(None, None):
            yield {
                "selected": self.value() == lookup,
                "query_string": cl.get_query_string({self.parameter_name: lookup}, []),
                "display": title,
            }

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(is_deleted=True)
        if self.value() == "all":
            return queryset
        if self.value() is None:
            return queryset.filter(is_deleted=False)
        return queryset
