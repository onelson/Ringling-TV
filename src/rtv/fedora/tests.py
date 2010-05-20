from django.test import TestCase
from django.contrib.auth.models import User
from rtv.fedora import get_client, pp
from rtv.fedora.cmodels import install_episode, purge_episode
from fcrepo.connection import FedoraConnectionException
class FedoraTest(TestCase):
    fixtures = ['test_users']
    def setUp(self):
        self.user = User.objects.get(username='brian')
        try:
            install_episode()
        except FedoraConnectionException:
            # if for some reason, episode is already in the repo, purge it and
            # add it again.  It needs to be "fresh". 
            purge_episode()
            install_episode()
        
    def tearDown(self):
        try:
            purge_episode()
        except: pass
        
    def testCanTalkToFedoraServer(self):
        get_client()
        
    def testCanCreateVideo(self):
        pass

    def testInstallPurgeEpisodeContentModel(self):
        # episode is installed in setup, so it should fail to add it again
        self.assertRaises(FedoraConnectionException, install_episode)
        purge_episode()
        # removing it twice should raise the same exception
        self.assertRaises(FedoraConnectionException, purge_episode)
        # when not already in the system, install should work
        install_episode()
        client = get_client()
        client.getObject(pp('EPISODE')) # as should get