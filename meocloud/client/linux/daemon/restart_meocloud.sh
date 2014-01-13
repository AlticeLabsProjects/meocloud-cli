#! /bin/bash

if which meocloud 2>&1 > /dev/null
then
    meocloud stop 2>&1 > /dev/null
    meocloud start 2>&1 > /dev/null
fi
