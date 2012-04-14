import redis
import datetime
import time

r = redis.Redis(host='localhost', port=6379, db=0)

if __name__ == "__main__":
    print "this will delete all the data in redis"
    print "you should only run this at the start of the competition"
    print "are you sure you want to do this? [y/n]"
    x = raw_input()
    if x == "y":
        print "gogo"
        keys = r.keys("org.srobo.*")
        for x in keys:
            r.delete(x)
        r.delete("org.srobo.matches")
        r.delete("org.srobo.time.start")
        dt = datetime.datetime.strptime('Sat 14 Apr 2012 09:00:00 AM BST','%a %d %b %Y %H:%M:%S %p %Z')
        competition_9am = int(time.mktime(dt.timetuple()))
        r.set("org.srobo.time.start", competition_9am) 
        r.set("org.srobo.time.offset", r.get("org.srobo.time.start"))
        r.set("org.srobo.time.paused", False)
    else:
        print "OK!"
