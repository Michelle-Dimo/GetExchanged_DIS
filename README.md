# GetExchanged
## Setup instructions

### Run the application by downloading Docker, and run the following in the terminal:

Clone git repository
```shell
git clone https://github.com/Michelle-Dimo/GetExchanged_DIS.git
```

Go into the project
```shell
cd GetExchanged_DIS
```

Build and run the app
```shell
docker compose up --build
```
After the first time of running the app `--build` can be excluded from the command.

### Or install dependencies and run the app manually (for MacOS or Linux users):

Create a virtual python environment

```shell
python -m venv venv_name
```
Switch to using the python in the virtual environment
```shell
source venv_name/bin/activate
```

Go into the virtual environment directory
```shell
cd venv_name
```

Clone git repository
```shell
git clone https://github.com/Michelle-Dimo/GetExchanged_DIS.git
```

Install python packages
```shell
pip install -r requirements.txt
```

Go into the project
```shell
cd GetExchanged_DIS
```

Initialize the database
```shell
python app/init_db.py
```

Start the app
```shell
flask run --app app
```

## Folder setup
The app is devided into multiple folder, as follows:

- app/ → Main Flask application  
  - static/ → CSS style file and favicon 
  - templates/ → all HTML templates  
  - pycache/ → Python cache  
- data/ → Scraped datasets  
- scripts/ → Contains scripts for scraping, etc.

---

## Application architecture

- init.py → Initializes Flask app and DB connection  
- init_db.py → Contains the Database 
- main.py → Blueprint and routes
- auth.py → User authentication and routes

---

## Routes
### Core
/ → home page  
/about → About page  
/profile → Enter profile page

### Authentication
/login → Login page  
/signup → Signup page  
/logout → Logout user  

### Profile page
/edit-profile → Edit profile information    
/my_applications  → View your applications  

### Details
/api/map-data → Maps the universities worldwide  
/search → search bar to navigate the website  
/api/live-search → View the searching results  
/reports → View and create reports   
/reports/university → Read the reports of each university 
/agreements → View agreements   
/agreements_text → Read the agreements for each university  
/apply/<int:agreement_id → applying to a university via the agreement  

---

## Known issues with the application
- The site can be a little slow in loading the application, especially in the search function.

## Ideas that were not yet implemented
- The alumni/applicant function should limit the users access to fx. apply to a university.
- This function should also make it possible for an alumni to write reports from their visited universities.
- This function should also make it possible for an applicant to save reports from universities they want to visist.
- The agreements page for a specific university should have a button which links to the reports of this university.
- When a person has applied to an agreement, their application shows under __my applications__ with a link to the agreement, but the page does not directly show which institution the user has applied to.
- The search function does not show where the specific search word appears in the search results, but simply all the reports and agreemenst that the words appear in.

---

## Project structure

GetExchanged/  
├── app/  
│   ├── __init__.py  
│   ├── agreements.py  
│   ├── reports.py  
│   ├── auth.py  
│   ├── int_db.py  
│   ├── main.py  
│   ├── static/  
│   ├── templates/  
│   └── __pycache__/  
├── data/  
├── instance/  
├── scripts/  
├── requirements.txt  
├── .env  
├── .gitignore  
├── Doskerfile  
├── entrypoint.py  
├── docker-compose.yml  
└── README.md  

---

## Other notes about the project
- The ER diagram has been updated to match our final project. But the attributes to both reports and agreements does not match entirely, because there are too many columns in the actual database. These columns have been simplified into the attribute __text__.
- The study field attribute in reports would originally be defined by the specific user that made the report. But since no user can make any reports, this becomes an entity in itself. However, we had a hard time adding the study_fields entity to the ER diagram as an associative entity, but that only holds if there is not a many-to-many relationship between agreements and study_fields, and a many-to-many relationship between university and study-fields (Two many-to-many relationships makes it impossible to include an associative entity, at least with our current database structure)
