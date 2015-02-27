import kg2bee
import os
import sys
import units
import praw
import requests
#work out where we are
DIR = os.path.dirname(os.path.realpath(__file__))

conf = "{}/kg2bee.cfg".format( DIR )

#get a kg2bee
bee = kg2bee.kg2bee( conf )
#run it
stream = bee.getStream()
# How many posts kg2bee has performed
posts = 0 

for item in stream:
    try:
        if bee.shouldReply( item ) and bee.haventReplied( item ):
            bee.reply( item )

            if posts > 10:
                bee.removeNegativeComments()
                posts = 0
            
            posts += 1

    except units.exception.IncompatibleUnitsError:
        pass

    except praw.errors.RateLimitExceeded:
        print "Rate limited :("
        print " "

    except requests.exceptions.HTTPError as e:
        print e
        print " "

    except UnicodeEncodeError:
        pass
