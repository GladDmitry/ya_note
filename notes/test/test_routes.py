from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    slug_url_names = ('notes:edit', 'notes:delete', 'notes:detail')
    noslug_urls = ('notes:add', 'notes:list', 'notes:success')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Автор',
                                              password='someonelse'
                                              )
        cls.noauthor = User.objects.create_user(username='Не автор',
                                                password='nobody'
                                                )
        cls.note = Note.objects.create(title='Заголовок', text='Текст',
                                       author=cls.author
                                       )

    def get_url(self, name):
        if name in self.slug_url_names:
            return reverse(name, args=(self.note.slug,))
        return reverse(name)

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('notes:detail', (self.note.slug,)),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        self.client.force_login(self.author)
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')

        for name in self.slug_url_names + self.noslug_urls:
            with self.subTest(name=name):
                url = self.get_url(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_verification_access(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.noauthor, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in self.slug_url_names:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
