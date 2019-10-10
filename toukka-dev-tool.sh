#!/bin/bash

case "$1" in

    test)
        nose2-3
        ;;

    clean)
        #py3clean -v toukka
        find . -regex '^.*\(__pycache__\|\.py[co]\)$' -delete
        ;;

    pylint)
        pylint3 toukka
        ;;

    flake8)
        flake8
        ;;

    mypy)
        mypy toukka
        ;;
    dev-test)
        python3 -X dev ./toukka-cmd --version
        python3 -X dev ./toukka-experimental --version
        python3 -X dev ./toukka-spotify --version
        python3 -X dev ./toukka-spotify-manager --version
        python3 -X dev ./toukka-spotify-watcher --version
        ;;
    # TODO: python3 -X importtime
    *)
        echo "Unknown command"
        exit 1
        ;;

esac

