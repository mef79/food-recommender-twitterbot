import urllib2, json, random, time
from twython import Twython
from googleplaces import GooglePlaces, types, lang
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# keep track of which messages to use
hungry_count = 7
original_count = 1
hangry_count = 3

# prevent tweeting at the same user
last_tweet_id = 0
hangry_ids = []

# store options for tweet contents
hungry_contents = []
hangry_contents = []
original_contents = []

# top 100 cities
cities = []

# create a tywthon object
twitter = Twython('l9DRASlNvCOaHkP8fqHrzO1LG', 							#API_KEY
				  'P4Q33KyhSjTcymrdCcOkUQqyqEI2Jsayd8mL4J5Il8ulQojhsC', #API_SECRET
				  '2510683141-Qd8qfoterOYXeyaWrZKkxs6a1foqS1xwcdjbK2k', #ACCESS_TOKEN
				  'hesSYgqcnvqaALVtuDD6p5BDNDtYaDVWehF60rVyilkeG' 		#ACCESS_TOKEN_SECRET
				  )

# fill in the contents from text files
def populate_contents(contents, filename):
	f = open("".join([filename, ".txt"]))
	lines = f.readlines()
	for line in lines:
		contents.append((line.rstrip('\n')).split(", "))

# fill in the top 100 cities from city-data.com
def populate_cities():
	soup = BeautifulSoup(urllib2.urlopen('http://www.city-data.com/top1.html').read())
	for link in soup.find_all("a"):
		if link.string  != None and not ('U.S.' in link.string or '1' in link.string or 'lists' in link.string):
			cities.append(link.string)

# get a random restaurant near the inputted city
def get_restaurant(place_name, include_city):
	restaurant_result = {}
	google_places = GooglePlaces('AIzaSyAJyCCeJNiaky6gVuZ2G1-0-hK0MaJJr3o')
	query_result = google_places.nearby_search(location=place_name, radius=1000, types=[types.TYPE_FOOD])
	restaurant = random.choice(query_result.places)
	restaurant.get_details()
	restaurant_result['name'] = restaurant.name
	if include_city:
		restaurant_result['addr'] = restaurant.formatted_address.replace(", United States", "")
	else:
		restaurant_result['addr'] = restaurant.formatted_address[:restaurant.formatted_address.index(",")]
	return restaurant_result

# send a reply to someone tweeting about being hungry or hangry (specified by input)
# return True if tweet was successful
def send_reply_tweet(tweet_type, in_reply_to, contents, count):
	try:
		restaurant = get_restaurant(in_reply_to['place']['full_name'])
		tweet_contents = contents[count % len(contents)]
		tweet_text = "".join([tweet_contents[0], restaurant['name'], " at ", restaurant['addr'], tweet_contents[1]])
		twitter.update_status(status="".join(['@', in_reply_to['user']['screen_name'], " ", tweet_text]), in_reply_to_status_id=in_reply_to['id'])
		log_message("".join(['me: (reply ', str(hungry_count), ')\t@', in_reply_to['user']['screen_name'], " ", tweet_text, "\n"]))
		return True
	except: # because wi-fi
		log_message("".join([tweet_type, " tweet failed.\n"]))

# create an original tweet
# return True if tweet was successful
def tweet_original(city):
	try:
		restaurant = get_restaurant(city)
		tweet_contents = original_contents[original_count % len(original_contents)]
		tweet_text = "".join([tweet_contents[0], city, tweet_contents[1], restaurant['name'], " at ", restaurant['addr'], tweet_contents[2]])

		twitter.update_status(status=tweet_text)
		log_message("".join(['me: (original ', str(original_count), ')\t', tweet_text, "\n"]))
		return True
	except:
		log_message("Original tweet failed\n")
		return False

# find and return a tweet about "I'm hungry"
def get_hungry_tweet():
	try:
		tweet = search_tweets("\"I'm hungry\"")
		return tweet
	except:
		log_message("Getting hungry tweet failed\n")

# find and return a tweet about being hangry
def get_hangry_tweet(hangry_ids):
	try:
		tweet = search_tweets('#hangry')
		if tweet != None and tweet['id'] not in hangry_ids:
			return tweet
		print "no results for #hangry"
		tweet = search_tweets("i'm hangry")
		if tweet != None and tweet['id'] not in hangry_ids:
			return tweet
		print "no results for i'm hangry"
		tweet = search_tweets("getting hangry")
		if tweet != None and tweet['id'] not in hangry_ids:
			return tweet
		print "no results for getting hangry"
	except:
		log_message("Getting hangry tweet failed\n")

# return the first tweet for the query
def search_tweets(query):
	search_results = twitter.search(q=query, count=100)
	tweets = search_results['statuses']
	for tweet in tweets:
		if tweet['place'] != None and tweet['place']['place_type'] == 'city' and tweet['place']['country'] == 'United States':
				return tweet

# wait and print some messages so I know it's still going
def wait():
	for i in range (0, 6):
		log_message(" ".join(["waiting ", str(i)]))
		time.sleep(ranom.randint(400,600))

# add text to the log
def log_message(message):
	log = open('log.txt', 'a')
	log.write(message)
	log.close()

# fill in the cities
populate_cities()

while True:

	# fill in the possible tweet contents
	# this way, the contents can be changed while the bot is running
	populate_contents(hungry_contents, 'hungry_contents')
	populate_contents(hangry_contents, 'hangry_contents')
	populate_contents(original_contents, 'original_contents')

	# loop variables, needed them so that the bot doesn't skip a type of tweet when there are wi-fi issues
	made_hungry_tweet = False
	made_hangry_tweet = False
	made_original_tweet = False

	while not made_original_tweet:
		if tweet_original(random.choice(cities)):
			original_count += 1
			made_original_tweet = True
			wait()

	while not made_hungry_tweet:
		tweet = get_hungry_tweet()
		if tweet != None and tweet['id'] != last_tweet_id:
			last_tweet_id = tweet['id']
			if send_reply_tweet('hungry', tweet, hungry_contents, hungry_count):
				made_hungry_tweet = True
				hungry_count += 1
				wait()

	attempts = 0
	while not made_hangry_tweet and attempts < 5:
		tweet = get_hangry_tweet(hangry_ids)
		if tweet != None and tweet['id'] not in hangry_ids:
			hangry_ids.append(tweet['id'])
			if send_reply_tweet('hangry', tweet, hangry_contents, hangry_count):
				made_hangry_tweet = True
				hangry_count += 1
				wait()
		attempts += 1
