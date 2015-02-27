"""
kg2bee reddit bot

Converts all measurements to kg and bees

@category   silly
@version    $ID: 1.1.1, 2015-02-19 17:00:00 CST $;
@author     KMR, Jason
@licence    http://www.wtfpl.net
"""
import praw
import re
import kg2db
import yaml

from pprint import pprint

from units import unit, scaled_unit
from units.predefined import define_units

__version__ = "1.1.1"

class kg2bee:
    #setup the predefined units
    define_units()

    #giant hulking regex to find volumes of measurements
    regex  = re.compile( r'(^|\s)((?:(?:[0-9]*,)*(?:[0-9]+)(?:\.)?(?:[0-9]+)?)|(?:(?:\.)?(?:[0-9]+)))\s*([a-zA-Z]{1,})', re.IGNORECASE )
    
    #all the other attributes
    bee    = None
    kilo   = None
    bees   = None
    config = None

    def __init__( self, conf ):
        self.config = yaml.safe_load( open( conf ) )
        
        if self.config['debug']:
            print "Hello, welcome to kg2bee, Debug is ON\r\n"

        # add bees, and the conversion rate
        self.bee = scaled_unit('bees', 'mg', self.config['bee'] )

        #setup handlers
        self.bees = unit('bees')
        self.kilo = unit('kg')

        #other class things
        self.rAPI = praw.Reddit( user_agent=( self.config['user'] ) )

        self.rAPI.login(username=self.config['name'], password=self.config['pasw'])
    
    def getStream( self ):
        #grab a comment stream
        return praw.helpers.comment_stream( self.rAPI, self.config['subs'], self.config['maxi'])

    def getComments( self ):
        user = self.rAPI.get_redditor( self.config['name'] )
        return user.get_comments(sort='new', time='day', limit=None)

    def removeNegativeComments( self ):
        if self.config['debug']:
            print "Removing negative comments"

        for comment in self.getComments():
            if comment.ups < -1:
     
                if self.config['debug']:
                    print "Deleting comment {} with score {}".format( comment.permalink, comment.ups )

                comment.delete()

    def shouldReply( self, comment ):
        #make sure it's not a deleted comment or one by kg2bee, and it hasn't been replied to yet
        if comment.author.name and comment.author.name is not "kg2bee":
            if comment.subreddit.display_name not in self.config['banned_subreddits']:
                #run the regex on the comment to find something to convert
                measures = self.regex.findall( comment.body.lower() )
                #only proceed if there is a single volume fetched
                if len( measures ) == 1:
                    count = measures[0][1].replace(",","")
                    uType = measures[0][2].strip()
                    #split it into it's correct units and volume
                    s = float( count )
                    u = uType
                    m = unit(u)
                    #make sure there is enough weight so it will actually display
                    k = self.regex.findall( "{}".format( self.kilo( m( s ) ) ) )
                    #check if it's something that should be replied to
                    if ( s > 0 ) and ( m is not "bees" ) and ( float( k[0][1] ) > 0 ) :
                        if self.config['debug']:
                            print "found something to process: {}, value: {}".format( comment.permalink, k )
                        return True
            else:
                if self.config['debug']:
                    print "Not replying to comment found in {}".format(comment.subreddit)

        return False

    def haventReplied( self, comment ):
        if kg2db.get_comment( comment.id ) is None:
            return True
        return False
    
    def reply( self, comment ):
        #get the values to convert
        measures = self.regex.findall( comment.body.lower() )
        #split it into it's correct units and volume
        count = measures[0][1].replace(",","")
        uType = measures[0][2].strip()
        s = float( count )
        u = uType
        m = unit(u)
        
        if self.config['debug']:
            print "Replied to comment: {} in subreddit: {} with \r\n".format( comment.id, comment.subreddit )
            print "{}?! That's {}\r\n".format( self.kilo( m( s ) ), self.bees( m( s ) ) )

        if not self.config['silent']:
            comment.reply( "{}?! That's {}".format( self.kilo( m( s ) ), self.bees( m( s ) ) ) )
            kg2db.add_comment( comment.id )
    
