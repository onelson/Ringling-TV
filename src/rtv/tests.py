import os, uuid
from django.test import TestCase
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from rtv.settings import check_bins
from rtv.fedora.models import Video
from rtv.fedora.cmodels import install_episode
from rtv.models import TranscodeJob
from rtv.storage import PermenantStorage

class SettingsTest(TestCase):
    def testBinariesAreAvailabe(self):
        check_bins()

class StorageTest(TestCase):
    def setUp(self): 
        self.tempfile = str(uuid.uuid4())
    def tearDown(self):
        path = os.path.join(settings.MEDIA_ROOT, self.tempfile) 
        if os.path.exists(path):
            os.remove(path)
            
    def testPermenantStorageIsPermenant(self):
        storage = PermenantStorage()
        path = storage.save(self.tempfile, ContentFile('new content'))
        self.assertEquals(path, self.tempfile)
        self.assertEquals(11, storage.size(path))
        self.assertEquals('new content', storage.open(path).read())
        storage.delete(path)
        self.assertTrue(storage.exists(path))

class ViewsTest(TestCase):
    def testDemo(self):
        response = self.client.get('/rtv/demo/')
        self.failUnlessEqual(response.status_code, 200)

    def testInfo(self):
        response = self.client.get('/rtv/publish-queue/')
        self.failUnlessEqual(response.status_code, 200)

    def testUpload(self):
        response = self.client.get('/rtv/upload/')
        self.failUnlessEqual(response.status_code, 200)
        # this test needs to also check the ability to upload and therefore test
        # the redirect on to rtv.views.success


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
        vid = TranscodeJob.objects.create(user=self.user, title='test video')
        ext = os.path.splitext(vfh.name)[1] 
        vid.raw.save('tmp'+ext,vfh, save=True)
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
        self.assertTrue(os.path.exists(self.vid.raw.path))
        
    def testGetSetInfo(self):
        self.vid.set_info()
        self.assertTrue(len(self.vid.info) > 0)
        info_type = type(self.vid.get_info())
        self.assertNotEquals('str', info_type)
        self.assertTrue('dict', info_type)
        self.assertTrue('video' in self.vid.get_info())
        
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
        self.vid.set_info()
        self.assertEqual(self.vid.status, self.vid.STATUS_PROCESSED)
        self.assertTrue(os.path.exists(self.vid.ogv.path))
        self.assertTrue(os.path.exists(self.vid.mp4.path))
        self.assertTrue(os.path.exists(self.vid.thumbnail.path))
        tj = self.vid
        Video.objects.create(user=tj.user.username, raw=tj.raw.url, 
                             raw_info=tj.info, mp4=tj.mp4.url, ogv=tj.ogv.url, 
                             thumbnail=tj.thumbnail.url, dc={'title':tj.title})

