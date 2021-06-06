import datetime

from django.db.models.query import FlatValuesListIterable
from django.http.response import Http404
from django.shortcuts import redirect
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
        self.logged_in_menu = (
            "New Post",
            "Unpublished Posts",
            "Published Posts",
            "logout",
        )
        self.now = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.timedelta = datetime.timedelta(15)
        self.author = User.objects.get(pk=1)
        self.author2 = User.objects.get(pk=2)
        for count in range(1, 11):
            post = Post(title=f"Post {count} Title", text="foo", author=self.author)
            if count < 6:
                pubdate = self.now - self.timedelta * count
                post.post_date = pubdate
                comment1 = Comment(post=post, author=self.author, text="comment 1")
                comment2 = Comment(post=post, author=self.author2, text="comment 2")
            post.save()
            comment1.save()
            comment2.save()
        count = 11
        xss_attack = Post(
            title=f"Post {count} Title",
            text='foo <script> alert("This was successful!"); </script>',
            author=self.author,
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
            resp = self.client.get(f"/posts/{post.pk}/", follow=True)
            if count < 6:
                self.assertEqual(resp.status_code, 200)
                self.assertContains(resp, title)
            else:
                self.assertContains(resp, "My Blog Login")

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
            resp = self.client.get(f"/posts/{count}/comments/")
            self.assertNotContains(resp, "Author:")
            self.assertNotContains(resp, "Post:")
            self.assertContains(resp, "New comment:")
            post = self.client.post(
                f"/posts/{count}/comments/", data=comment, follow=True
            )
            self.assertContains(post, "testuser: testusers comment.")

    def test_add_comment_login_redirect(self):
        login = self.client.login(username="admin", password="?")
        comment = {"author": 1, "post": 1, "text": "This should fail."}
        post = self.client.post("/posts/1/", data=comment, follow=True)
        self.assertFalse(login)
        self.assertContains(post, "My Blog Login")

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

    def test_create_user(self):
        url = "/register/"
        resp = self.client.get(url)
        self.assertContains(resp, "Create New User")
        self.assertContains(resp, "Email address(optional)")

    def test_create_user_redirect(self):
        url = "/register"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 301)

    def test_create_user_post(self):
        user_data = {
            "username": "testuser",
            "email": "abc123@gmail.com",
            "password1": "abcDef123456",
            "password2": "abcDef123456",
        }
        post = self.client.post("/register/", data=user_data, follow=True)
        user = User.objects.get(username="testuser")
        self.assertEqual(post.status_code, 200)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.pk, 3)

    def test_logged_out_views(self):
        resp = self.client.get("/")
        for option in self.logged_in_menu:
            self.assertNotContains(resp, option)
        resp = self.client.get("/posts/5/")
        self.assertContains(resp, "Post 5 Title")
        self.assertNotContains(resp, "Edit")

    def test_logged_in_home_view(self):
        self.author.set_password("12345")
        self.author.save()
        login = self.client.login(username="admin", password="12345")
        self.assertTrue(login)
        home = self.client.get("/")
        for option in self.logged_in_menu:
            self.assertContains(home, option)

    def test_logged_in_post_view(self):
        self.author.set_password("12345")
        self.author.save()
        login = self.client.login(username="admin", password="12345")
        self.assertTrue(login)
        for count in range(1, 6):
            post_view = self.client.get(f"/posts/{count}/")
            self.assertContains(post_view, "Edit")

    def test_logged_in_wrong_user_view(self):
        self.author2.set_password("54321")
        self.author2.save()
        login = self.client.login(username="noname", password="54321")
        self.assertTrue(login)
        for count in range(1, 6):
            post_view = self.client.get(f"/posts/{count}/")
            self.assertNotContains(post_view, "Edit")
        for count in range(6, 11):
            post_view = self.client.get(f"/posts/{count}/", follow=True)
            self.assertContains(post_view, "Page Not Found")
            self.assertEqual(200, post_view.status_code)

    def test_new_post_post(self):
        self.author.set_password("12345")
        self.author.save()
        login = self.client.login(username="admin", password="12345")
        self.assertTrue(login)
        title = "Test Post"
        text = "Test post text"
        pubdate = datetime.datetime.utcnow().strftime("%Y-%m-%d")

        data = {
            "author": self.author.pk,
            "title": title,
            "text": text,
            "post_date": pubdate,
        }
        post = self.client.post("/posts/new_post/", data=data, follow=True)
        found_post = Post.objects.get(title="Test Post")
        self.assertEqual(found_post.title, title)
        self.assertEqual(found_post.text, text)
        self.assertEqual(found_post.post_date.strftime("%Y-%m-%d"), pubdate)
        self.assertEqual(post.status_code, 200)

    def test_edit_post_post(self):
        pk = 6
        self.author.set_password("12345")
        self.author.save()
        login = self.client.login(username="admin", password="12345")
        self.assertTrue(login)
        pubdate = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        post_obj = Post.objects.get(pk=pk)
        data = {
            "author": post_obj.author.pk,
            "post_date": pubdate,
            "title": "A New Title",
            "text": "Some new text.",
        }
        post = self.client.post(f"/posts/{pk}/edit/", data=data, follow=True)
        self.assertEqual(post.status_code, 200)
        post_obj = Post.objects.get(pk=pk)
        self.assertEqual(post_obj.post_date.strftime("%Y-%m-%d"), pubdate)
        self.assertEqual(post_obj.title, "A New Title")
        self.assertEqual(post_obj.text, "Some new text.")

    def test_published_posts(self):
        self.author.set_password("12345")
        self.author.save()
        login = self.client.login(username="admin", password="12345")
        self.assertTrue(login)
        pub_list = self.client.get(f"/posts/{self.author.username}/published/")
        self.assertEqual(pub_list.status_code, 200)
        for count in range(1, 6):
            self.assertContains(pub_list, f"Post {count} Title")
        for count in range(6, 11):
            self.assertNotContains(pub_list, f"Post {count} Title")

    def test_unpublished_posts(self):
        self.author.set_password("12345")
        self.author.save()
        login = self.client.login(username="admin", password="12345")
        self.assertTrue(login)
        pub_list = self.client.get(f"/posts/{self.author.username}/unpublished/")
        self.assertEqual(pub_list.status_code, 200)
        for count in range(1, 6):
            self.assertNotContains(pub_list, f"Post {count} Title")
        for count in range(6, 11):
            self.assertContains(pub_list, f"Post {count} Title")
