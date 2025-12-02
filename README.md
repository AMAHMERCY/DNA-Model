cd your_project_folder

For windows use the following
python -m venv venv
source env/Scripts/activate

For MAC OS use and linux user use the following
python3 -m venv venv
source venv/bin/activate

install dependencies with the following
pip install -r requirements.txt
pip install numpy pandas xgboost

User should run migration before running the server
python manage.py migrate

finally you can run
py manage.py runserver
