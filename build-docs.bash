SCRIPT=`which $0`
ROOT=`dirname $SCRIPT`
export DJANGO_SETTINGS_MODULE=myproject.local_settings
PATH=$ROOT/bin:$PATH
$ROOT/bin/sphinx-build -b html -d $ROOT/docs/_build/doctrees   $ROOT/docs/ $ROOT/docs/_build/html
