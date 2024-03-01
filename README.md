# Clinical Data Report Project

## Description

The Clinical Data Report Project is a Django-based application designed to help manage and maintain clinical data efficiently.

## Setup

Follow these steps to set up and run the project:

```bash
git clone https://github.com/AndronicusLepcha/Clinical-Data-Report-Project.git
cd Clinical-Data-Report-Project

python -m venv venv

# On Windows:
.\venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate

# Optional: Create superuser
python manage.py createsuperuser

python manage.py runserver