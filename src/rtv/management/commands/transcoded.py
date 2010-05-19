from django.core.management.base import NoArgsCommand, CommandError
from optparse import make_option
import sys, os, time, logging


from django.conf import settings
from django.db import connection
from rtv.models import TranscodeJob
from rtv.transcoder import TranscodeError

LOG_FILE = os.path.join(settings.PROJECT_ROOT,'tmp','transcoded.log')
logging.basicConfig(filename=LOG_FILE,level=logging.DEBUG)

LOG = logging.getLogger('Transcode.d')
LOG.addHandler(logging.StreamHandler())

class Command(NoArgsCommand):

    def handle_noargs(self, **opts):
        LOG.info('== init ==')
        while True:
            connection.close()
            try:
                job = TranscodeJob.objects.filter(
                    status=TranscodeJob.STATUS_PENDING)[0]
                logging.info('starting <TranscodeJob: %d>' % job.pk)
                try:
                    job.transcode()
                    logging.info('<TranscodeJob: %d> done.' % job.pk)
                except TranscodeError, err:
                    logging.error(err)
            except IndexError:
                logging.debug('waiting...')
                time.sleep(10)