from rest_framework.pagination import PageNumberPagination


class FlexiblePagination(PageNumberPagination):
    """
    Pagination class that allows clients to override page size
    via a `page_size` query parameter (capped at 500).
    Default: 20 results per page.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 500
