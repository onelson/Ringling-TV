from django.test import TestCase
from django.conf import settings
from django.core.files import File
from django.contrib.auth.models import User
from rtv.models import TranscodeJob
import os

from rtv.fedora.models import Video

class TranscodeJobTest(TestCase):
    fixtures = ['test_users']
    
    def createFakeVid(self):
        '''
        Cheating a little here... creating the vid in setup, then testing after 
        the fact.
        '''
        samples = os.path.join(settings.PROJECT_ROOT,'..','parts',
            'sample-media','video')
        # grabbing first vid from the samples dir
        vid_file = os.path.join(samples,os.listdir(samples)[0])
        vfh = File(open(vid_file,'rb'))
        self.created_vid = {'size':os.path.getsize(vfh.name)}
        vid = TranscodeJob.objects.create(user=self.user, title='test video')
        vid.source.save('tmp',vfh, save=True)
        return vid
    
    def setUp(self):
        self.user = User.objects.get(username='meg')
        self.vid = self.createFakeVid()
    
    def tearDown(self):
        self.vid.delete()
        
    def testCreate(self):
        self.assertTrue(os.path.exists(self.vid.source.path))
    def testGet(self):
        TranscodeJob.objects.get(pk=self.vid.pk)

    def testTranscodeAndCreateVideo(self):
        """
        I hoped to have this test in the fedora test suite, but it would involve
        reruning the transcode tests...
        """
        self.vid.transcode()
        self.assertEqual(self.vid.status, self.vid.STATUS_PROCESSED)
        self.assertTrue(os.path.exists(self.vid.ogv.path))
        self.assertTrue(os.path.exists(self.vid.mp4.path))
        self.assertTrue(os.path.exists(self.vid.thumbnail.path))
        tj = self.vid
        Video.objects.create(user=tj.user.username, source=tj.source.url, 
                    mp4=tj.mp4.url, ogv=tj.ogv.url, thumbnail=tj.thumbnail.url, 
                    dc=dict(title=tj.title))
