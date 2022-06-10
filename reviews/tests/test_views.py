from django.test import TestCase, Client,RequestFactory
from ..views import index


class TestIndexView(TestCase):
    """Test the index view"""
    def setUp(self):
        self.factory = RequestFactory()

    def test_index_view(self):
        request = self.factory.get('')
        request.session = {}
        response = index(request)
        self.assertEquals(response.status_code, 200)