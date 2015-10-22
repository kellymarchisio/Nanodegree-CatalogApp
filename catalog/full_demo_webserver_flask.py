from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
import re
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('postgresql+psychopg2://catalog:catalog@52.88.17.188/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/restaurants/JSON/')
def restaurantsJSON():
	restaurants = session.query(Restaurant).all()
	return jsonify(MenuItems=[i.serialize for i in restaurants])

@app.route('/restaurants/<int:restaurant_id>/menu/JSON/')
def restaurantMenuJSON(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
	return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
def restaurantMenuItemJSON(restaurant_id, menu_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	item = session.query(MenuItem).filter_by(id=menu_id).one()
	return jsonify(MenuItems=item.serialize)

@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
	restaurants = session.query(Restaurant).all()
	return render_template('allrestaurants.html', restaurants=restaurants)

@app.route('/restaurant/new/', methods = ['GET','POST'])
def newRestaurant():
	if request.method == 'POST':
		newRestaurant = Restaurant()
		newRestaurant.name = request.form['addRestaurant']
		session.add(newRestaurant)
		session.commit()
		flash('New restaurant created!')
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('newrestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET','POST'])
def editRestaurant(restaurant_id, methods=['GET','POST']):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		restaurant.name = request.form['editRestaurant']
		session.add(restaurant)
		session.commit()
		flash('Restaurant name successfully edited!')
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('editrestaurant.html', restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET','POST'])
def deleteRestaurant(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		session.delete(restaurant)
		session.commit()
		flash('Restaurant successfully deleted!')
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('deleterestaurant.html', restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id).all()
	print len(items)
	return render_template('menu.html', restaurant=restaurant, items=items)

@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods = ['GET','POST'])
def newMenuItem(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		price = re.search(r'\$\d+\.\d\d', request.form['newItemPrice'])
		if (len(request.form['newItemName']) > 0 and len(request.form['newItemPrice']) > 0 and
			price):
			newItem = MenuItem() 
			newItem.name = request.form['newItemName']
			newItem.description = request.form['newItemDescription']
			newItem.price = request.form['newItemPrice']
			newItem.course = request.form['newItemCourse']
			newItem.restaurant_id = restaurant.id
			session.add(newItem)
			session.commit()
			flash('New menu item created!')
			return redirect(url_for('showMenu', restaurant_id=restaurant_id))
		else:
			flash('Make sure you add a valid new menu item name and valid price when creating a new item')
			return redirect(url_for('showMenu', restaurant_id=restaurant_id))
	else:
		return render_template('addmenuitem.html', restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods = ['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
	itemToEdit = session.query(MenuItem).filter_by(id=menu_id).one()
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		if len(request.form['editItemName']) > 0:
			itemToEdit.name = request.form['editItemName']
			session.add(itemToEdit)
			session.commit()
			flash("Menu item successfully edited!")
			return redirect(url_for('showMenu', restaurant_id=restaurant_id))
		else:
			flash("your entered an invalid menu item name.")
			return redirect(url_for('showMenu', restaurant_id=restaurant_id))
	else:
		return render_template('editmenuitem.html', restaurant=restaurant, item=itemToEdit)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
	itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		session.delete(itemToDelete)
		session.commit()
		flash("Menu item successfully deleted!")
		return redirect(url_for('showMenu', restaurant_id = restaurant_id))
	else:
		return render_template('deletemenuitem.html', restaurant=restaurant, item=itemToDelete)
	return "page to delete a new menu item. Task 3 complete!"

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)




