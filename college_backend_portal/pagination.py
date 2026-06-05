from rest_framework.pagination import PageNumberPagination


class FlexiblePagination(PageNumberPagination):
    """
    Pagination class that allows clients to override page size
    by default display only 20 items per page
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 500
