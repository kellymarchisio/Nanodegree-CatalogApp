from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item

engine = create_engine('postgresql+psychopg2://catalog:catalog@52.88.17.188/catalog')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# categories: soccer, basketball, baseball, football, frisbee, snowboarding
# 	rock climbing, foosball, skating, hockey

categories = {
	'category1' : Category(name="Soccer"),
	'category2' : Category(name="Basketball"),
	'category3' : Category(name="Baseball"),
	'category4' : Category(name="Football"),
	'category5' : Category(name="Frisbee"),
	'category6' : Category(name="Snowboarding"),
	'category7' : Category(name="Rock Climbing"),
	'category8' : Category(name="Foosball"),
	'category9' : Category(name="Skating"),
	'category10' : Category(name="Hockey")
}

for category in categories.values():
	session.add(category)

session.commit()


# already added all categories, now add items to categories

soccer_items = [Item(name="Cleats", parent_id = 1), Item(name="Soccer Ball", parent_id = 1),
Item(name="Shin Guards", parent_id = 1), Item(name="Goalkeeper Gloves", parent_id = 1), 
Item(name="Shorts", parent_id = 1), Item(name="Jersey", parent_id = 1)]

basketball_items = [Item(name="Basketball", parent_id = 2), Item(name="Sneakers", parent_id = 2),
Item(name="Basketball Net", parent_id = 2)]

baseball_items = [Item(name="Bat", parent_id = 3), Item(name="Baseball", parent_id = 3),
Item(name="Batting Gloves", parent_id = 3), Item(name="Pitching Rubber", parent_id = 3), 
Item(name="Helmet", parent_id = 3), Item(name="Glove", parent_id = 3),
Item(name="Cap", parent_id = 3), Item(name="Cleats", parent_id = 3)]

football_items = [Item(name="Whistle", parent_id = 4), Item(name="Shoulder Pads", parent_id = 4),
Item(name="Football", parent_id = 4), Item(name="Mouthguard", parent_id = 4), 
Item(name="Jersey", parent_id = 4)]

frisbee_items = [Item(name="Frisbee", parent_id = 5), Item(name="Shorts", parent_id = 5),
Item(name="T-Shirt", parent_id = 5)]

snowboarding_items = [Item(name="Snow Pants", parent_id = 6), Item(name="Snowboard", parent_id = 6),
Item(name="Gloves", parent_id = 6), Item(name="Hat", parent_id = 6), Item(name="Faceguard", parent_id = 6), 
Item(name="Boots", parent_id = 6), Item(name="Goggles", parent_id = 6)]

rockclimbing_items = [Item(name="Clamp", parent_id = 7), Item(name="Rope", parent_id = 7),
Item(name="Water Bottle", parent_id = 7), Item(name="Climbing Gear", parent_id = 7)]

foosball_items = [Item(name="Foosball Table", parent_id = 8), Item(name="Foosball", parent_id = 8)]

skating_items = [Item(name="Skates", parent_id = 9), Item(name="Shoe Laces", parent_id = 9),
Item(name="Leotard", parent_id = 9), Item(name="Ribbon", parent_id = 9)]

hockey_items = [Item(name="Skates", parent_id = 10), Item(name="Hockey Stick", parent_id = 10),
Item(name="Hockey Gloves", parent_id = 10), Item(name="Shoulder Pads", parent_id = 10), 
Item(name="Mouthguard", parent_id = 10), Item(name="Helmet", parent_id = 10)]

all_items = [soccer_items, baseball_items, basketball_items, football_items, foosball_items,
frisbee_items, snowboarding_items, rockclimbing_items, skating_items, hockey_items]

for item_category in all_items:
	for item in item_category:
		session.add(item)

session.commit()

print "added items!"