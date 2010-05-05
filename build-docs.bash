START_DIR=`pwd`
ROOT=`which $0`
ROOT=`dirname $ROOT`
PATH=$ROOT/bin:$PATH
DOCS=$ROOT/docs
export DJANGO_SETTINGS_MODULE=myproject.local_settings
echo "Building docs in [$DOCS]"
sphinx-build -b html -d $DOCS/_build/doctrees $DOCS $DOCS/_build/html
echo 'Done.'
