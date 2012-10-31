#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ebaysdk import finding, nodeText
from optparse import OptionParser
from email.mime.text import MIMEText
from termcolor import colored
import locale
import smtplib
import datetime
import time

# Display Item wrapper for Ebay item
class DisplayItem(object):

	def __init__():
		print "Init"

# Depends on termcolor module
# TODO:
# Format mail into HTML
# Include the ability to specify the category maybe
# List everything that's been added in the last n time_interval (hour)
# Format Display how much time is left on it
# Build a Display class and allow user to specify the column to sort on

def format_cur_code(cur_code):
	if cur_code == "USD":
		locale.setlocale(locale.LC_ALL, 'en_US.utf8')
		return locale.localeconv()['currency_symbol']
	elif cur_code == "GBP":
		locale.setlocale(locale.LC_ALL, 'en_GB.utf8')
		return locale.localeconv()['currency_symbol']
	else:
		return cur_code
	end

def format_amount(amount):
	return "{0:.2f}".format(float(amount))

def format_price(cur_code, amount):
	formatted_amount = format_amount(amount)
	return format_cur_code(cur_code) + formatted_amount

def get_item(part):
	el = item.getElementsByTagName(part)[0]
	return nodeText(el).encode("utf-8").strip()

def build_display(sep, part):
	el = item.getElementsByTagName(part)[0]
	return nodeText(el).encode("utf-8").strip() + sep

# Return an element for processing
def grabElement(elementname):
	if item.getElementsByTagName(elementname).length > 0:
		return item.getElementsByTagName(elementname)[0]
	else:
		return None

# Return an element for processing
def grabElementValue(elementname):
	el = item.getElementsByTagName(elementname)[0]
	return nodeText(el).encode("utf-8")

# Grab the value of an element
def grabValue(el):
	return nodeText(el).encode("utf-8")

# Display the formatted prices
def display_formatted_prices(item, price_el, ship_price_el):
	price = grabElement(price_el)
	cur_id = price.getAttribute('currencyId')

	display_text = ""	
	# Handle the shipping price (if available - it might be courier)
	shipping_price = grabElement(ship_price_el)
	if shipping_price is not None and price is not None:
		total_price = str(format_amount(float(grabValue(price)) + float(grabValue(shipping_price))) ).encode("utf-8")
		formatted_price = format_price(cur_id, grabValue(price))
		formatted_shipping_price = format_price(cur_id, grabValue(shipping_price))
		display_text += colored(format_cur_code(cur_id) + format_amount(total_price), 'red')
		display_text += " (" + formatted_price + " + " + formatted_shipping_price + ")"
	elif price is not None:
		total_price = str(format_amount(float(grabValue(price))))
		formatted_price = format_price(cur_id, grabValue(price))
		display_text += colored(format_cur_code(cur_id) + format_amount(total_price), 'red')
	else:
		display_text = "No price/shipping price"

	return display_text

# Send an email out
def send_email(listings, from_email, to_email):

	send_text = ""
	for disp in found_items:
  		send_text += disp + "\n\n"

	msg = MIMEText(send_text)

	# me == the sender's email address
	# you == the recipient's email address
	msg['Subject'] = 'Ebay SDK Mailout %s ' % str(datetime.date.today())

	msg['From'] = from_email
	msg['To'] = to_email

	# Send the message via our own SMTP server, but don't include the
	# envelope header.
	s = smtplib.SMTP('localhost')
	s.sendmail(from_email, [to_email], msg.as_string())
	s.quit()
	print "Successfully sent email to %s " % to_email

