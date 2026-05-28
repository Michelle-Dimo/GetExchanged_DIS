Todo liste DIS projekt 

Generelle krav til web.appen: 
- Interagere med database via SQL 
- Regular expression matching / cfg 

Bonus points: 
- Views: optional, could be a list/table of all agreements for a country or the act of filtering/sorting (✓) 
- Triggers: as a user, it could be uploading a report to the database (✓) 
- Stored procedures 

To-create: 
- Create sql database: store scraped data (database.sql) 
- Base_html: create base html file: webapp skeleton, how to interact with database 
- Sub_files: create html files for each sub-page 
- Style.css file(s) (again, for each sub-page) 
- Example report (optional) 

Sub-pages: 
- Homepage:  
-- Search function (regex matching)
-- Agreements, reports and profile (login)
- Reports page:  
-- Sorting function 
-- SQL statements 
-- World map 
- Agreements page:  
-- Sorting function 
-- SQL statements 
-- World map
- Login page:
-- Regex matching for recognizing existing username 
- Register page:
-- Regex matching to check for KU-ID 
- Profile_page (requires being logged in)? 
-- My_status (alumni/applicant) 
-- My_ratings (links to txt files, idk) 
-- My_agreements (links to PDF/txt files) 
-- My_applications (links to PDF/txt files) 
-- NB: 1 or 2 example profiles should be sufficient 

