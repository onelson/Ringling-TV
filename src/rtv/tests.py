from django.test import TestCase
from django.conf import settings
from django.core.files import File
from django.contrib.auth.models import User
from rtv.models import TranscodeJob
import os

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
        self.tmpfile = vid_file
        self.created_vid['pk'] = vid.pk
        self.created_vid['path'] = vid.source.path
    
    def setUp(self):
        self.user = User.objects.get(username='meg')
        self.createFakeVid()
        
    def tearDown(self):pass

    def testCanCreate(self):
        self.assertTrue(os.path.exists(self.created_vid['path']))
    def testCanGet(self):
        obj = TranscodeJob.objects.get(pk=self.created_vid['pk'])
        self.assertEqual(os.path.getsize(obj.source.path), self.created_vid['size'])
    
    def testCanTranscode(self):
        obj = TranscodeJob.objects.get(pk=self.created_vid['pk'])
        obj.transcode()
        self.assertEqual(obj.status, obj.STATUS_PROCESSED)
        self.assertTrue(os.path.exists(obj.ogv.path))
        self.assertTrue(os.path.exists(obj.mp4.path))
        self.assertTrue(os.path.exists(obj.thumbnail.path))
    
    def testCanDelete(self):
        obj = TranscodeJob.objects.get(pk=self.created_vid['pk'])
        obj.delete()
        self.assertFalse(os.path.exists(self.created_vid['path']))