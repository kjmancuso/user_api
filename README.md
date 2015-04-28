user_api
========

Playground for simple API to fool around with simple user entities.

Prereqs
-------

Only Flask, rest uses standard library.


Installation
------------

The **lazy way**, assuming site virtualenv, git, and pip are all happy.

```bash
curl https://raw.githubusercontent.com/kremlinkev/user_api/master/bootstrap.sh | bash
```
This will do the following:

- Create a venv named ```kremlinkev_user_api``` into your working directory
- Checkout this repo into ```src/```
- Install requirements
- Run the app

Else the **manual method** of the following after checking out the repo:
```bash
pip install -r requirements
python user_api.py
```

Tests
-----

Rudimentary unit tests are located in ```run_tests.py```
