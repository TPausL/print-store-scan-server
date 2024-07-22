# PrintStore

Scan 3D-printed products in order to keep track of the stock in a digital twin of the storage shelf.

## This repo

This repository contains the code for scanning the images and analyzing them and storing the result in the database.

## Notes for setup

1. Run the following command to install the dependencies:

   ```shell
   pip install -r requirements.txt
   ```

2. Run application in debug mode with
   ```shell
   flask --app main run --debug --host 0.0.0.0
   ```
   when you are in a venv or prepend `python -m` when running directly on your machine
