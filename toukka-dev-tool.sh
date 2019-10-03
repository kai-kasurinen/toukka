#!/bin/bash

case "$1" in
    test)
        nose2-3
        ;;

    clean)
        py3clean -v toukka
        ;;
    *)
        echo "Unknown command"
        exit 1
        ;;
esac

