import twitter
import getopt
import sys, os
import ConfigParser

def main():
    global config

    #try to open a .clitterrc file from the user's home
    try:
        f = open('%s/.clitterrc' % (os.path.expanduser('~')), 'rb')
        config = ConfigParser.RawConfigParser()
        config.readfp(f)
    except:
        print 'First run!\nAdded .clitterrc to your home directory'
        print 'Put your username and password in there!'
        f = open('%s/.clitterrc' % (os.path.expanduser('~')), 'wb')
        template = """[Main]
username = twitter_username
password = twitter_password
        """
        f.write(template)
        f.close
        sys.exit(2)

    try:
        opts, args = getopt.getopt(
                sys.argv[1:],\
                'lfur',\
                ['list', 'follow=', 'update=', 'replies']\
        )
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('--list', '-l'):
            _list()
            break
        elif opt in ('--follow', '-f'):
            follow(arg)
            break
        elif opt in ('--update', '-u'):
            update(arg)
            break
        elif opt in ('--replies', '-r'):
            replies()
            break

def usage():
    print """
Usage is as follows:

To list your friends status update:
    clitter --list

To make an update:
    clitter --update="suck it!"
    """

def _list():
    api = twitter.Api(username=config.get('Main', 'username'),
        password=config.get('Main', 'password'))

    try:
        timeline = api.GetFriendsTimeline(count=14)
    except urllib2.HTTPError:
        print 'Invalid username or password in ~/.clitterrc'
        sys.exit(2)

    for item in timeline:
        print '%s (%s) @ %s' % \
                (item.GetUser().GetName(), 
                 item.GetUser().GetScreenName(),
                 item.GetCreatedAt())
        try:
            print unicode(item.GetText())
        except:
            print 'UNICODE FAIL!'
        print 'Status ID: %s' % (item.GetId())
        print ''

def replies():
    api = twitter.Api(username=config.get('Main', 'username'),
        password=config.get('Main', 'password'))
    
    try:
        timeline = api.GetReplies()
    except urllib2.HTTPError:
        print 'Invalid username or password in ~/.clitterrc'
        sys.exit(2)

    print "Listing replies!\n"
    for item in timeline:
        print '%s (%s) @ %s' % \
                (item.GetUser().GetName(), 
                 item.GetUser().GetScreenName(),
                 item.GetCreatedAt())
        try:
            print unicode(item.GetText())
        except:
            print 'UNICODE FAIL!'
        print 'Status ID: %s' % (item.GetId())
        print ''


def update(status=None):
    api = twitter.Api(username=config.get('Main', 'username'),
        password=config.get('Main', 'password'))

    if status is not None:
        try:
            api.PostUpdate(status)
        except urllib2.HTTPError:
            print 'Invalid username or password in ~/.clitterrc'
            sys.exit(2)

        print 'Status posted!'
    else:
        print 'No status to post'

if __name__=='__main__':
    main()
