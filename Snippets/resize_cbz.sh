#!/bin/bash

set -o errexit -o nounset

resize() {
    local f; for f in "${@:2}"; do
        aunpack -Fzip "$f"
        mogrify -verbose -resize "$1" "${f%.cbz}"/*
        apack -f -Fzip "$1 $f" "${f%.cbz}"
    done
}

help() {
    echo 'dotcbz resize <geometry> <cbz...>'
    echo '  geometry: https://www.imagemagick.org/Magick++/Geometry.html'
    exit 1
}

case ${1:-} in
    resize) resize "${@:2}";;
    *) help;;
esac
