#!/bin/bash

# move this file to /usr/bin/pdf.sh
# (and give executable permissions)
# chmod u+x /usr/bin/pdf.sh

source /mnt/2050F97550F95250/Github/PDFtools/.venv/bin/activate

python /mnt/2050F97550F95250/Github/PDFtools/main.py "$@"