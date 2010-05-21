from django.test import TestCase
from django.conf import settings
from django.core.files import File
from django.contrib.auth.models import User
from rtv.models import TranscodeJob
import os

import rtv.settings
from rtv.fedora.models import Video
from rtv.fedora.cmodels import install_episode

class SettingsTest(TestCase):
    def testBinariesAreAvailabe(self):
        rtv.settings.check_bins()

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
        ext = os.path.splitext(vfh.name)[0] 
        vid.source.save('tmp'+ext,vfh, save=True)
        return vid
    
    def setUp(self):
        self.user = User.objects.get(username='meg')
        self.vid = self.createFakeVid()
        try: 
            install_episode()
        except: pass
    
    def tearDown(self):
        self.vid.delete()
        
    def testCreate(self):
        self.assertTrue(os.path.exists(self.vid.source.path))
    def testGet(self):
        TranscodeJob.objects.get(pk=self.vid.pk)

    def testTranscodeAndCreateVideo(self):
        """
        Calls TranscodeJob.transcode() then verifies the derived files exist.
        Takes TranscodeJob data, and passes it to Video.objects.create() to add
        the urls to the fedora repository.
        
        I've lumped a few assertions together here since this test involves the
        most labor.
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
