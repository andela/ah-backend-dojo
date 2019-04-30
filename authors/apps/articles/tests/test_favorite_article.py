import json
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from authors.apps.authentication.models import User
from ..models import Article
from rest_framework import status



class FavoriteArticle(TestCase):
    """
    Tests for Favoring Articles
    """

    def setUp(self):
        self.email = 'johndoe@gmail.com'
        self.username = 'johndoe'
        self.password = 'Johndoe3@'


        self.email2 = 'fieldmarshal@gmail.com'
        self.username2 = 'fieldmarshal'
        self.password2 = 'FieldMarshal@3'
        # create a user
        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        # create the second user
        self.user2 = User.objects.create_user(
            self.username2, self.email2, self.password2)

        # verify a user's account and save
        self.user.save()
        self.token = self.user.token

        # verify and save the second user
        self.user2.save()
        self.token2 = self.user2.token

        self.test_client = APIClient()

        self.article_data = {
            "article": {
                "title": "Article 2 title",
                "body": "Article body",
                "description": "Article description"
                }
        }

    def test_favorite_an_article(self):
        """
        Test favorite an article
        """
        response = self.test_client.post(
            "/api/articles/",data=json.dumps(self.article_data),
                                       content_type='application/json',
                             HTTP_AUTHORIZATION=f"Bearer {self.token}")
        favorite_url = reverse(
            'favorite', 
            kwargs={'slug': response.data['article']['slug']}
        )
        response = self.test_client.post(
            favorite_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.token}")
        
        self.assertIn(
            'You have successfully favorited this article',
            response.data['message']            
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )



    def test_article_has_already_been_favorited_by_a_user(self):
        """
        Test user cann't favorite an article twice
        """
        response = self.test_client.post(
            "/api/articles/",data=json.dumps(self.article_data),
                                       content_type='application/json',
                             HTTP_AUTHORIZATION=f"Bearer {self.token}")
        favorite_url = reverse(
            'favorite', 
            kwargs={'slug': response.data['article']['slug']}
        )
        response = self.test_client.post(
            favorite_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.test_client.post(
            favorite_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.assertIn(
            'You already favorited this article',
            response.data['message']            
        )

    def test_unfavorite_an_article(self):
        """
        Test Unfavorite an article
        """
        response = self.test_client.post(
            "/api/articles/",data=json.dumps(self.article_data),
                                       content_type='application/json',
                             HTTP_AUTHORIZATION=f"Bearer {self.token}")
        
        slug = response.data['article']['slug']

        favorite_url = reverse(
            'favorite', 
            kwargs={'slug':slug}
        )
        response = self.test_client.post(
            favorite_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.token}")

        unfavorite_url = reverse(
            'unfavorite', 
            kwargs={'slug': slug}
        )
        response = self.client.delete(
            unfavorite_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.assertIn(
            'You have successfully unfavorited this article.',
            response.data['message']            
        )
    

    def test_unfavorite_an_article_without_favoriting(self):
        """
        Test unfavorite an article without having favorited it.
        """
        response = self.test_client.post(
            "/api/articles/",data=json.dumps(self.article_data),
                                       content_type='application/json',
                             HTTP_AUTHORIZATION=f"Bearer {self.token}")
        
        slug = response.data['article']['slug']

        unfavorite_url = reverse(
            'unfavorite', 
            kwargs={'slug': slug}
        )
        response = self.client.delete(
            unfavorite_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.assertIn(
            'You have not favourited this article',
            response.data['message']            
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )