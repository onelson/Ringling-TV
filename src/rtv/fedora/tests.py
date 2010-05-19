from django.test import TestCase
from django.contrib.auth.models import User
from rtv.fedora import get_client

class FedoraTest(TestCase):
    fixtures = ['test_users']
    def setUp(self):
        self.user = User.objects.get(username='brian')
        
    def testCanTalkToFedoraServer(self):
        get_client()

    def testCanCreateVideo(self):
        pass