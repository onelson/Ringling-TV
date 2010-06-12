import os, tempfile
from subprocess import Popen, PIPE, STDOUT

class TranscodeError(Exception):pass

class GenericConverter(object):
    '''
    To build a new command to be passed as a callable object
    to the GenericConverter class, start the command with the
    binary to be used, followed by whichever flags you wish to use.
        %(bin)s
    Next, use the location of file.
        "%(src)s"
    Any encoding settings from ffmpeg and ffmpeg2theora go here.
        ex: bitrate, -pass #, -threads #, etc.
    %(dst)s is the created temporary video file based on these 
    settings. 
    
    Name these as a conversion process by creating them in this format:
        NAME_OF_CONVERSION_PROCESS = [
            %(bin)s -flags "%(src)s" -encoding -settings "%(dst)s"]
    This can also be made into a list.
        NAME_OF_CONVERSION_PROCESS = [
            """%(bin)s -flags "%(src)s" -encoding -settings "%(dst)s"""",
            """%(bin)s -flags "%(src)s" -encoding -settings "%(dst)s""""]
            
    This configuration can be passed to the class in this format:
        NAME_OF_CONVERSION_PROCESS = GenericConverter(**settings)
            
    To configure settings for the extension, suffix, etc., change 
    what you wish them to be here.
        'my_settings': {
            'ext': '.mp4', 
            'bin': RTV_FFMPEG, 
            'cmds': SINGLE_PASS_H264,
            'suffix': '_h264'}
    '''
    _bin = ''
    _cmd = '%(bin)s %(src)s %(dst)s'
    _ext = ''
    _suffix = ''
    def __init__(self, bin, cmds, ext, suffix=''):
        self._bin = bin
        self._cmds = cmds
        self._ext = ext
        self._suffix = suffix
        
    def __call__(self, file):
        src = os.path.realpath(file)
        dst = tempfile.NamedTemporaryFile(suffix=self._suffix+self._ext, prefix='rtv.trans', 
                                          delete=False)
        dst.close()
        replacements = {'bin': self._bin, 'src': src, 'dst': dst.name}
        commands = [cmd % replacements for cmd in self._cmds]
        for command in commands:
            process = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True)
            output = process.communicate()[0]
            if process.returncode != 0:
                raise TranscodeError(output)
        return dst.name

# command strings
SINGLE_PASS_H264 = [
'''%(bin)s -y -i "%(src)s" -ab 96k -vcodec libx264 -vpre hq -crf 22 -threads 0 "%(dst)s"''']

# had issues doing the two pass - could just be some bad params...
DOUBLE_PASS_H264 = [
'''%(bin)s -i "%(src)s" -an -pass 1 -vcodec libx264 -vpre slow_firstpass -b 15 -bt 15 -threads 0 "%(dst)s"''',
'''%(bin)s -i "%(src)s" -ab 128k -pass 2 -vcodec libx264 -vpre slow -b 15 -bt 15 -threads 0 "%(dst)s"''']

from rtv.settings import RTV_FFMPEG, RTV_FFMPEG2THEORA

FORMATS = {
'ogv': {
    'ext': '.ogv', 
    'bin': RTV_FFMPEG2THEORA, 
    'cmds': ['%(bin)s -y -p pro "%(src)s" -o "%(dst)s"'],
    'suffix': '_theora'},
'mp4': {
    'ext': '.mp4', 
    'bin': RTV_FFMPEG, 
    'cmds': SINGLE_PASS_H264,
    'suffix': '_h264'},
'mp4-2pass': {
    'ext': '.mp4', 
    'bin': RTV_FFMPEG, 
    'cmds': SINGLE_PASS_H264,
    'suffix': '_h264-2pass'},
'jpg': {
    'ext': '.jpg', 
    'bin': RTV_FFMPEG, 
    'cmds': ['''%(bin)s -y -i "%(src)s" -vcodec mjpeg -vframes 1 -an -f rawvideo "%(dst)s"''']},
}

theora = GenericConverter(**FORMATS['ogv'])
h264 = GenericConverter(**FORMATS['mp4'])
# 2 pass is unused until we can get it to work consistently
#h264_2pass = GenericConverter(**FORMATS['mp4-2pass'])
jpeg = GenericConverter(**FORMATS['jpg'])
