#! /bin/sh
DIR=$(dirname $0)
# top layer
LOG_DIR=$DIR/../../../logs

if [ ! -d "$LOG_DIR" ];
then
  mkdir $LOG_DIR
fi
