from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category,Tag
from django.contrib.auth.models import User


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')
        self.user_obama.is_staff=True
        self.user_obama.save()

        self.category_ballad = Category.objects.create(name='ballad', slug='발라드')
        self.category_jpop = Category.objects.create(name="J-pop", slug='제이팝')

        self.tag_python_kor=Tag.objects.create(name='파이썬 공부',slug='파이썬-공부')
        self.tag_python=Tag.objects.create(name='python',slug='python')
        self.tag_hello=Tag.objects.create(name='hello',slug='hello')

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello world, we are the world',
            category=self.category_ballad,
            author=self.user_trump
        )
        self.post_001.tags.add(self.tag_hello)

        self.post_002 = Post.objects.create(
            title="두 번째 포스트입니다",
            content="1등이 전부나쟈이",
            category=self.category_ballad,
            author=self.user_obama
        )

        self.post_003 = Post.objects.create(
            title='세 번째 포스트',
            content='category 가 없을 수 도 있지',
            author=self.user_obama
        )
        self.post_003.tags.add(self.tag_python_kor)
        self.post_003.tags.add(self.tag_python)
    def test_category_page(self):
        response = self.client.get(self.category_ballad.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_ballad.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_ballad.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)

        logo_btn = navbar.find('a', text='Do It Django')
        self.assertEqual(logo_btn.attrs['href'], '/')
        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')
        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')
        about_me_btn = navbar.find('a', text="About me")
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_ballad.name} ({self.category_ballad.post_set.count()})', categories_card.text)
        self.assertIn('미분류 (1)', categories_card.text)

    def test_post_list(self):
        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.post_001.author.username.upper(),post_001_card.text)
        self.assertIn(self.tag_hello.name,post_001_card.text)
        self.assertNotIn(self.tag_python.name,post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name,post_001_card.text)


        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertIn(self.post_002.author.username.upper(),post_002_card.text)
        self.assertIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.author.username.upper(), post_003_card.text)
        self.assertIn(self.tag_hello.name, post_003_card.text)
        self.assertNotIn(self.tag_python.name, post_003_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_003_card.text)


        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)

        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

    def test_post_detail(self):
        self.assertEqual(self.post_001.get_absolute_url(), f'/blog/{self.post_001.pk}/')
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.post_001.title, soup.title.text)
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_ballad.name, post_area.text)
        self.assertIn(self.user_trump.username.upper(), post_area.text)
        self.assertIn(self.post_001.content, post_area.text)

    def test_create_post(self):
        response=self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code,200)


        self.client.login(username='trump',password='somepassword')
        response=self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code,200)

        self.client.login(username='obama',password='somepassword')
        response=self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code,200)
        soup=BeautifulSoup(response.content,'html.parser')

        self.assertEqual('Create Post - Blog',soup.title.text)
        main_area=soup.find('div',id='main-area')
        self.assertIn('Create New Post',main_area.text)

        self.client.post(
            '/blog/create_post',
            {
                'title':'Post Form 만들기',
                'content':"Post Form 페이지를 만듭시다",
            }
        )
        self.assertEqual(Post.objects.count(),4)
        last_post=Post.objects.last()
        self.assertEqual(last_post.title,"Post Form 만들기")
        self.assertEqual(last_post.author.username,'obama')

