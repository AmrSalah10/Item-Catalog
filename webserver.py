from flask import Flask, request, render_template, redirect
from flask import url_for, flash, make_response, jsonify
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Category, Base, Movie, User
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

from functools import wraps


# Connect to Database and create database session
engine = create_engine('sqlite:///movies.db')
Base.metadata.bind = engine
app = Flask(__name__, static_url_path='')

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Movies"

# Return Homepage with (sign in) button
# and creating (State) code for anti forgery
@app.route('/')
@app.route('/main')
def main():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('main.html', account_id=login_session.get
                           ('account_id'), STATE=state)

# Return (gconnect) page to exchange Authorization code
# with access_token after logging in
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        print(result)
        return response

    # Verify that the access token is used for the intended user.
    account_id = credentials.id_token['sub']
    if result['user_id'] != account_id:
        response = make_response(json.dumps("Token's user ID"
                                 "doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the user is logged in.
    stored_access_token = login_session.get('access_token')
    stored_account_id = login_session.get('account_id')

    if stored_access_token is not None and account_id == stored_account_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session incase user is not logged in.
    # Then they are be used to Verify that the user is logged in.
    login_session['access_token'] = credentials.access_token
    login_session['account_id'] = account_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    print('result is ')
    print result

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;"'
    ' "-webkit-border-radius: 150px;-moz-border-radius: 150px;"> "'
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")

    # checking user existence and create new one
    try:
        user = session.query(User).filter_by(email=login_session["email"]
                                             ).one()
    except NoResultFound:
        newUser = User(name=login_session["username"],
                       email=login_session["email"],
                       picture=login_session["picture"])
        session.add(newUser)
        session.commit()

    return output

# Decorator function to check logging in status
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if login_session.get('account_id') is None:
            flash ('You have to Sign in First')
            return redirect(url_for('main', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# Returning gdisconnect when logging out
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'apllication/json'
        return render_template('gdisconnect.html', response=response)
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com'
    '/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['account_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return render_template('gdisconnect.html', response=response)
    else:
        response = make_response(json.dumps('Failed to revoke token for'
                                            'given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return render_template('gdisconnect.html', response=response)

# Show categories page
@app.route('/main/category')
def showCategories():
    categories = session.query(Category).all()
    return render_template('categories.html',
                           categories=categories,
                           account_id=login_session.get('account_id'))

# Show showmovies page
@app.route('/main/category/<int:category_id>')
@app.route('/main/category/<int:category_id>/movies')
def showmovies(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    movies = session.query(Movie).filter_by(category_id=category.id)
    return render_template('showmovies.html',
                           movies=movies,
                           category=category,
                           account_id=login_session.get('account_id'))

# Return Movies with Info in json content
@app.route('/main/category/<int:category_id>/movies/json')
def showmoviesjson(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    movies = session.query(Movie).filter_by(category_id=category.id)
    return jsonify(Movie=[i.serialize for i in movies])

# Show movieInfo page
@app.route('/main/category/<int:category_id>/movies/<int:movie_id>/info')
def movieInfo(category_id, movie_id):
    category = session.query(Category).filter_by(id=category_id).one()
    movie = session.query(Movie).filter_by(id=movie_id).one()

    if login_session.get('email'):
        user = session.query(User).filter_by(email=login_session['email']
                                             ).one()
        return render_template('movieInfo.html',
                               movie=movie,
                               category=category, user_id=user.id)
    else:
        return render_template('movieInfo.html',
                               movie=movie, category=category)

# Adding Movie to db only by logged in User
@app.route('/main/category/<int:category_id>/movies/add',
           methods=['GET', 'POST'])
@login_required
def addmovie(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        user = session.query(User).filter_by(email=login_session['email']
                                             ).one()
        newmovie = Movie(name=request.form['name'],
                         story=request.form['story'],
                         IMDB_Rating=request.form['IMDB_Rating'],
                         category_id=category_id, user_id=user.id)
        session.add(newmovie)
        session.commit()
        return redirect(url_for('showmovies', category_id=category_id))
    else:
        return render_template('addmovie.html', category=category)

# Edit Movie data only by creator
@app.route('/main/category/<int:category_id>/movies/<int:movie_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editmovie(category_id, movie_id):
    category = session.query(Category).filter_by(id=category_id).one()
    movie = session.query(Movie).filter_by(id=movie_id).one()

    if request.method == 'POST':
        user = session.query(User).filter_by(email=login_session['email']
                                             ).one()
        if movie.user_id == user.id:
            movie.name = request.form['name']
            movie.story = request.form['story']
            movie.IMDB_Rating = request.form['IMDB_Rating']
            session.add(movie)
            session.commit()

            return redirect(url_for('movieInfo', category_id=category_id,
                                    movie_id=movie_id))
    else:
        return render_template('editmovie.html', movie=movie,
                               category=category)

# Delete Movie data only by creator
@app.route('/main/category/<int:category_id>/movies/<int:movie_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deletemovie(category_id, movie_id):
    category = session.query(
                             Category).filter_by(id=category_id).one()
    movie = session.query(Movie).filter_by(id=movie_id).one()

    if request.method == 'POST':
        user = session.query(User).filter_by(email=login_session['email']
                                             ).one()
        if movie.user_id == user.id:
            session.delete(movie)
            session.commit()
            flash('%s is Deleted successfully!' % movie.name)
            return redirect(url_for('showmovies', category_id=category_id))
    else:
        return render_template('deletemovie.html',
                               movie=movie, category=category)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000, threaded=False)
