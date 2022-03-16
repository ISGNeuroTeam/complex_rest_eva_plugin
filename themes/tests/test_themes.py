import json
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
from rest.test import TestCase, APIClient
from rest_auth.models import User

class TestThemes(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = User.objects.create_user('temp', "temp@temp.te", "temporary")
        self.client.force_authenticate(user=user)


    def test_theme_list(self):
        response = self.client.get('/themes/v1/themes')

        # checking status code
        self.assertEqual(response.status_code, 200)


    def test_create_theme(self):
        response = self.client.post('/themes/v1/theme/create', {'themeName':'TestThemeNamed', "color":"red"})

        # checking status code
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/themes/v1/themes')
        self.assertNotEqual(len(response.json()), 0)

    def test_get_theme(self):
        response = self.client.get('/themes/v1/theme', {'themeName':'TestThemeNamed'})

        # checking status code
        self.assertEqual(response.status_code, 200)

    def test_delete_theme(self):
        response = self.client.delete('/themes/v1/theme/delete', {'themeName': 'TestThemeNamed'})

        # checking status code
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/themes/v1/themes')
        self.assertEqual(len(response.json()), 0)

