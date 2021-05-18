import datetime
from .models import Post, Category
from django.test import TestCase, TransactionTestCase, LiveServerTestCase
from django.db.transaction import TransactionManagementError
from django.contrib.auth.models import User
from django.test import Client
from .views import update_user_posts
from django.http import HttpRequest
from django.utils.timezone import utc

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
        # with self.assertRaises(TransactionManagementError):
        #     posts = Post.objects.select_for_update().filter()
        #     print(posts)
        pass


class TestCategoryCase(TestCase):
    
    fixtures = ['blogging_test_fixture.json']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.otheruser = User.objects.get(pk=2)
        self.category = Category(name='test', description='more test')
        self.category.save()
        p1 = Post(title='This is a title', text='first', author=self.user)
        p2 = Post(title='This is another title', text='second', author=self.user)
        p3 = Post(title='This is a third title', text='third', author=self.user)
        p4 = Post(title='Excluded from update', text='fourth', author=self.otheruser)
        self.posts = [p1, p2, p3, p4]
        for post in self.posts:
            post.save()
            self.category.posts.add(post)
        
    def test_str(self):
        self.assertEqual(str(self.category), self.category.name)
    
    def test_post_titles(self):
        test_list = self.category.post_titles()
        for post in self.posts:
            self.assertIn(post.title, test_list)

class FrontEndTestCase(TestCase):
    
    fixtures = ['blogging_test_fixture.json',]
    def setUp(self):
        self.now = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.timedelta = datetime.timedelta(15)
        author = User.objects.get(pk=1)
        for count in range(1, 11):
            post = Post(title=f'Post {count} Title',
                        text='foo',
                        author=author)
            if count < 6:
                pubdate = self.now - self.timedelta * count
                post.post_date = pubdate
            post.save()
    
    def test_list_only_published(self):
        resp = self.client.get('/')
        resp_text = resp.content.decode(resp.charset)
        self.assertTrue("Recent Posts" in resp_text)
        for count in range(1, 11):
            title = f"Post {count} Title"
            if count < 6:
                self.assertContains(resp, title, count=1)
            else:
                self.assertNotContains(resp, title)

    def test_detail_only_published(self):
        for count in range(1, 11):
            title = f'Post {count} Title'
            post = Post.objects.get(title=title)
            resp = self.client.get(f'/posts/{post.pk}/')
            if count < 6:
                self.assertEqual(resp.status_code, 200)
                self.assertContains(resp, title)
            else:
                self.assertEqual(resp.status_code, 404)

    

# class PostTransactionTestCase(TransactionTestCase):
#     fixtures = ['blogging_test_fixture.json']

#     def setUp(self):
#         self.user = User.objects.get(pk=1)
#         self.otheruser = User.objects.get(pk=2)
#         p1 = Post(title='This is a title', text='first', author=self.user)
#         p2 = Post(title='This is another title', text='second', author=self.user)
#         p3 = Post(title='This is a third title', text='third', author=self.user)
#         p4 = Post(title='Excluded from update', text='fourth', author=self.otheruser)
#         self.posts = [p1, p2, p3, p4]
#         for post in self.posts:
#             post.save()
#         self.p1 = Post.objects.create(title='This is a title', text='first', author=self.user)
    
#     def test_update_user_posts(self):
#         # self.assertEqual(self.posts[1].text, 'second')
#         # request = HttpRequest()
#         # request.method = 'GET'
#         # request.path = '/posts/admin/test'
#         # response = update_user_posts(request, 'admin', 'test')
#         # #print(response.content)
#         # self.assertNotIn(b'Excluded from update', response.content)
#         # self.assertNotIn(b'second', response.content)
#         # self.assertIn(b'test', response.content)
#         # request.path = '/posts/bob/test'
#         # self.assertRaises(TransactionManagementError, update_user_posts, request, 'bob', 'test')
#         with self.assertRaises(TransactionManagementError):
#             posts = Post.objects.select_for_update().filter()
#             print(posts)
