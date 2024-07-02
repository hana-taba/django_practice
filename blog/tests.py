from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post,Category
from django.contrib.auth.models import User


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump=User.objects.create_user(username='trump',password='somepassword')
        self.user_obama=User.objects.create_user(username='obama',password='somepassword')

        self.category_ballad=Category.objects.create(name='ballad',slug='발라드')
        self.category_jpop=Category.objects.create(name="J-pop",slug='제이팝')

        self.post_001=Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello world, we are the world',
            category=self.category_ballad,
            author=self.user_trump
        )

        self.post_002=Post.objects.create(
            title="두 번째 포스트입니다",
            content="1등이 전부나쟈이",
            category=self.category_ballad,
            author=self.user_obama
        )

        self.post_003=Post.objects.create(
            title='세 번째 포스트',
            content='category 가 없을 수 도 있지',
            author=self.user_obama
        )
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

    def category_car_test(self,soup):
        cateogries_card=soup.find('div',id='categories-card')
        self.assertIn('Categories',cateogries_card.text)
        self.assertIn(f'{self.category_ballad.name}({self.category_ballad.post_set.count()})')
        self.assertIn(f'미분류 (1)',cateogries_card.text)
    def test_post_list(self):
        self.assertEqual(Post.objects.count(),3)

        response=self.client.get('/blog/')
        self.assertEqual(response.status_code,200)
        soup=BeautifulSoup(response.content,'html.parser')

        self.navbar_test(soup)
        self.category_car_test(soup)

        main_area=soup.find('div',id='main-area')
        self.assertNotIn('아직 게시물이 없습니다',main_area.text)

        post_001_card=main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)


        post_002_card=main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)


        post_003_card = main_area.find('div', id='post-3')
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn(self.post_003.category.name, post_003_card.text)

        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)

        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(),0)
        response=self.client.get('/blog')
        soup=BeautifulSoup(response.content,'html.parser')
        main_area=soup.find('div',id='main-area')
        self.assertIn('아직 게시물이 없습니다',main_area.text)


    def test_post_deatil(self):

        self.assertEqual(self.post_001.get_absolute_url(),'/blog/1/')
        response=self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code,200)
        soup=BeautifulSoup(response.content,'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.post_001.title,soup.title.text)
        main_area=soup.find('div',id='main-area')
        post_area=main_area.find('div',id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_ballad,post_area.text)
        self.assertIn(self.user_trump.username.upper(),post_area.text)
        self.assertIn(self.post_001.content,post_area.text)

