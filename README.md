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
