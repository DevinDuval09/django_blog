from .models import Post
from django.test import TestCase, SimpleTestCase, TransactionTestCase, LiveServerTestCase
from django.contrib.auth.models import User

class PostTestCase(TestCase):
    fixtures = ['blogging_test_fixture.json']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        print(self.user.username)
    
    def test_string_repr(self):
        expected = 'This is a title'
        p1 = Post(title=expected)
        actual = str(p1)
        self.assertEqual(expected, actual)
