# Website for stuartmccall.ca and northlightimages.com

This Django application displays images in a quick and friendly gallery interface. It is designed for <https://www.stuartmccall.ca> and <https://www.northlightimages.com>.

## Usage

Create a Python virtual environment and install the application in editable mode:

    python3 -m venv .venv
    ./.venv/bin/pip install -e .

Install Node package dependencies:

    npm install

Create a copy of local_settings.py and change it in your favourite editor:

    cp artsite/local_settings.example.py artsite/local_settings.py
    open artsite/local_settings.py

Run the application using WSGI, or use the Django test server:

    ./venv/bin/manage.py runserver

## Authors

Dylan McCall <dylan@dylanmccall.com>
