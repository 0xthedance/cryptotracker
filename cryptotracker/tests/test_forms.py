from django.test import SimpleTestCase


def HomepageTest(SimpleTestCase):
    def test_url_by_pattern(self):
        response = self.client.get(/)
        self.assertEqual(response.status_code, 200)