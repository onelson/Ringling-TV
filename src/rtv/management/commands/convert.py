from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import sys

class Command(BaseCommand):
    
    help = ''
    
    option_list = BaseCommand.option_list + (
        make_option('--out', '-o', 
                    dest='format',
                    action='store',
                    type='string',
                    help='destination format'
        ),
    )
    
    def handle(self, *args, **opts):
        pass