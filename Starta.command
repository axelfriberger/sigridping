#!/bin/zsh
cd -- "${0:A:h}"
python3 watch.py
read '?Tryck Enter för att stänga.'
