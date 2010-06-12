"""
This command is used to remove the content models added by install-cmodels.
"""

import sys
from django.core.management.base import CommandError, NoArgsCommand
from rtv.fedora.cmodels import purge_episode

class Command(NoArgsCommand):
    help = 'purge content models in fedora repo'
    def handle_noargs(self, *args, **kwargs):
        try:
            purge_episode()
        except Exception, err:
            print >> sys.stderr, err