def display_instant_purchase(item):

	item_text = ""
	list_type = str(grabElementValue("listingType").strip())

	if list_type == "AuctionWithBIN" or list_type == "FixedPrice" or list_type == "StoreInventory":

		# TODO: Use operator module to sort the list of items
		# d = DisplayItem()
		# d.setTitle(get_item("title"))
		# d.setItemId(get_item("itemId"))
		# d.setListType(colored("Instant Purchase", 'blue'))
		# d.setPriceText(display_formatted_prices(item, "buyItNowPrice", "shippingServiceCost"))
		# d.setEndTime(grabElementValue("endTime"))
		# found_items.append(d)

		item_text += build_display(",", "title")
		item_text += build_display(",", "itemId")
		item_text += colored("Instant Purchase", 'blue') + ", " 

		if list_type == "FixedPrice" or list_type == "StoreInventory":
			item_text += display_formatted_prices(item, "currentPrice", "shippingServiceCost")
		else:
			item_text += display_formatted_prices(item, "buyItNowPrice", "shippingServiceCost")

		item_text += ", " + grabElementValue("endTime")

		return item_text

def display_item(item):

	item_text = ""
	list_type = str(grabElementValue("listingType").strip())
	item_text += build_display(",", "title")
	item_text += build_display(",", "itemId")

	# List all item list_types
	if list_type == "AuctionWithBIN":
		item_text += colored("Instant Purchase", 'blue') + ", " 
		item_text += display_formatted_prices(item, "buyItNowPrice", "shippingServiceCost")
	elif list_type == "FixedPrice" or list_type == "StoreInventory":
		item_text += colored("Instant Purchase", 'blue') + ", " 
		item_text += display_formatted_prices(item, "currentPrice", "shippingServiceCost")
	else:
		item_text += colored(list_type, 'green') + ", " 
		item_text += display_formatted_prices(item, "currentPrice", "shippingServiceCost")

	# TODO: Format time
	item_text += ", " + grabElementValue("endTime")
	return item_text

# Display items in GB only 
country = "GB"
parser = OptionParser()
parser.add_option("-k", "--keywords", dest="keywords", help="keywords to search for")
parser.add_option("-d", "--displayonly", dest="displayonly", default=False, action="store_true", help="just display results, don't send an email")
parser.add_option("-b", "--buyitnowonly", dest="buyitnowonly", default=False, action="store_true", help="Whether to display just buy it now items")
parser.add_option("-s", "--sortorder", dest="sortorder", type="choice", choices=["price", "end", "start"], default="price", help="Whether to display just buy it now items")

(options, args) = parser.parse_args()
keywords = options.keywords

if keywords is None:
	exit("Please specify some keywords to search for")

sort_order_type = options.sortorder
if options.sortorder == "price":
	sort_order_type = "PricePlusShippingLowest"
elif options.sortorder == "end":
	sort_order_type = "EndTimeSoonest"
elif options.sortorder == "start":
	sort_order_type = "StartTimeSoonest"

print "\n" + "#" * 100
print "Please wait, searching Ebay for %s" % keywords + " with options " + sort_order_type

# http://developer.ebay.com/devzone/finding/callref/findItemsAdvanced.html
f = finding()
f.execute('findItemsAdvanced', {'keywords': keywords, 'sortOrder': sort_order_type} )

response_dom 	= f.response_dom()
response_dict 	= f.response_dict()
response  		= f.response_obj()


# process the response via DOM
items = response_dom.getElementsByTagName('item')

found_items = []
if len(items) > 0:
	print "#" * 100
	print "Item search URL " + response.itemSearchURL
	for item in items:

		display_text = ""

		# We don't need to pass the item in explicitly to the function, it is passed anyway
  		if grabElementValue("country") == country:

			if options.buyitnowonly:
				text = display_instant_purchase(item)
				if text:
					found_items.append(text)
			else:
  				text = display_item(item)
  				if text:
  					found_items.append(text)	
  			

	#
	# Display all items FIXME
	#
  	#found_items.sort()
  
	if not options.displayonly:
  		send_email(found_items, "ebaysdkmailer", "jonathan.holloway@gmail.com")
	else:
		for item in found_items:
			print item
else:
	print "No items found matching %s" % keywords
