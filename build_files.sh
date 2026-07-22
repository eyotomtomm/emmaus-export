#!/bin/bash

pip install -r requirements/base.txt
pip install "fido2>=1.1,<2.0"
python manage.py collectstatic --noinput
