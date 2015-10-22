from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask import flash, make_response
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import util
from database_setup import Category, Item, Base, User

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

CLIENT_ID = json.loads(open(
  'client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('postgresql+psychopg2://catalog:catalog@52.88.17.188/catalog')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def createUser(login_session):
  newUser = User(
    name = login_session['username'], email = login_session['email'], 
    picture = login_session['picture'])
  session.add(newUser)
  session.commit()
  user = session.query(User).filter_by(email = login_session['email']).one()
  return user.id

def getUserId(email):
	try:
		user = session.query(User).filter_by(email = email).one()
		return user.id
	except:
		return None

def getUserInfo(user_id):
	user = session.query(User).filter_by(id = user_id).one()
	return user

@app.route('/category/JSON/')
def categoriesJSON():
	categories = session.query(Category).all()
	return jsonify(Categories=[i.serialize for i in categories])

@app.route('/category/<string:category_name>/items/JSON/')
def categoryItemsJSON(category_name):
	category = session.query(Category).filter_by(name=category_name).one()
	items = session.query(Item).filter_by(parent_id=category.id).all()
	return jsonify(Items=[i.serialize for i in items])

@app.route('/', methods = ['GET','POST'])
def showHomepage():
	categories = session.query(Category).all()
	if 'username' not in login_session:
		print "not logged in yet"
		state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
		login_session['state'] = state
	else:
		print "logged in with username: " + login_session['username']
	return render_template('homepage.html', categories=categories, STATE=login_session['state'])

@app.route('/gconnect', methods=['POST'])
def gconnect():
  print 'spot 1'
  print 'request.args.get("state") = ' + request.args.get('state')
  print 'login_session["state"] = ' + login_session['state']
  if request.args.get('state') != login_session['state']:
    response = make_response(json.dumps('Invalid state parameter'), 401)
    response.headers['Content-Type'] = 'application/json'
    print 'problem A'
    return response
  code = request.data
  try:
    # Upgrade the authorization code into a credentials object
    oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
    oauth_flow.redirect_uri = 'postmessage'
    credentials = oauth_flow.step2_exchange(code)
  except FlowExchangeError:
    response = make_Response(json.dumps(
      'Failed to upgrade the authorization code.'), 401)
    response.headers['Content-Type'] = 'application/json'
    print 'problem B'
    return response
  # Check that the access token is valid
  access_token = credentials.access_token
  url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % 
    access_token)
  h = httplib2.Http()
  result = json.loads(h.request(url, 'GET')[1])
  # If there was an error in access token info, abort.
  if result.get('error') is not None:
    response = make_response(json.dumps(result.get('error')), 50)
    response.headers['Content-Type'] = 'application/json'
    return response 
  if result['issued_to'] != CLIENT_ID:
    response = make_response(json.dumps(
      'Token\'s client ID does not match app\'s.'), 401)
    print 'Token\'s client ID does not match app\'s.'
    print 'problem C'
    response.headers['Content-Type'] = 'application/json'
  gplus_id = credentials.id_token['sub']
  if result['user_id'] != gplus_id:
    response = make_response(
      json.dumps("Token's user ID doesn't match given user ID."), 401)
    print 'problem D'
    response.headers['Content-Type'] = 'application/json'
    return response
  # Check if user is already logged in to system
  stored_credentials = login_session.get('credentials')
  stored_gplus_id = login_session.get('gplus_id')
  if stored_credentials is not None and gplus_id == stored_gplus_id:
    response = make_response(json.dumps(
      'Current user is already connected.'), 200)
    response.headers['Content-Type'] = 'application/json'

  # Store the access token in the session for later use.
  login_session['credentials'] = credentials
  login_session['gplus_id'] = gplus_id

  # Get user info
  userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo?'
  params = {'access_token': credentials.access_token, 'alt': 'json'}
  answer = requests.get(userinfo_url, params=params)
  data = json.loads(answer.text)

  login_session['username'] = data['name']
  login_session['picture'] = data['picture']
  login_session['email'] = data['email']

  user_id = getUserId(login_session['email'])

  if not user_id:
    user_id = createUser(login_session)
  login_session['user_id'] = user_id

  output = ''
  output += '<h4>Welcome, '
  output += login_session['username']
  output += '! ' 
  output += '<img src="' 
  output += login_session['picture']
  output += (' " style = "width: 30px; height: 30px; border-radius: 15px;' 
  '-webkit-border-radius: 15px; -moz-border-radius: 15px;"></h4>') 
  return output

@app.route('/gdisconnect')
def gdisconnect():
  # Only disconnect a connected user.
  if 'username' not in login_session:
    return redirect('/login')
  credentials = login_session.get('credentials')
  if credentials is None:
    response = make_response(json.dumps('Current user is not connected.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  access_token = credentials.access_token
  print access_token
  url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
  h = httplib2.Http()
  result = h.request(url, 'GET')[0]
  print result

  if result['status'] == '200':
    del login_session['credentials']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']

    response = make_response(json.dumps('Successfully disconnected.'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response

  else:
    # For whatever reason, the given token was invalid.
    response = make_response(json.dumps(
      'Failed to revoke token for given user.'), 400)
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/category/<string:category_name>/')
def viewCategory(category_name):
	category = session.query(Category).filter_by(name = category_name).one()
	items = session.query(Item).filter_by(parent_id = category.id).all()
	if 'username' in login_session:
		return render_template('category.html', category = category, items = items, STATE=login_session['state'])
	else:
		return render_template('category_public.html', category = category, items = items, STATE=login_session['state'])

@app.route('/category/<string:category_name>/add/', methods = ['GET','POST'])
def addItem(category_name):
	if 'username' not in login_session:
		return redirect('/')
	parentCategory = session.query(Category).filter_by(name = category_name).one()
  	if request.method == 'POST':
	  	newItem = Item(name = request.form['name'], description = request.form['description'],
	  		parent_id = parentCategory.id)
	  	session.add(newItem)
	  	session.commit()
	  	return redirect(url_for('viewCategory', category_name = parentCategory.name))
  	else:
  		return render_template('addItem.html', category = parentCategory) 

@app.route('/category/<string:category_name>/<string:item_name>')
def viewItem(category_name, item_name):
	category = session.query(Category).filter_by(name = category_name).one()
	item = session.query(Item).filter_by(parent_id = category.id).filter_by(
		name = item_name).one()
	if 'username' in login_session:
		return render_template('item.html', item = item, category = category, STATE=login_session['state'])
	else:
		return render_template('item_public.html', item = item, category = category, STATE=login_session['state'])

@app.route('/category/<string:category_name>/<string:item_name>/delete/', methods = ['GET','POST'])
def deleteItem(category_name, item_name):
	if 'username' not in login_session:
		return redirect('/')
	parentCategory = session.query(Category).filter_by(name = category_name).one()
	itemToDelete = session.query(Item).filter_by(parent_id = parentCategory.id).filter_by(name = item_name).one()
	if request.method == 'POST':
		session.delete(itemToDelete)
		session.commit()
		return redirect(url_for('viewCategory', category_name = parentCategory.name))
	else:
		return render_template('deleteItem.html', item = itemToDelete, category = parentCategory, STATE=login_session['state'])

@app.route('/category/<string:category_name>/<string:item_name>/edit/', methods = ['GET','POST'])
def editItem(category_name, item_name):
	if 'username' not in login_session:
		return redirect('/')
	parentCategory = session.query(Category).filter_by(name = category_name).one()
	itemToEdit = session.query(Item).filter_by(parent_id = parentCategory.id).filter_by(name = item_name).one()
	if request.method == 'POST':
		if request.form['description']:
			itemToEdit.description = request.form['description']
		session.add(itemToEdit)
		session.commit()
		return redirect(url_for('viewCategory', category_name = parentCategory.name))
	else:
		return render_template('editItem.html', item = itemToEdit, category = parentCategory, STATE=login_session['state'])

def createUser(login_session):
  newUser = User(
    name = login_session['username'], email = login_session['email'], 
    picture = login_session['picture'])
  session.add(newUser)
  session.commit()
  user = session.query(User).filter_by(email = login_session['email']).one()
  return user.id


def getUserInfo(user_id):
  user = session.query(User).filter_by(id = user_id).one()
  return user


def getUserID(email):
  try:
    user = session.query(User).filter_by(email = email).one()
    return user.id
  except:
    return None

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)




