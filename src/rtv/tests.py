from django.test import TestCase
from django.core.files import File
from django.contrib.auth.models import User
from rtv.fedora import get_client
from rtv.models import TranscodeJob
import tempfile, os

class FedoraServerTest(TestCase):
    fixtures = ['test_users']
    def setUp(self):
        self.user = User.objects.get(username='brian')
        
    def testCanTalkToFedoraServer(self):
        client = get_client()

class TranscodeJobTest(TestCase):
    fixtures = ['test_users']
    
    def createFakeVid(self):
        '''
        Cheating a little here... creating the vid in setup, then testing after 
        the fact.
        '''
        vid_file = tempfile.NamedTemporaryFile(prefix='rtvtest', delete=False)
        vid_file.write("I'm a video " * (1024**2))
        vid_file.close()
        vfh = File(open(vid_file.name,'rb'))
        self.created_vid = {'size':os.path.getsize(vfh.name)}
        vid = TranscodeJob.objects.create(user=self.user, title='test video')
        vid.source.save('tmp',vfh, save=True)
        self.tmpfile = vid_file.name
        self.created_vid['pk'] = vid.pk
        self.created_vid['path'] = vid.source.path
    
    def setUp(self):
        self.tmpfile = None
        self.user = User.objects.get(username='meg')
        self.createFakeVid()
    def tearDown(self):
        os.remove(self.tmpfile)

    def testCanCreate(self):
        self.assertTrue(os.path.exists(self.created_vid['path']))
    def testCanGet(self):
        obj = TranscodeJob.objects.get(pk=self.created_vid['pk'])
        self.assertEqual(os.path.getsize(obj.source.path), self.created_vid['size'])
    
    def testCanTranscode(self):
        raise NotImplementedError
    def testCanSendToFedora(self):
        raise NotImplementedError
    
    def testCanDelete(self):
        obj = TranscodeJob.objects.get(pk=self.created_vid['pk'])
        obj.delete()
        self.assertFalse(os.path.exists(self.created_vid['path']))