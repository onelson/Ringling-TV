"""
This command is used to bulk add/import the app's required content models to 
the fedora repo.
"""

import sys
from django.core.management.base import CommandError, NoArgsCommand
from rtv.fedora.cmodels import install_episode

class Command(NoArgsCommand):
    help = 'add required content models to fedora repo'
    def handle_noargs(self, *args, **kwargs):
        install_episode()
        # Done
        sys.exit(0)
