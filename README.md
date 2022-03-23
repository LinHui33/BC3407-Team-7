# BC3407 Project

- XYZ Hospital Data Portal
- Deployed at: https://hospital-data-portal.herokuapp.com/
    - Automatic deployments from github
      enabled https://stackoverflow.com/questions/39197334/automated-heroku-deploy-from-subfolder
    - usernames/passwords: admin/admin1234 , nurse/nurse1234

# Current Progress:

1. Data was cleaned and stored in an sqlite database. In total, 3 tables were created from the original dataset
    1. Appointments: Contains appointment details. Each row corresponds to an appointment, and related to a user.
        1. TODO: Incorporate past ML performance as a separate column
    2. Users: Contains user unique characteristics. Each row corresponds to a user.
    3. Login: Contains username, hashed password & access_level
2. User Access
    1. Login/Logout functions were implemented
    2. TODO: Finalize what the nurse/admin can/cannot do
       1. Nurse: Can view all pages except for ML model & Manage Users, Add, Edit & Remove Appointments & Patients
       2. Admin: Can do and see everything, including performance of ML Model & Manage Users
3. Home Page
    1. Interactive gantt chart & data table for current date's appointments
        1. filtering of data table while clicking on chart
        2. TODO: Expected no-show rates for current date
        3. TODO: ML Insights (e.g. Looking at the next 2 weeks, expected no-show is 50%. Advised to overbook
           appointments to maximize capacity.)
    2. Create Appointments: Popup modal to create new appointment
    3. Create Patient: Popup modal to create new patient
4. Appointment Screener with filters
    1. TODO
5. Patient Screener with filters
    1. TODO
6. Dashboard with Past ML Performance
    1. TODO

# Known Limitations:

1. Application is hosted online on Heroku Any changes made to data files deployed together with the application will not
   persist - e.g. updates to sqlite .db files while deployed online will only remain temporarily for ~30mins
    1. Workarounds for this include utilising a cloud DB service (e.g. Heroku's PostgreSQL, or using other cloud
       services/databases)
    2. For simplicity's sake, we will assume that this data portal will be deployed on the Hospital's intranet, where
       changes made to data files will persist. The current deployment only serves as a Proof-of-Concept.
2. Flask-login may at times seem a little buggy due to Heroku Deployment
    1. Resolved by appending '--preload' to procfile, with reference
       to https://stackoverflow.com/questions/39684364/heroku-gunicorn-flask-login-is-not-working-properly
    2. Deployment on the Intranet will not require Procfile, gunicorn, or the specification of server in index.py

# Project Instructions

As the world struggles to contain the ever-changing variants of COVID-19, healthcare industry is facing tremendous
stress from issues arising from different aspects. One significant issue is on resource allocation and utilization.
Building additional hospital facility may not be a viable solution in a land scarce country like Singapore. One long
standing problem among resource utilization is due to missed appointments. When patients do not show up following their
appointment time, the missed appointment results in a waste of resources that have been scheduled and planned. There has
not been good solution in reducing the no-show rates. In some, the rates are not even been tracked or computed.

You are to create a Python-based program that can be useful for healthcare industry in tackling this issue. This program
is a prototype or proof-of-concept to path the implementation for subsequent development solution to be integrated to
the existing system. You are given a sample dataset to start with. It comes with past records of patients who show-up or
did not show-up for the appointment in a clinic. You can use it as a start, to develop a suitable solution to provide
insights to healthcare professionals. The solution can be a dashboard, web-based or command prompt program. The
objective is to apply what you have learnt in this course into this problem domain.

The following table displays the first 5 records from the attached dataset “appointmentData.csv”. It includes the age
and gender information of patients. Followed by the time they registered for the appointment and the appointment time
details. The day name of appointment is reflected. The other details like their health condition, and other relevant
features are also captured. The last column “Show Up” denotes if the patient shows up for the medical appointment.

Below are some questions you can try to answer or features you can try to include, you can address one or more of the
following or suggest other relevant questions:

1. How is the overall picture of no shows over the period?
2. No-show made up of how many percent of the given data?
3. What kind of people or age group likely to no-show? Or it’s random?
5. Does sending reminder helps with reducing no-show?
6. Provide appropriate dashboard or visualization features to summarize the given data set for viewing.
7. Suggest or implement suitable features that can help with reducing no-show or highlight patients more likely to
   no-show with additional reminders or etc?

Alternatively, you can look for additional dataset that can help with understanding or tackling this issue or for better
resource planning in healthcare. For example, the healthcare resources data, infection rates, chronic disease rates etc.
You can make assumptions on information not stated in this requirements, or target a certain specialist clinic.

All work must be done in the Python programming language.

Deliverables:
Prepare a zip file (in .zip format only) containing the relevant deliverables below:
Report: One word or pdf file containing the proof-of-concept prototype with the following content:
Work/responsibility distribution. Which team members in charge of which part of the program. Objective of the project
and how it addresses the issue. Features/Functionalities designed for the prototype. User manual with print screens from
the prototype to illustrate how to use this project's program; consider different user roles. Include the links to
recording, i,e. the hyperlinks to every group member’s individual recorded videos. Do not submit video files, submit
only hyperlink. One folder containing additional dataset (if any), all working files.

One group submit one copy of the above. Submission box will be opened in Week 11. All works submitted will go through
plagiarism checker. Submitting work done by others will result in failing the module directly.

No presentation nor lesson on week 13, you are to prepare the recording beforehand and submit before due date. Recording
replaces class presentation. The duration of each group member’s individual recording should be about 2 to 3 minutes
maximum. You are advised to adhere to the time limit strictly or penalty will be imposed. In the individual video, you
are required to reflect on your contribution to the group project, what you have done for the project, what have you
learnt from the project. Each group member will record his/her own video and ensure that the hyperlink to the video is
included on the first page of the report submitted by the group. You can use Zoom, Teams or YouTube for recording. If
you use other software to record into mp4 file, upload online to Youtube, OneDrive or other cloud storage (Do not submit
video files). In the case of Youtube, indicate as restricted, and submit only the link information. Include the link
information (one link for each team member) in your report.

You are required to submit a peer evaluation form online individually at the end of the semester. Individual peer
evaluation submission is compulsory for all team members. An online peer evaluation system will be opened nearer to the
submission date.

Good project outcome is the end product of good teamwork. We hope to see all team members contribute equally. The peer
evaluation will be considered in evaluating the project grade should the contribution be significantly unequal.
Submission will be kept confidential.

Due Date:
Week 13 Wednesday (13 Apr 2022, 7 p.m.)