from django.core.files.storage import FileSystemStorage

class PermenantStorage(FileSystemStorage):
    """
    Permenant storage works just like file-system storage, but does not ever
    clean up after itself.
    """
    def delete(self, *args, **kwargs): pass
    def __unicode__(self):
        return unicode('<PermenantStorage>' % (self.pid  or 'undefined')[0])
    def __str__(self): 
        return str(self.__unicode__())
