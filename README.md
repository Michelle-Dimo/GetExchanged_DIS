# GetExchanged
## Setup instructions

Run the application by using Docker:

```shell
docker compose up --build
```

Or install dependencies manually, preferably inside a virtual environment:

```shell
pip install -r requirements.txt
```

## Environment configuration

Create a `.env` file in the root directory and add:

```shell
POSTGRES_DB=ku_exchange
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secret
```

Make sure PostgreSQL is running and the database exists.

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
/ → index page  
/home → Home page  
/about → About page  
/profile → Enter profile page

### Authentication
/login → Login page  
/signup → Signup page  
/logout → Logout user  

### Profile page
/my_repotrs → View created reports  
/edit-profile → Edit profile information  
/my_agreements → View saved agreements  
/my_applications  → View your applications  

### Details
/api/map-data → Maps the universities worldwide  
/search → search bar to navigate the website  
/reports → View and create reports   
/reports/university → Read the reports of each university 
/agreements → View agreements   
/agreements_text → Read the agreements for each university  

---

## Known backend issues

- Database constraints could be improved
- 

---

## Known frontend issues

- Navigation flow can feel inconsistent

---

## Project structure

GetExchanged/
├── app/
│   ├── __init__.py
│   ├── agreements.py
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
├── .gitattributes
├── .gitignore
├── Doskerfile
├── entrypoint.py
├── docker-compose.yml
└── README.md

---
