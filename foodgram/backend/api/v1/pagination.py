from rest_framework.pagination import LimitOffsetPagination


class PagePagination(LimitOffsetPagination):
    page_query_param = 'page'
    page_size = 5

    def get_offset(self, request):
        page = request.query_params.get(self.page_query_param)
        if page and page.isdigit():
            page_num = int(page)
            if page_num > 0:
                limit = self.get_limit(request)
                if limit is None:
                    limit = self.page_size
                return (page_num - 1) * limit
        return super().get_offset(request)
