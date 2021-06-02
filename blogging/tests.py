import datetime

from django.db.models.query import FlatValuesListIterable
from .models import Post, Category, Comment
from django.test import TestCase, TransactionTestCase, LiveServerTestCase
from django.db.transaction import TransactionManagementError
from django.contrib.auth.models import User
from django.test import Client
from django.http import HttpRequest
from django.utils.timezone import utc


class PostTestCase(TestCase):
    fixtures = ["blogging_test_fixture.json"]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.otheruser = User.objects.get(pk=2)
        p1 = Post(title="This is a title", text="first", author=self.user)
        p2 = Post(title="This is another title", text="second", author=self.user)
        p3 = Post(title="This is a third title", text="third", author=self.user)
        p4 = Post(title="Excluded from update", text="fourth", author=self.otheruser)
        self.posts = [p1, p2, p3, p4]
        self.comments = []
        for post in self.posts:
            post.save()
            comment = Comment(
                post=post, author=post.author, text=f"{post.title} comment."
            )
            comment.save()
            self.comments.append(comment)

    def test_string_repr(self):
        expected = "This is a title"
        actual = str(self.posts[0])
        self.assertEqual(expected, actual)

    def test_comment_str(self):
        for comment in self.comments:
            post = comment.post
            username = comment.author.username
            self.assertEqual(f"{username}: {comment.text}", str(comment))
            self.assertIn(post, self.posts)

    def test_add_multiple_comments(self):
        for post in self.posts:
            comment = Comment(
                post=post,
                author=self.user,
                text=f"another comment by {self.user.username}",
            )
            comment.save()
            self.comments.append(comment)
            another_comment = Comment(
                post=post,
                author=self.otheruser,
                text=f"another comment by {self.otheruser.username}",
            )
            another_comment.save()
            self.comments.append(another_comment)

        test_list = [comment.post for comment in Comment.objects.all()]
        for post in self.posts:
            count = 0
            for comment_post in test_list:
                if post == comment_post:
                    count += 1
            self.assertEqual(count, 3)


class TestCategoryCase(TestCase):

    fixtures = ["blogging_test_fixture.json"]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.otheruser = User.objects.get(pk=2)
        self.category = Category(name="test", description="more test")
        self.category.save()
        p1 = Post(title="This is a title", text="first", author=self.user)
        p2 = Post(title="This is another title", text="second", author=self.user)
        p3 = Post(title="This is a third title", text="third", author=self.user)
        p4 = Post(title="Excluded from update", text="fourth", author=self.otheruser)
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

    fixtures = [
        "blogging_test_fixture.json",
    ]

    def setUp(self):
        self.now = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.timedelta = datetime.timedelta(15)
        author = User.objects.get(pk=1)
        author2 = User.objects.get(pk=2)
        for count in range(1, 11):
            post = Post(title=f"Post {count} Title", text="foo", author=author)
            if count < 6:
                pubdate = self.now - self.timedelta * count
                post.post_date = pubdate
                comment1 = Comment(post=post, author=author, text="comment 1")
                comment2 = Comment(post=post, author=author2, text="comment 2")
            post.save()
            comment1.save()
            comment2.save()
        count = 11
        xss_attack = Post(
            title=f"Post {count} Title",
            text='foo <script> alert("This was successful!"); </script>',
            author=author,
            post_date=self.now - self.timedelta * count,
        )
        xss_attack.save()

    def test_list_only_published(self):
        resp = self.client.get("/")
        resp_text = resp.content.decode(resp.charset)
        self.assertTrue("Posts" in resp_text)
        for count in range(1, 11):
            title = f"Post {count} Title"
            if count < 6:
                self.assertContains(resp, title, count=1)
            else:
                self.assertNotContains(resp, title)

    def test_detail_only_published(self):
        for count in range(1, 11):
            title = f"Post {count} Title"
            post = Post.objects.get(title=title)
            resp = self.client.get(f"/posts/{post.pk}/")
            if count < 6:
                self.assertEqual(resp.status_code, 200)
                self.assertContains(resp, title)
            else:
                self.assertEqual(resp.status_code, 404)

    def test_comments(self):
        author = User.objects.get(pk=1)
        author2 = User.objects.get(pk=2)
        for count in range(1, 6):
            resp = self.client.get(f"/posts/{count}/")
            self.assertContains(resp, f"{author.username}: comment 1")
            self.assertContains(resp, f"{author2.username}: comment 2")
    
    def test_add_comment(self):
        author = User.objects.create(username="testuser")
        author.set_password("12345")
        author.save()
        login = self.client.login(username="testuser", password="12345")
        self.assertTrue(login)
        for count in range(1, 6):
            text = f"Another {count} comment."
            comment = {"author": author.pk, "post": count, "text": text}
            post = self.client.post(f"/posts/{count}/", data=comment, follow=True)
            self.assertEqual(post.status_code, 200)
            self.assertContains(post, text)

    def test_add_comment_on_comment_page(self):
        author = User.objects.create(username="testuser")
        author.set_password("12345")
        author.save()
        login = self.client.login(username="testuser", password="12345")
        self.assertTrue(login)
        for count in range(1, 6):
            comment = {"author": author.pk, "post": count, "text": "testusers comment."}
            resp = self.client.get(f"/posts/{count}/comments")
            self.assertNotContains(resp, "Author:")
            self.assertNotContains(resp, "Post:")
            self.assertContains(resp, "New comment:")
            post = self.client.post(f"/posts/{count}/comments", data=comment, follow=True)
            self.assertContains(post, "testuser: testusers comment.")

    def test_xss_attack(self):
        pk = 11
        resp = self.client.get(f"/posts/{pk}/")
        self.assertContains(resp, "&lt;script&gt;")

    def test_generic_sorted_list_sort_date(self):
        url = "/posts/exclude/post_date__gt/2021-01-01/"
        resp = self.client.get(url)
        self.assertEqual(
            resp.content.decode().count("None"), 5
        )  # should be 5 posts with no post_date from setUp

    def test_generic_sorted_list_number(self):
        url = "/posts/filter/title__contains/1/"
        resp = self.client.get(url)
        for x in (1, 10, 11):  # Posts that contain 1 from setUp
            self.assertContains(resp, f"Post {x} Title")

    def test_generic_sorted_list_letters(self):
        url = "/posts/filter/text__contains/foo/"
        resp = self.client.get(url)
        for x in range(1, 12):
            self.assertContains(resp, f"Post {x} Title")
