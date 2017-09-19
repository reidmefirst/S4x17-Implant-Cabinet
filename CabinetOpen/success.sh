#!/bin/bash
echo -e "SOLID SNAKE SAYS:\n\n" | lpr
inkscape --without-gui --export-pdf=/dev/stdout robot-success.svg | lpr
echo -e "\n\n\n\n"|lpr
