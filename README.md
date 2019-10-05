# Item Catalog Project

This is the Second of three projects of Udacity Full Stack Nanodegree Course. It is particular to design a Data-Driven Web App.

## About

Developing a Database and web application that provides a list of items within a variety of categories and integrate third party user registration and authentication. Authenticated users should have the ability to post, edit, and delete their own items by flask framework, OAutho2 and supporting JSON type endpoints.


## Preparation

To start the project we have to prepare data and programs:

1- Virtual Machine: We will use a virtual machine to set up a Linux machine which will contain the database.
I used Virtual Box program

to download it : https://www.virtualbox.org/wiki/Downloads

2- Vagrant: This program is used with Virtual Machine to get me access the Linux  machine, adding needed files to it and running  python programs on it by creating a vagrant folder on my windows machine

to downlad it: https://www.vagrantup.com

3- Linux terminal: We need a linux terminal program to use vagrant commands (vagrant up / vagrant ssh) to log in Linux machine from my machine
I used GitBash terminal

to download it: https://gitforwindows.org

4- Downloading python to create the project file

link: https://www.python.org


## Database

The Database has two python files to be created:

1- db_setup.py file, in this file I created our tables [category, movie, user]

  1-1 category consists of two columns [name, id]

  1-2 movie consists of six columns [name, id, story, imdb rating, category_id, user_id]

  1-3 user consists of two columns [name, id]

* In this file I used SQLAlchemy ORM

2- movieitems.py, I used this file to fill the Database columns[category, movie] by some data and added (@property) function to support JSON data.

## SQLAlchemy

It is an ORM [Object Relational Mapping] program that converts SQL statements and columns to python objects to make it easier dealing with database and prevent mistakes in SQL statements.

to Download [Linux command :sudo pip install SQLAlchemy==1.3.8]

## Web application

Then I created web app that has the ability to connect to the Database by creating:

1- Web server (webserver.py) file that responsible for linking the user submit actions and Database.

2- Templates of html files that responsible for interface to the user and allow submit actions.


## Web server

This file consists of functions to execute every user action, and every function has its Route (URI) that when requested on browser this function is called and executed. the concept of any web app is CRUD which is abbreviation of user actions:
- Create to add data to Database
- Read to get data from Database
- Update to modify data on Database
- Delete to remove data from Database

So in this project my webserver  functions handlel:
- Add movie [Create]
- Show Movies [Read]
- Show categories [Read]
- Edit Movies [Update]
- Delete Movies [Delete]


* I useed flask framework to write the webserver

## flask framework

flask is a framework of python which combine between python functions and html templates

## Templates

Templates are html files that shows the data of Database on the browser and allow me doing CRUD actions


## Authentication

To sign in with google email to my app there are several steps

1- Create a project on Google API with my app name to gain an ID [Client_ID]

2- On main.html I added sign in button to initiate connection between webserver and google servers

3- On my server I added gconnect function that handles google sever response after logging in by user that receives [One time code] then exchanges it to [access_token]

4- Then it sends access_token in URI to google server to receive [user_info]

* client_secrets.json file is downloaded from Google API which contains data used for gconnect function to handle its mission
* To sign out I added gdisconnect function that handles logging out

## Authorization

To make Authorization for logged in users to I Modified Add movies function to allow only logged in users adding  

## Local permission

1- Modified gconnect function to create users in database

2- Modified Edit and delete functions to allow only creators of movies to do that


## Setting up project

Terminal commands to set up the project

1- Setting up Linux machine: $ vagrant up / $ vagrant ssh

2-  Creating database and adding movies to data base: $ python movieitems.py

3- Setting up the server: $ python webserver.py

## Guide

This project has guide example to help students creating their own apps

guide link: https://docs.google.com/document/d/e/2PACX-1vT7XPf0O3oLCACjKEaRVc_Z-nNoG6_ssRoo_Mai5Ce6qFK_v7PpR1lxmudIOqzKo2asKOc89WC-qpfG/pub?embedded=true

## Standards

This project has standards that reviewer will be using to evaluate your code.

Standers link:https://review.udacity.com/#!/rubrics/2008/view
