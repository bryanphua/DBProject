# DBProject
Development of database-based system on Django. Our database project aims to create an online dataset library that data scientists can use to find and share datasets to aid in their research projects.


# Team Members
Bryan Phua  
Jonathan Bei Qi Yang  
Loh Wei Quan  
Ooi Kai Lue  
Ruth Wong Nam Ying  

# Entity Relationship Diagram
![alt text](https://github.com/woshibiantai/DBProject/blob/master/ExtraResources/ERD.png "Logo Title Text 1")

# Database Schema

`To be added`

# How to run the program
First navigate to the root of the project in your terminal, then run:  
`>> python manage.py runserver`


Open [localhost:8000/](localhost:800/) in your favorite browser to view the web application. 
![alt text](https://github.com/woshibiantai/DBProject/blob/master/ExtraResources/home.png "Home page")

# Site Functionality

## Registration:
a new user has to provide necessary information; he/she can pick a login-name and a password. The login name should be checked for uniqueness. Use Django’s auth mode and session DB module for this.

## Following:
After registration, a user can choose to follow a dataset that he or she likes. (For our database, there’s no multiple copies of dataset, its either 1 or 0) But our datasets have a follow list that will increment when a new user follows it.
![alt text](https://github.com/woshibiantai/DBProject/blob/master/ExtraResources/follow.gif "Follow Dataset")

## User records:
Upon user demand, you should print the full record of a user:  
- his/her account information  
- his/her full history of followed datasets (dataset name, number of responders, date etc.)  
- his/his list of created datasets  
- his/her full history of comments  
- the list of all the comments he/she ranked with respect to usefulness
![alt text](https://github.com/woshibiantai/DBProject/blob/master/ExtraResources/profile.gif "User Profile")

## New Dataset:
The creator of the dataset records the details of a new dataset, such as genre and description. For the purposes of this project, datasets will merely serve as placeholders.
![alt text](https://github.com/woshibiantai/DBProject/blob/master/ExtraResources/create.gif "Create new Dataset")

## Comment recordings:
Users can record their comments for a dataset. You should record the date, and an optional short text. No changes are allowed; only one comment per user per dataset is allowed.

## Usefulness ratings:
Users can assess other uses comments, give an upvote (+1) or downvote (-1)). A user is not allowed to rate his/her own comment.
![alt text](https://github.com/woshibiantai/DBProject/blob/master/ExtraResources/comment.gif "Comment and Vote")

## Dataset Browsing:
Users may search for Datasets, by asking conjunctive queries on the creator of database, and/or ratings, and/or title, and/or labels. The system will allow the user to specify that the results are to be sorted:
- by date created  
- by the number of followers   
- rating of the dataset itself   
- name of dataset  
![alt text](https://github.com/woshibiantai/DBProject/blob/master/ExtraResources/search.png "Search results")

## Dataset recommendation:
When a user follows a particular dataset, the system will suggest a list of other datasets that the user may be interested in. Recommendation is done by displaying other datasets in the same genre.

## Statistics:
Every month, the administrator wants
- the list of the m most followed Datasets (in terms of followers for the Dataset)
- the list of m most popular users (in terms of popular created datasets)
- the list of m most popular genres
![alt text](https://github.com/woshibiantai/DBProject/blob/master/ExtraResources/statistics.png "View statistics")
![alt text](https://github.com/woshibiantai/DBProject/blob/master/ExtraResources/genre.png "Top genres")
