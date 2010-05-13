from django.test import TestCase
from django.contrib.auth.models import User
import rtv.fedora

class FedoraServerTest(TestCase):
    fixtures = ['test_users']
    def setUp(self):
        self.user = User.objects.get(username='brian')
        
    def testCanTalkToFedoraServer(self):
        client = rtv.fedora.get_client()

class VideoModelTest(TestCase):
    fixtures = ['test_users']
    def setUp(self):
        self.user = User.objects.get(username='meg')

    def testCanCreate(self):
        raise NotImplementedError
    def testCanTranscode(self):
        raise NotImplementedError
    def testCanSendToFedora(self):
        raise NotImplementedError
    def testCanDelete(self):
        raise NotImplementedError