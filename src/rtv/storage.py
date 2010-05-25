from django.core.files.storage import FileSystemStorage

class PermenantStorage(FileSystemStorage):
    """
    Permenant storage works just like file-system storage, but does not ever
    clean up after itself.
    """
    def delete(self, *args, **kwargs): pass
