# Project 9
## About the project 9
This project is realized with Django framework in order to create a website for book review.
The main goal is to a website which:
* Allow users to post theirs requests of reviews about a book or theirs reviews. 
* Follow the other users.
## About main struture
* Project: book_review
* Application: reviews
## Code organization
├── book_review
│   ├── book_review
│   │   ├── asgi.py
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── db.sqlite3
│   ├── manage.py
│   ├── media
│   │   └── images
│   └── reviews
│       ├── admin.py
│       ├── apps.py
│       ├── flake8-rapport
│       │   ├── back.svg
│       │   ├── file.svg
│       │   ├── index.html
│       │   └── styles.css
│       ├── forms.py
│       ├── __init__.py
│       ├── migrations
│       │   ├── 0001_initial.py
│       │   └── __init__.py
│       ├── models.py
│       ├── templates
│       │   ├── reviews
│       │   │   ├── includes
│       │   │   │   ├── header.html
│       │   │   │   ├── messages.html
│       │   │   │   ├── navbar.html
│       │   │   │   ├── review_info_snippet.html
│       │   │   │   ├── review_snippet.html
│       │   │   │   ├── review_snippet_without_border.html
│       │   │   │   ├── ticket_info_snippet.html
│       │   │   │   └── ticket_snippet.html
│       │   │   ├── review_create.html
│       │   │   ├── review_delete.html
│       │   │   ├── review_detail.html
│       │   │   ├── review_list.html
│       │   │   ├── review_update.html
│       │   │   └── users
│       │   │       ├── connection.html
│       │   │       ├── home.html
│       │   │       ├── own_posts.html
│       │   │       ├── register.html
│       │   │       ├── user_follows_delete.html
│       │   │       └── user_follows.html
│       │   └── tickets
│       │       ├── ticket_create.html
│       │       ├── ticket_delete.html
│       │       ├── ticket_detail.html
│       │       ├── ticket_list.html
│       │       └── ticket_update.html
│       ├── tests.py
│       ├── urls.py
│       └── views.py
├── README.md
├── requirements.txt
└── setup.cfg

## Process
1. Clone and launch the project:
```
git clone  https://github.com/ThiHieuLUU/OCProject9.git
cd OCProject9/

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt 

cd book_review/

python manage.py runserver
```
2. Check code with flake8
* See flake8 configuration in "setup.cfg" file.
* Check code in reviews application
```bash
cd reviews
flake8 --format=html --htmldir=flake8-rapport
```
* Result:
```bash
firefox flake8-rapport/index.html &
```
