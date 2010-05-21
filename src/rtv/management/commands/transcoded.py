from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import sys, os, time, logging

import django.db.connection
refresh_db_connection = getattr(django.db.connection, 'close')

from django.conf import settings
from rtv.models import TranscodeJob
from rtv.transcoder import TranscodeError

LOG_FILE = os.path.join(settings.PROJECT_ROOT,'tmp','transcoded.log')
logging.basicConfig(filename=LOG_FILE,level=logging.DEBUG)

LOG = logging.getLogger('Transcode.d')
LOG.addHandler(logging.StreamHandler())

ACTION_HELP = 1
ACTION_START = 2
ACTION_STOP = 3
ACTION_RESTART = 4

ACTIONS = {
    'help': ACTION_HELP,
    'start': ACTION_START,
    'stop': ACTION_STOP,
    'restart': ACTION_RESTART,
}

ACTION_DEFAULT = ACTION_HELP
class Command(BaseCommand):
    action = ACTION_DEFAULT
    
    def _help(self): pass
    def _start(self):
        """
        TODO: This guy will be getting ported to the daemon style (see the huge 
        comment below this class).
        """ 
        LOG.info('== init ==')
        while True:
            refresh_db_connection()
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

    def _stop(self): pass
    def _restart(self): pass
    
    def handle(self, *args, **opts):
        try:
            self.action = ACTIONS[args[0]]
        except (KeyError, IndexError):
            if args:
                print >> sys.stderr, 'invalid choice [%s]' % args[0]
            else: 
                print >> sys.stderr, 'must specify action'
            
        for key in ACTIONS:
            """
            Looking up the str to go with the action int index, then grabbing
            self._<actionName> and stashing it for use below.  Kind of a silly 
            form of validation.
            """
            if self.action == ACTIONS[key]:
                run = getattr(self,'_'+key)
                break
        
        return run() # once we know how to delegate, just run it!


# This code was all stolen from another project I did.  The daemon was never 
# completed - it could start, and record its pid, but stop and restart were 
# never implemented.

'''from optparse import make_option
from django.core.management.base import CommandError, BaseCommand, NoArgsCommand
from django.conf import settings
from multiprocessing import Pool
import time, logging, os, multiprocessing
import django.db
from gmate.jobs.models import Job

def daemonize():
    """
    Detach from the terminal and continue as a daemon.
    """
    # swiped from twisted/scripts/twistd.py
    # See http://www.erlenstar.demon.co.uk/unix/faq_toc.html#TOC16
    if os.fork():   # launch child and...
        os._exit(0) # kill off parent
    os.setsid()
    if os.fork():   # launch child and...
        os._exit(0) # kill off parent again.
    os.umask(022)
    null = os.open("/dev/null", os.O_RDWR)
    for i in range(3):
        try:
            os.dup2(null, i)
        except OSError, e:
            if e.errno != errno.EBADF:
                raise
    os.close(null)

def start_daemon(opts):
    django.db.connection.close()
    daemonize()
    pf = open(opts['pidfile'],'w')
    pf.write(str(os.getpid()))
    pf.close()
    logging.basicConfig(filename=opts['logfile'])
    log = multiprocessing.get_logger()
    log.setLevel(logging.DEBUG)
    pool = Pool(processes=opts['processes'])
    while True:
        django.db.connection.close()
        jobs = Job.objects.filter(status=Job.STATUS_PREPARING, marked_for_deletion=False).values_list('id', flat=True).order_by('id')
        load = os.getloadavg()[0]
        log.info('jobs waiting <%s>' % str(jobs.count())) 
        if jobs:
            if load < opts['load']:
                log.info('starting job <%s>' % str(jobs[0]))
                pool.apply_async(run_submission, (jobs[0],))
            else:
                log.info('load is <%s>...' % str(load))
                log.debug('waiting <%s> seconds' % str(opts['interval']))
        time.sleep(opts['interval'])
        django.db.connection.close()

    
def run_submission(pk):
    django.db.connection.close()
    log = multiprocessing.get_logger()
    log.setLevel(logging.DEBUG)
    job = Job.objects.get(pk=int(pk))
    if job.status == Job.STATUS_PREPARING:
        job.submit()
    log.info('submitted job <%s>' % str(job.pk))

class Command(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option('--concurrency', '-c', 
                    dest='processes',
                    action='store',
                    type='int',
                    default=None,
                    help='max processes to spawn'
        ),
        make_option('--pidfile', '-p', 
                    dest='pidfile',
                    action='store',
                    type='string',
                    default=os.path.join(settings.PROJECT_ROOT,'logs','submitd.pid')
        ),
        make_option('--logfile', '-f', 
                    dest='logfile',
                    action='store',
                    type='string',
                    default=os.path.join(settings.PROJECT_ROOT,'logs','submitd.log')
        ),
        make_option('--load', '-l', 
                    dest='load',
                    action='store',
                    type='float',
                    default=1.0,
                    help='load threshold'
        ),
        make_option('--interval', '-i', 
                    dest='interval',
                    action='store',
                    type='int',
                    default=60,
                    help='polling interval (secs)'
        ),
    )
#    help = 'Help text goes here'
    
    def handle(self, *args, **opts):
        start_daemon(dict(opts))
        
    def stop_daemon(self,graceful=False):pass
    def restart_demon(self,graceful=False):pass''' 