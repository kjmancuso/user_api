#!/bin/bash

virtualenv kremlinkev_user_api
git clone https://github.com/kremlinkev/user_api kremlinkev_user_api/src/
./kremlinkev_user_api/bin/pip install -r kremlinkev_user_api/src/requirements.txt
./kremlinkev_user_api/bin/python kremlinkev_user_api/src/user_api.py
