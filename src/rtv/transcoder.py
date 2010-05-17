import sys, os, tempfile
from subprocess import Popen, PIPE, STDOUT

class TranscodeError(Exception):pass

class GenericConverter(object):
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
        base,ext = os.path.splitext(os.path.basename(src))
        root = os.path.dirname(src)
#        dst = os.path.join(root, base+self._suffix+self._ext)
        dst = tempfile.NamedTemporaryFile(suffix=self._suffix+self._ext, prefix='trans', 
                                          delete=False)
        dst.close()
        replacements = {'bin': self._bin, 'src': src, 'dst': dst.name}
        commands = [cmd % replacements for cmd in self._cmds]
        for command in commands:
            process = Popen(command, stdout=PIPE, stderr=STDOUT)
            output = process.communicate()[0]
            if process.returncode != 0:
                raise TranscodeError(output)
        return dst.name

# command strings
SINGLE_PASS_H264 = [
'''%(bin)s -y -i "%(src)s" -ab 96k -vcodec libx264 -vpre slow -crf 22 -threads 0 "%(dst)s"''']
DOUBLE_PASS_H264 = [
'''%(bin)s -i "%(src)s" -an -pass 1 -vcodec libx264 -vpre slow_firstpass -b 15 -bt 15 -threads 0 "%(dst)s"''',
'''%(bin)s -i "%(src)s" -ab 128k -pass 2 -vcodec libx264 -vpre slow -b 15 -bt 15 -threads 0 "%(dst)s"''']

from rtv.settings import RTV_FFMPEG, RTV_FFMPEG2THEORA

FORMATS = {
'flv': {
    'ext': '.flv', 
    'bin': RTV_FFMPEG, 
    'cmds': ['''%(bin)s -y -i "%(src)s -ab 96k -vcodec libx264 -vpre slow -crf 22 -threads 0 "%(dst)s"''']},
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

#flash = GenericConverter(**FORMATS['flv'])
theora = GenericConverter(**FORMATS['ogv'])
h264 = GenericConverter(**FORMATS['mp4'])
#h264_2pass = GenericConverter(**FORMATS['mp4-2pass'])
jpeg = GenericConverter(**FORMATS['jpg'])
