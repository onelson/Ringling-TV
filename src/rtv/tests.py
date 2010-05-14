from django.test import TestCase
from django.contrib.auth.models import User
import rtv.fedora
from rtv.models import Video
import unittest

from rtv.models import Video
import tempfile, os

class FedoraServerTest(TestCase):
    fixtures = ['test_users']
    def setUp(self):
        self.user = User.objects.get(username='brian')
        
    def testCanTalkToFedoraServer(self):
        client = rtv.fedora.get_client()

class VideoModelTest(unittest.TestCase):
    fixtures = ['test_users']
    
    def createFakeVid(self):
        '''
        Cheating a little here... creating the vid in setup, then testing after 
        the fact.
        '''
        vid_file = tempfile.NamedTemporaryFile(prefix='rtvtest', delete=False)
        vid_file.write("I'm a video " * (1024**2))
        vid_file.close()
        from django.core.files import File
        vfh = File(open(vid_file.name,'rb'))
        self.created_vid = {'size':os.path.getsize(vfh.name)}
        vid = Video.objects.create(user=self.user, title='test video', 
            video=vfh)
        self.created_vid['pk'] = vid.pk
        self.created_vid['path'] = vid.video.path
    
    def setUp(self):
        self.user = User.objects.get(username='meg')
        self.createFakeVid()

    def testCanCreate(self):
        self.user.video = Video.objects.create(name='testUpload')
        self.user.video.save()
        self.assertTrue(os.path.exists(self.created_vid['path']))
    def testCanGet(self):
        self.user.getvideo = Video.objects.get(name='testUpload')
        obj = Video.objects.get(pk=self.created_vid['pk'])
        self.assertEqual(os.path.getsize(obj.video.path), self.created_vid['size'])

    def testCanTranscode(self):
        raise NotImplementedError
    def testCanSendToFedora(self):
        raise NotImplementedError
    
    def testCanDelete(self):
        self.user.video.delete()
        obj = Video.objects.get(pk=self.created_vid['pk'])
        obj.delete()
        self.assertFalse(os.path.exists(self.created_vid['path']))
