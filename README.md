# DBProject
Development of database-based system on Django. Our database project aims to create an online dataset library that data scientists can use to find and share datasets to aid in their research projects.


# Team Members
Bryan Phua  
Jonathan Bei Qi Yang  1001619
Loh Wei Quan  
Ooi Kai Lue  
Ruth Wong Nam Ying  1001795

# Entity Relationship Diagram
![alt text](https://github.com/woshibiantai/DBProject/blob/master/misc/ERD.png "ERD Diagram")

# Database Schema

The DDL for our Database Schema can be found : [here](https://github.com/woshibiantai/DBProject/blob/master/misc/DDLs.txt)

# How to run the program
First navigate to the root of the project in your terminal, then run:  
`>> python manage.py runserver`


Open [localhost:8000/](localhost:800/) in your favorite browser to view the web application.
![alt text](https://github.com/woshibiantai/DBProject/blob/master/misc/home.png "Home page")

# Site Functionality

## Registration:
a new user has to provide necessary information; he/she can pick a login-name and a password. The login name will be checked for uniqueness. We made us of Django’s auth mode and session DB module for this. To create a staff account, go to /staffme/ to sign up. The special code is "purplepandas". You can login as per normal using this staff account to view the statistics.

## Following:
After registration, a user can choose to follow a dataset that he or she likes. (For our database, there’s no multiple copies of dataset, its either 1 or 0) But our datasets have a follow list that will increment when a new user follows it.
![alt text](https://github.com/woshibiantai/DBProject/blob/master/misc/follow.gif "Follow Dataset")

## User records:
Upon user demand, you will be navigated to a user's profile page, which displays:  
- his/her account information  
- his/her full history of followed datasets (dataset name, number of responders, date etc.)  
- his/his list of created datasets  
- his/her full history of comments  
![alt text](https://github.com/woshibiantai/DBProject/blob/master/misc/profile.gif "User Profile")

## New Dataset:
The creator of the dataset records the details of a new dataset, such as genre and description. For the purposes of this project, datasets will merely serve as placeholders.
![alt text](https://github.com/woshibiantai/DBProject/blob/master/misc/create.gif "Create new Dataset")

## Comment recordings:
Users can record their comments for a dataset. The date, and an optional short text will be recorded and displayed. No changes are allowed; only one comment per user per dataset is allowed. You can only delete comments that you make.

## Usefulness ratings:
Users can assess other uses comments, give an upvote (+1) or downvote (-1)). A user is not allowed to rate his/her own comment.
![alt text](https://github.com/woshibiantai/DBProject/blob/master/misc/comment.gif "Comment and Vote")

## Dataset Browsing:
Users may search for Datasets, by asking conjunctive queries on the creator of database, and/or ratings, and/or title, and/or labels. The system will allow the user to specify that the results are to be sorted:
- by date created  
- by the number of followers   
- rating of the dataset itself   
- name of dataset  
![alt text](https://github.com/woshibiantai/DBProject/blob/master/misc/search.png "Search results")

## Useful Comments:
For each dataset, the user can sort the comments according to it's usefulness according to the number of votes, or the recency. 

## Dataset recommendation:
When a user follows a particular dataset, the system will suggest a list of other datasets that the user may be interested in. Recommendation is done by displaying other datasets in the same genre.

## Statistics:
Every month, the administrator wants
- the list of the m most followed Datasets (in terms of followers for the Dataset)
- the list of m most popular users (in terms of popular created datasets)
- the list of m most popular genres
![alt text](https://github.com/woshibiantai/DBProject/blob/master/misc/statistics.png "View statistics")
![alt text](https://github.com/woshibiantai/DBProject/blob/master/misc/genre.png "Top genres")
