from django.test import TestCase
from django.contrib.auth.models import User
from fcrepo.connection import Connection
from fcrepo.client import FedoraClient

class FedoraServerTest(TestCase):
    fixtures = ['test_users']
    def setUp(self):
        self.connection = Connection('http://localhost:8080/fedora',
            username='fedoraAdmin',
            password='fedoraAdmin')
        self.user = User.objects.get(username='brian')
        
    def testCanTalkToFedoraServer(self):
        client = FedoraClient(self.connection)
