import sys, os
import urllib2, urllib
import base64
import curses
import curses.wrapper
import ConfigParser

try:
    import json
except:
    import simplejson as json

class ApiInterface(object):
    username = None
    password = None
    headers = {}
    urllib = None

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def _SetAuthHeaders(self):
        basic_auth = base64.encodestring('%s:%s' % \
                (self.username, self.password))[:-1]
        self.headers['Authorization'] = 'Basic %s' % (basic_auth)

    def _GetAuthOpener(self):
        handler = urllib2.HTTPBasicAuthHandler()
        opener = urllib2.build_opener(handler)
        self._SetAuthHeaders()
        opener.addheaders = self.headers.items()

        return opener

    def _GetStandardOpener(self):
        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)
        return opener
    
    def _JsonDecode(self, data):
        return json.loads(data)

    # Methods requiring an Authenticated opener
    def GetFriendTimeline(self, count=18):
        opener = self._GetAuthOpener()
        url = 'http://api.twitter.com/1/statuses/friends_timeline.json' \
                '?count=%d' % (count)
        items = opener.open(url).read()
        opener.close()
        items = self._JsonDecode(items)
        return [Status.FromDict(i) for i in items]

    def GetReplies(self, count=10):
        opener = self._GetAuthOpener()
        url = 'http://api.twitter.com/1/statuses/mentions.json?count=%d' % \
                (count)
        items = opener.open(url).read()
        opener.close()
        items = self._JsonDecode(items)
        return [Status.FromDict(i) for i in items] 

    def PostUpdate(self, status):
        opener = self._GetAuthOpener()
        url = 'http://api.twitter.com/1/statuses/update.json'
        data = {'status': status}
        data = urllib.urlencode(dict([(k, unicode(v)) for k, v in data.items()]))
        item = opener.open(url, data)
        item = json.loads(item)
        return Status.FromDict(item)

    # Methods that don't...
    def GetTrendingTopics(self):
        opener = self._GetStandardOpener()
        url = 'http://search.twitter.com/trends.json'
        items = opener.open(url).read()
        opener.close()
        items = self._JsonDecode(items)
        return [Trend.FromDict(i) for i in items['trends']]

    def Search(self):
        pass
        
class Status(object):
    """
    Holds a single status. This object has a static method to
    populate it from a json dict.
    """

    text = None
    created_at = None
    source = None
    id = None
    user = None

    def __init__(self, text, created_at, source, id, user):
        self.text = text
        self.created_at = created_at
        self.source = source
        self.id = id
        self.user = user

    def GetText(self):
        return self.text

    def GetCreated(self):
        return self.created_at

    def GetSource(self):
        return self.source

    def GetId(self):
        return self.id

    def GetUser(self):
        return self.user

    @staticmethod
    def FromDict(data):
        user = User.FromDict(data['user'])
        return Status(
                data['text'],
                data['created_at'],
                data['source'],
                data['id'],
                user)

class User(object):
    """
    Holds a single user. This object is mostly populated
    from the Status object when statuses are loaded from 
    the twitter api.
    """

    name = None
    screen_name = None
    location = None
    description = None
    following = None

    def __init__(self, name, screen_name, location, description, following):
        self.name = name
        self.screen_name = screen_name
        self.location = location
        self.description = description
        self.following = following

    def GetName(self):
        return self.name

    def GetScreenName(self):
        return self.screen_name

    def GetLocation(self):
        return self.location

    def GetDescription(self):
        return self.description

    def GetFollowing(self):
        return self.following

    @staticmethod
    def FromDict(data):
        return User(
                data['name'],
                data['screen_name'],
                data['location'],
                data['description'],
                data['following'])

class Trend(object):
    """
    Holds a trending topic from the twitter api.
    """

    name = None
    url = None

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def GetName(self):
        return self.name

    def GetUrl(self):
        return self.url

    @staticmethod
    def FromDict(data):
        return Trend(data['name'], data['url'])

class Clitter(object):

    config = None
    windows = {}
    active_window = None

    def __init__(self):
        try:
            f = open('%s/.clitterrc' % (os.path.expanduser('~')), 'rb')
            self.config = ConfigParser.RawConfigParser()
            self.config.readfp(f)
        except:
            print 'Add twitter accounts to ~/.clitterrc!'
            f = open('%s/.clitterrc' % (os.path.expanduser('~')), 'wb')
            template = """[Main]
[twitter_account_1]
username = twitter_username
password = twitter_password
            """
            f.write(template)
            f.close()
            sys.exit(2)

        # Build a window for each twitter account in .clitterrc
        print self.config.sections()
        self.BuildWindows()

    def BuildWindows(self):
        pass

    def main(self):
        api = ApiInterface('kyleterry', 'MyLamp0wns!')
        items = api.GetFriendTimeline()
        string_items = []
        for i in items:
            string_items.append('@%s (%s): %s\n' % \
                    (i.GetUser().GetScreenName(),
                     i.GetUser().GetName(),
                     i.GetText()))
        stdscr = curses.initscr()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.noecho()
        curses.cbreak()
        #stdscr.keypad(1)
        count = 1
        while True:
            stdscr.refresh()
            if count == 300:
                count = 1
                api = ApiInterface('kyleterry', 'MyLamp0wns!')
                items = api.GetFriendTimeline()
                string_items = []
                for i in items:
                    string_items.append('@%s (%s): %s\n' %\
                            (i.GetUser().GetScreenName(),
                             i.GetUser().GetName(),
                             i.GetText()))
            (height, width) = stdscr.getmaxyx()
            titlebar = curses.newwin(1, width, 0, 0)
            titlebar.clrtoeol()
            titlebar.addstr("Clitter! - Command line Twitter client", curses.color_pair(1))
            titlebar.refresh()

            cursorbar = curses.newwin(1, width, 1, 0)
            cursorbar.addstr(0,0, '>')
            cursorbar.refresh()

            stdscr.move(1,2)

            #account_window = curses.newwin(3, width, 0, 0)
            stdscr.addstr(2, 0, '\n'.join(string_items))
            stdscr.refresh()

            c = stdscr.getch()
            c = chr(c)
            if c == 'q':
                break
            elif c == 'r':
                titlebar.clrtoeol()
                titlebar.addstr(" - refreshing...", curses.color_pair(1))
                titlebar.refresh()
                api = ApiInterface('kyleterry', 'MyLamp0wns!')
                items = api.GetFriendTimeline()
                string_items = []
                for i in items:
                    string_items.append('@%s (%s): %s\n' %\
                            (i.GetUser().GetScreenName(),
                             i.GetUser().GetName(),
                             i.GetText()))
            elif c == curses.KEY_UP: pass
            elif c == curses.KEY_DOWN: pass
            elif c == curses.KEY_RIGHT: pass
            elif c == curses.KEY_LEFT: pass
            count = count + 1
        stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def UpdateWindow(window, items):
        for status in items:
            window.addstr('%s: %s' % (status.GetText(), status.GetUser().GetScreenName()))
            window.addstr('\n')

clitter = Clitter()
curses.wrapper(clitter.main())
