#!/bin/bash

DIR_BASE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# DIR_ENV="$(which python | xargs dirname)"
DIR_ENV=$DIR_BASE/venv

set -e 

    # Create Python virtualenv
    cd $DIR_BASE
    if [ ! -f ${DIR_ENV}/bin/activate ]; then
        printf "\n == Create Python virtualenv == \n"
        virtualenv -p python3 $DIR_ENV 
    fi 
    source ${DIR_ENV}/bin/activate

    # Update python env
    pip install -r requirements.txt

    printf "\n == Installed requirements == \n"

    # Build docs
    cd $DIR_BASE
    make html SPHINXBUILD="python ${DIR_ENV}/bin/sphinx-build"

    # Create TAR
    # if [[ ! -d "$DIR_BASE/output/" ]]; then 
    #     mkdir $DIR_BASE/output/
    # fi 
    # tar -czvf OasisLMF_docs.tar.gz -C build/html/ .
    # mv OasisLMF_docs.tar.gz $DIR_BASE/output/