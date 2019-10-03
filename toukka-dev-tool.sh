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

    *)
        echo "Unknown command"
        exit 1
        ;;

esac

