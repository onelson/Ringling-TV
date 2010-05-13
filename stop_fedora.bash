#!/bin/bash

SCRIPT=`which $0`
echo $SCRIPT
DIR=`dirname $SCRIPT`
export FEDORA_HOME="$DIR/parts/fedora" && export CATALINA_HOME="$FEDORA_HOME/tomcat" && sh "$CATALINA_HOME/bin/catalina.sh" stop
