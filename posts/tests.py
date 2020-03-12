from django.core import mail
from django.test import TestCase
from django.test import Client
from . models import Post, User, Group, Comment, Follow

client = Client()

class EmailTest(TestCase):
    def test_send_email(self):
  # Метод send_mail отправляет email сообщения.
        mail.send_mail(
                'Тема письма', 'Текст письма.',
                'from@rocknrolla.net', ['to@mailservice.com'],
                fail_silently=False, # выводить описание ошибок
        )
    
# Проверяем, что письмо лежит в исходящих
        self.assertEqual(len(mail.outbox), 1)
    
# Проверяем, что тема первого письма правильная.
        self.assertEqual(mail.outbox[0].subject, 'Тема письма')


class ProfileTest(TestCase):
        def profiletest(self):
                self.user = User.objects.create_user(first_name = "test", last_name = 'test', username = 'test', email = 'ya@ya.ru', password = 'test',)
                
                post_text  = 'Пробуем тестировать'
                self.post = Post.objects.create(text=post_text, author=self.user)
                post_id = self.post.id

                client.login(username='test', password='test')
                
                response = self.client.get('/')
                self.assertContains(
                        response, 
                        post_text,
                        count=1, 
                        status_code=200, 
                        msg_prefix='', 
                        html=False
                        )
                
                response = self.client.get('/text/')#пробовал и username, profile.username
                self.assertContains(
                        response, 
                        post_text,
                        count=1, 
                        status_code=200, 
                        msg_prefix='', 
                        html=False
                        )
                
                response = self.client.get('/test/post_id/')
                self.assertContains(
                        response, 
                        post_text,
                        count=1, 
                        status_code=200, 
                        msg_prefix='', 
                        html=False
                        )

                with open('posts/media/no-photo.jpg', 'rb') as fp:
                        client.post('/new/', {'text': 'Text', 'image': fp})

class ImageTest(TestCase):
        def setUp(self):
                response = self.client.get('/test/post_id/')
                self.assertContains(response, '<img ', status_code=200 )

                response = self.client.get('/test/')
                self.assertFormError(response)

class CacheTest(TestCase):
        def setUp(self):
                self.user = User.objects.create_user(
                        first_name = "test",
                        last_name = 'test',
                        username = 'test',
                        email = 'ya@ya.ru',
                        password = 'test',
                )
                new_post = "Тест на кеширование"
                self.posted = Post.objects.create(text=new_post, author=self.user)
                post_id = self.post.id
                client.login(username='test', password='test')

                response = self.client.get('/')

                self.assertEqual(response.status_code, 200)

                self.assertNotContains(
                        response,
                        new_text,
                )
                cache.clear()

class FollowTest(TestCase):
        def setUp(self):
                self.client = Client()
                self.user1 = User.objects.create(username='test',
                                                 email='ya@ya.com',
                                                 password='test')
                self.user2 = User.objects.create(username='test2',
                                                 email='ya2j@ya.com',
                                                 password='test2')
                self.user3 = User.objects.create(username='test3',
                                                 email='ya3@ya.com',
                                                 password='ya3')
# Авторизованный пользователь может подписываться на других пользователей
                self.client.force_login(self.user1)
                self.client.get(reverse('profile_follow',
                                        kwargs={
                                                'username': self.user2.username
                                        }
                                        )
                                )
                self.assertEqual(Follow.objects.count(), 1)
# Авторизованный пользователь может отписываться от других пользователей
                self.client.force_login(self.user1)
                self.client.get(reverse('profile_follow',
                                        kwargs={
                                                'username': self.user2.username
                                        }
                                        )
                                )
                self.assertEqual(Follow.objects.count(), 0)
#Запись появляется в ленте тех кто подписан
class New_user_post_view_test(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(username='test',
                                            email='ya@ya.com',
                                            password='test')
        self.user2 = User.objects.create(username='test2',
                                            email='ya2j@ya.com',
                                            password='test2')
        self.user3 = User.objects.create(username='test3',
                                            email='ya3@ya.com',
                                            password='ya3')
        self.post = Post.objects.create(
            text="Test text",
            author=self.user1,
        )
        Follow.objects.create(user=self.user1, author=self.followee)
        self.client.login(**self.user_data)
        follower_feed = self.client.get(f"/follow/")
        self.assertContains(follower_feed, self.post.text, count=1, status_code=200)

