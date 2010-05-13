from django.test import TestCase
from django.contrib.auth.models import User
import rtv.fedora

class FedoraServerTest(TestCase):
    fixtures = ['test_users']
    def setUp(self):
        self.user = User.objects.get(username='brian')
        
    def testCanTalkToFedoraServer(self):
        client = rtv.fedora.get_client()
