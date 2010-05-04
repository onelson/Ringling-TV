START_DIR=`pwd`
ROOT=`which $0`
DOCS_DIR=`dirname $ROOT`/docs
export DJANGO_SETTINGS_MODULE=myproject.local_settings
PATH=$DOCS_DIR/../bin:$PATH
make --directory=$DOCS_DIR "$@"
echo 'Done.'
