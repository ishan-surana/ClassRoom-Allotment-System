# ClassRoom Allotment System
This is the repository containing the files for the project I created for my DBS Lab (IT - Sem 4). The project was developed with the purpose of automate and streamline the process of room reservation and allocation within 
academic institutions, taking reference of the manual process followed at our institution (MIT Manipal) and integrating the entire process within a single application, enhancing efficiency, transparency, and user satisfaction. 
The backend is a **Flask** app with 3 Blueprint templates (types of users), and utilises HTML, CSS and JS for frontend. 
The database used here is **SQLITE3** due to its flexibility and ease of usage. 

The main deployment of the app is [here](https://classroom-allotment-system.onrender.com).

This work is licensed under [**CC BY-NC-ND 4.0**](LICENSE.md). Please refer the license for more details regarding freedom of use.

## Directory structure and Project files
- [app.py](app.py):- The backend, which handles authentication, queries to the database and all the routes of the app, is an app made using the Flask framework in Python3.
  It handles the auth through various functions of Flask, and runs queries through the sqlite3 library present in Python3. It handles all the data received through `GET` or `POST` requests,
  and carries out the specified functions under the accessed route. It also takes care of the *mail API* developed for the first stage of the application (the faculty advisor), since it is more convinient
  for an FA to just check their mail for the requests of their assigned club and approve/reject.
- [templates](templates):- 3 groups of templates are utilised - **user**, **sw** and **so**.
  + [user](templates/user) => The user portal is for the intended applicants, that is any club, student project or event organizer that wishes to utilise a room.
  They can make request for any room by filling out the form, which is dynamically updated to show the status of the rooms. The block is coloured ![](https://img.shields.io/static/v1?label=&message=gray&color=gray) if anyone has his application is progress for that room, therefore,
  the application can be rejected anytime and there is a chance for that room to get free soon. Confirmed booked room is coloured with ![](https://img.shields.io/static/v1?label=&message=red&color=red), hence, it will only get free after the request time ends. The user can select
  multiple rooms, all of which will be marked ![](https://img.shields.io/static/v1?label=&message=blue&color=blue). The user can see request bars of all of their requests dynamically updating through the scripts running continuously.
  + [sw](templates/sw) => The sw portal is for the ***Student Welfare*** office, that is, the 2nd stage of the application. They have the functionality to approve/reject requests made by any club/sp and approved by the respective
    FA. The request is then passed to so for the final stage of the application.
  + [so](templates/so) => The so portal is the final stage of the application, that is approval by the ***Security Office***. They approve/reject the request based on updates on room availability in case of any last minute changes
    and is essentially, the physical check before the approval.
  + [admin](templates/admin) => Hidden admin portal, can see all of the requests made by anyone at any stage. They have the power to completely approve or reject the request.
- [static files](static):- Static files, including images used and the favicon.ico.
- [database](classroom_allotment_system.db):- The sqlite3 database used as the data storage. It has 9 tables - **clubs** (club details along with fa email), **clublogin**, **requests** (ongoing requests), **status**
 (status of requests), **slots** (slots of the confirmed requests), **rooms**, **swlogin**, **sologin** and **deleted_requests**. It also has 2 *views* (as created in the app) and a *trigger* set on deletion on requests.
- [maintainance script](maintainance.py):- A maintainance script created to reduce load of the requests table, by deleting requests whose end time and date is before the time and date of when the script is running. It
  will run every 86400 seconds (ie, every day) if the line `import maintainance` is commented out from the app.
