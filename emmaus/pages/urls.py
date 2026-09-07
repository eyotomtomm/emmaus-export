from django.urls import path
from pages.views import (root_page_view, dynamic_pages_view, enquiry_view)

app_name = "pages"

urlpatterns = [
    path('', root_page_view, name="dashboard"),
    # Must precede the catch-all below, which would otherwise swallow it.
    path('enquiry/', enquiry_view, name='enquiry'),
    path('<str:template_name>/', dynamic_pages_view, name='dynamic_pages')
]
