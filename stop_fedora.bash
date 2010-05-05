#!/bin/bash

SCRIPT=`which $0`
echo $SCRIPT
DIR=`dirname $SCRIPT`
FEDORA_HOME=$DIR/parts/fedora
CATALINA_HOME=$FEDORA_HOME/tomcat
echo "FEDORA_HOME: $FEDORA_HOME"
echo "CATALINA_HOME: $CATALINA_HOME"
$CATALINA_HOME/bin/shutdown.sh