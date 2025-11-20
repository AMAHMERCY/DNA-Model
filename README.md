cd your_project_folder

For windows use the following
python -m venv venv
venv\Scripts\activate

For MAC OS use and linux user use the following
python3 -m venv venv
source venv/bin/activate

install dependencies with the following
pip install -r requirements.txt or
pip install django djangorestframework djangorestframework-simplejwt

User should run migration before running the server
python manage.py migrate

finally you can run
py manage.py runserver
