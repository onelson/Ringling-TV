
from myproject.settings import *
DEBUG=True
TEMPLATE_DEBUG=DEBUG
if 'django_nose' not in INSTALLED_APPS: 
    INSTALLED_APPS.append('django_nose')

TEST_RUNNER = 'django_nose.run_tests'

NOSE_ARGS = [
'--with-xunit', 
'--xunit-file='+os.path.join(PROJECT_ROOT,'tmp','nosetests.xml'),
'--with-coverage',
'--cover-package=rtv',
]