from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import sys, os

from rtv.transcoder import jpeg, theora, h264

# binding converter functions to 'format' command line options
convert = {
    'flv': flash,
    'ogv': theora,
    'mp4': h264,
    'jpg': jpeg,
}

class Command(BaseCommand):
    help = 'generate derivative from source video'
    option_list = BaseCommand.option_list + (
        make_option('--out', '-o', 
                    dest='format',
                    action='store',
                    type='string',
                    help='destination format'
        ),
    )
    
    def handle(self, *args, **opts):
        file = args[0]
        convert[opts['format']](file)
        sys.exit(0)