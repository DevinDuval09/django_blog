from .models import Post
from django.test import TestCase, TransactionTestCase, LiveServerTestCase
from django.db.transaction import TransactionManagementError
from django.contrib.auth.models import User
from django.test import Client
from .views import update_user_posts
from django.http import HttpRequest

class PostTestCase(TestCase):
    fixtures = ['blogging_test_fixture.json']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.otheruser = User.objects.get(pk=2)
        p1 = Post(title='This is a title', text='first', author=self.user)
        p2 = Post(title='This is another title', text='second', author=self.user)
        p3 = Post(title='This is a third title', text='third', author=self.user)
        p4 = Post(title='Excluded from update', text='fourth', author=self.otheruser)
        self.posts = [p1, p2, p3, p4]
        for post in self.posts:
            post.save()

    def test_string_repr(self):
        expected = 'This is a title'
        actual = str(self.posts[0])
        self.assertEqual(expected, actual)
    
    def test_update_user_posts(self):
        # self.assertEqual(self.posts[1].text, 'second')
        # request = HttpRequest()
        # request.method = 'GET'
        # request.path = '/posts/admin/test'
        # response = update_user_posts(request, 'admin', 'test')
        # #print(response.content)
        # self.assertNotIn(b'Excluded from update', response.content)
        # self.assertNotIn(b'second', response.content)
        # self.assertIn(b'test', response.content)
        # request.path = '/posts/bob/test'
        # self.assertRaises(TransactionManagementError, update_user_posts, request, 'bob', 'test')
        with self.assertRaises(TransactionManagementError):
            posts = Post.objects.select_for_update().filter()
            print(posts)
    

class PostTransactionTestCase(TransactionTestCase):
    fixtures = ['blogging_test_fixture.json']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.otheruser = User.objects.get(pk=2)
        p1 = Post(title='This is a title', text='first', author=self.user)
        p2 = Post(title='This is another title', text='second', author=self.user)
        p3 = Post(title='This is a third title', text='third', author=self.user)
        p4 = Post(title='Excluded from update', text='fourth', author=self.otheruser)
        self.posts = [p1, p2, p3, p4]
        for post in self.posts:
            post.save()
        self.p1 = Post.objects.create(title='This is a title', text='first', author=self.user)
    
    def test_update_user_posts(self):
        # self.assertEqual(self.posts[1].text, 'second')
        # request = HttpRequest()
        # request.method = 'GET'
        # request.path = '/posts/admin/test'
        # response = update_user_posts(request, 'admin', 'test')
        # #print(response.content)
        # self.assertNotIn(b'Excluded from update', response.content)
        # self.assertNotIn(b'second', response.content)
        # self.assertIn(b'test', response.content)
        # request.path = '/posts/bob/test'
        # self.assertRaises(TransactionManagementError, update_user_posts, request, 'bob', 'test')
        with self.assertRaises(TransactionManagementError):
            posts = Post.objects.select_for_update().filter()
            print(posts)
