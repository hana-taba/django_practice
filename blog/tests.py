from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post
from django.contrib.auth.models import User


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.trump=User.objects.create_user(username='trump',password='somepassword')
        self.user_obama=User.objects.create_user(username='obama',password='somepassword')

    def navbar_test(self, soup):
        navbar=soup.nav
        self.assertIn('Blog',navbar.text)
        self.assertIn('About me',navbar.text)

        logo_btn=navbar.find('a',text='Do It Django')
        self.assertEqual(logo_btn.attrs['href'],'/')
        home_btn=navbar.find('a',text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')
        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')
        about_me_btn=navbar.find('a',text="About me")
        self.assertEqual(about_me_btn.attrs['href'],'/about_me/')
    def test_post_list(self):
        # Test when there are no posts
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog')
        self.navbar_test(soup)
        self.assertEqual(Post.objects.count(), 0)
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

        # Create posts
        post_001 = Post.objects.create(
            title='첫번째 포스트 입니다',
            content='Hello World. We are the world',
            author=self.user_trump
        )
        post_002 = Post.objects.create(
            title='두번째 포스트입니다',
            content='1등이 전부는 아니잖아',
            author=self.user_obama
        )
        self.assertEqual(Post.objects.count(), 2)

        # Test when there are posts
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)
        self.assertNotIn('아직 게시물 없습니다', main_area.text)

        self.assertIn(self.user_trump.usename.upper(),main_area.text)
        self.assertIn(self.user_obama.username.upper(),main_area.text)

    def test_post_deatil(self):
        post_001=Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello World. We are the world',
            author=self.user_trump,
        )
        self.assertEqual(post_001.get_absolute_url(),'/blog/1/')
        response=self.client.get(post_001.get_absolute_url())
        self.assertEqual(response.status_code,200)
        soup=BeautifulSoup(response.content,'html.parser')
        self.navbar_test(soup)
        self.assertIn(post_001.title,soup.title.text)
        main_area=soup.find('div',id='main-area')
        post_area=main_area.find('div',id='post-area')
        self.assertIn(self.user_trump.username.upper(),post_area.text)
        self.assertIn(post_001.title,post_area.text)
        self.assertIn(post_001.content,post_area.text)

