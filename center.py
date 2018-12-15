import config # make a config.py with an api_key from google places
import googleTypes # a list of all the searcheable google types
import math as m
import requests
import requests_cache
import urllib, json

requests_cache.install_cache('googleAPICache') # cache searches for tests to not waste api calls

class User:

    def __init__(self, name, lat, lon, pricePref, ratingPref, eventPref):
        self.name = name
        self.location = lat, lon
        self.organizer = False
        self.pricePref = pricePref
        self.ratingPref = ratingPref
        self.eventPref = eventPref

class Party:
    def __init__(self, users = []):
        self.users = users
        self.center = None
        self.places = []

    def __str__(self):
        output = ""
        if len(self.users) == 0:
            output = "The party is empty."
        elif len(self.users) == 1:
            output = "Only " + self.users[0].name + " is in the party."
        else:
            for i in range(len(self.users)-1):
                user = self.users[i]
                output += user.name + ", "
            output += "and " + self.users[-1].name + " are in the party."
        return output

    def findCenter(self):
        x = 0
        y = 0

        for user in self.users:
            x += user.location[0]/len(self.users)
            y += user.location[1]/len(self.users)

        self.center = (x, y)

    def addToParty(self, user):
        if not self.users:
            user.organizer = True
        self.users.append(user)

    def searchLocation(self, type="", radius=5000):
        APIKEY = config.api_key
        parameters = {"location": str(self.center[0])+","+str(self.center[1]),"radius":radius, "type":type,"key":APIKEY}
        response = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json", params=parameters)
        data = response.json()

        try:
            next_page_token = data["next_page_token"]
            print next_page_token
        except:
            pass

        if type == "restaurant":
            print "restaurant count", len(data["results"])
        # print type, "Used cache?", response.from_cache
        for place in data["results"]:
            name = place["name"] if "name" in place else None
            price = place["price_level"] if "price_level" in place else None
            rating = place["rating"] if "rating" in place else None
            location = place["geometry"]["location"]["lat"], place["geometry"]["location"]["lng"]
            address = place["vicinity"] if "vicinity" in place else None
            types = [str(type) for type in place["types"]] if "types" in place else None

            dict = {"name": name, # each place is its own dict for easy access to what you're looking for
                    "price": price,
                    "rating": rating,
                    "location": location,
                    "address": address,
                    "types": types}

            if dict not in self.places:
                self.places.append(dict)


    def filterList(self):
        filteredList = []
        for user in self.users:
            for place in self.places:
                if place not in filteredList:
                    if place["price"] <= user.pricePref and place["rating"] >= user.ratingPref:
                        if user.eventPref in place["types"]:
                            filteredList.append(place)
        self.filteredPlaces = filteredList


# tests dont work together for some reason the second keeps data from the first but we can fix that later!
print "PARTY 1\nPARTY 1\nPARTY 1\nPARTY 1\n"
# party = Party()
# hakeem = User(42.3736, -71.1097)
# louie = User(40.7128, -74.0060)
# amadou = User(41.9645, -73.4408)
# party.addToParty(hakeem)
# party.addToParty(louie)
# party.addToParty(amadou)
#
# print party.findCenter()

print "PARTY 2\nPARTY 2\nPARTY 2\nPARTY 2\n"

party1 = Party()
print party1
hakeem1 = User("Hakeem", 40.807835, -73.963957, 4, 0, "bar")
louie1 = User("Louie", 40.709013, -74.013692, 4, 0, "restaurant")
amadou1 = User("Amadou", 40.773585, -73.936027, 4, 0, "night_club")
party1.addToParty(hakeem1)
print party1
party1.addToParty(louie1)
print party1
party1.addToParty(amadou1)
print party1
party1.findCenter()

print party1.center

for type in googleTypes.googleTypes:
    party1.searchLocation(type, 500)

print len(party1.places)

def getDist(user, party, place):
    return (m.sqrt((user.location[0]-place["location"][0])**2+(user.location[1]-place["location"][1])**2) - m.sqrt((user.location[0]-party.center[0])**2+(user.location[1]-party.center[1])**2))/m.sqrt((user.location[0]-party.center[0])**2+(user.location[1]-party.center[1])**2)

def sadnessFunction(place, party):
    weights = {"type" : 1, "price" : 1, "rating" : 1, "dist" : 1}
    sadness = {}
    for user in party.users:
        sadness[user.name] = 0
        dist = getDist(user, party, place)
        if dist > 0:
            sadness[user.name] += dist * weights["dist"]

    print(sadness)


sadnessFunction(party1.places[1], party1)
