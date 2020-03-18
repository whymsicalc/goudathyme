# ![Gouda Thyme Logo](https://github.com/whymsicalc/goudathyme/blob/master/static/images/gouda-time-logo-dark.png "Gouda Thyme")

Gouda Thyme is a full stack web app, built during Hackbright's Project Season that allows users to track items in their kitchen, receive text updates when an item is about to expire, create a grocery list based on ingredients user is low on, find recipes based on items in their kitchen, and search for recipes based on selected search criteria (e.g. dietary restrictions, cuisine, prep time).

### Contents

* [Technologies](#techstack)
* [Installation](#installation)
* [Features](#features)
* [Upcoming Features](#futurefeatures)
* [About The Developer](#aboutme)

## <a name="techstack"></a>Technologies

Tech Stack: Python, JavaScript, HTML, CSS, Flask, Jinja, jQuery, AJAX, PostgreSQL, SQLAlchemy, Bootstrap, unittest, Select2 Library, Schedule Library, Requests Library <br>
APIs: Spoonacular, Twilio

## <a name="installation"></a>Installation

### Prerequisites

You must have the following installed to run Gouda Thyme:

- PostgreSQL
- Python 3
- API key for Spoonacular and Twilio
- Requests Library 
- <a href="https://github.com/atrnh/schedule">Schedule Library</a>

### Run Gouda Thyme on your local computer

Clone or fork repository:
```
$ git clone https://github.com/whymsicalc/goudathyme
```
Create and activate a virtual environment inside your goudathyme directory:
```
$ virtualenv env
$ source env/bin/activate
```
Install dependencies:
```
$ pip install -r requirements.txt
```
Create a secrets.sh file to add your API keys and secret keys, eg:
<br><br>
![api](https://github.com/whymsicalc/goudathyme/blob/master/static/images/readme_api.png)

Add Variables to Environment:
```
$ source secrets.sh
```
Create database 'kitchen':
```
$ createdb kitchen
```
Run model.py interactively in the terminal, and create database tables:
```
$ python3 -i model.py
>>> db.create_all()
>>> quit()
```
Run the app from the command line.
```
$ flask run
```

## <a name="features"></a>Features

![Homepage](https://github.com/whymsicalc/goudathyme/blob/master/static/images/readme_homepage.png)
<br>

#### Register <br>

![Register](https://github.com/whymsicalc/goudathyme/blob/master/static/images/readme_register.png)
<br>

#### Login <br>

![Login](https://github.com/whymsicalc/goudathyme/blob/master/static/images/readme_login.png)
<br>

#### My Kitchen <br>

Users can add items to their virtual kitchen and edit expiration date, running low and notes on items. The day before an ingredient expires, users will get a text reminding them!
![My Kitchen](https://github.com/whymsicalc/goudathyme/blob/master/static/images/readme_my_items.gif)
<br>

#### Grocery List <br>

Users can see a list of ingredients they marked as running low and can update as they go grocery shopping.
![Grocery List](https://github.com/whymsicalc/goudathyme/blob/master/static/images/readme_groceries.png)
<br>

#### Recipes <br>

Users can see recipes they can make based on ingredients they have in their virtual kitchen.
![Recipes](https://github.com/whymsicalc/goudathyme/blob/master/static/images/readme_recipes.png)
<br>

#### Recipe Search <br>

Users can search for recipes based on search criteria they choose.
![Recipe Search](https://github.com/whymsicalc/goudathyme/blob/master/static/images/readme_recipe_search.gif)
<br>

## <a name="futurefeatures"></a>Upcoming Features

* Update Recipe Search: Spoonacular said they would update their complex search endpoint to have an option to search and filter recipes using all the ingredients a user has in their kitchen. Once the endpoint is added, I plan to update the "Search Recipes" page to utilize it.
* Update Twilio Integration: I only registered for a trial Twilio account. I need to update my account to send texts to all users who register. 

## <a name="aboutme"></a>About the Developer

Amber Chan graduated from UC Berkeley with a degree in Psychology with numerous HR related courses under her belt. She wanted to eventually work within a team where she could help add to, build, and shape company culture to improve employee performance and happiness. In her last job at a tech startup, she had the opportunity to provide feature feedback to product managers and engineers. She wanted to be a part of that process and to build and create great user experiences. Through Hackbright, she’s grown to enjoy the puzzle piecing aspect and challenge of programming even more than she has before. She is excited to learn and develop her skills even further after Hackbright. Gouda Thyme is her first full stack project. She can be found on [LinkedIn](https://www.linkedin.com/in/amber-chan-38634396/) and on [Github](https://github.com/whymsicalc/).