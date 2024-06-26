from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post

class TestView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_post_list(self):
        # Test when there are no posts
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog')
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)
        self.assertEqual(Post.objects.count(), 0)
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

        # Create posts
        post_001 = Post.objects.create(
            title='첫번째 포스트 입니다',
            content='Hello World. We are the world',
        )
        post_002 = Post.objects.create(
            title='두번째 포스트입니다',
            content='1등이 전부는 아니잖아',
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
