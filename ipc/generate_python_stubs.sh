#!/bin/bash
set -e

OWN_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $OWN_DIR

STUBS_PATH=../meocloud/client/linux/protocol

for protocol in daemon_core daemon_ui; do
    rm -rf ${protocol}
    rm -rf ${STUBS_PATH}/${protocol}

    thrift -gen py:new_style,slots ${protocol}.thrift

    rm gen-py/${protocol}/*-remote
    mv gen-py/${protocol} ${STUBS_PATH}

    rm -rf gen-py
done

