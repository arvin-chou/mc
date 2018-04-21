#! /bin/sh
DIR=$(dirname $0)
LOG_DIR=$DIR/../logs

if [ ! -d "$LOG_DIR" ];
then
  mkdir $LOG_DIR
fi
