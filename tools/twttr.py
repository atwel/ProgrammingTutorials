# -*- coding: utf-8 -*-

import os
import sys
import twitter
import networkx as nx
import pickle
import datetime

import math
import time
import random

from tools import liwc
from whoosh import fields, index
from whoosh.qparser import QueryParser
from whoosh.qparser.dateparse import DateParserPlugin
from whoosh.qparser import GtLtPlugin

#from twitter.oauth import write_token_file, read_token_file
#from twitter.oauth_dance import oauth_dance


# Go to http://twitter.com/apps/new to create an app and get these items
# See also http://dev.twitter.com/pages/oauth_single_token


if not os.path.exists("data"):
    os.mkdir("data")

CATS = ['WC', 'WPS', 'Sixltr', 'Dic', 'Numerals','funct', 'pronoun', 'ppron', 'i',
        'we', 'you', 'shehe', 'they', 'ipron', 'article', 'verb', 'auxverb', 'past',
        'present', 'future', 'adverb', 'preps','conj', 'negate', 'quant', 'number',
        'swear', 'social', 'family', 'friend', 'humans', 'affect', 'posemo', 'negemo',
        'anx', 'anger', 'sad', 'cogmech','insight', 'cause', 'discrep', 'tentat',
        'certain', 'inhib', 'incl', 'excl','percept', 'see', 'hear', 'feel', 'bio',
        'body', 'health', 'sexual', 'ingest', 'relativ', 'motion', 'space', 'time',
        'work', 'achieve', 'leisure', 'home', 'money', 'relig', 'death', 'assent',
        'nonfl', 'filler','Period', 'Comma', 'Colon', 'SemiC', 'QMark', 'Exclam',
        'Dash', 'Quote', 'Apostro', 'Parenth', 'OtherP', 'AllPct']


MONTHS = {"Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}


class TWTTR(object):

    def __init__(self):
        self.INDEX = None
        self.TWIT_PIPE = None
        self.NET = nx.DiGraph()
        self.APP_NAME = 'CSCS/SOC 260'
        self.CONSUMER_KEY = 'xPszGbQonsIFz0Ldz9zf8w'
        self.CONSUMER_SECRET = 's0hlqWZE9YFIS8XE2rZP2A10L3u5Xh4loc4lpaQkQ'
        self.ACCESS_TOKEN = '1441665122-odjHb5V7M5FOl4CxWUwTkyOsh9afwOtmEGKI2sj'
        self.ACCESS_TOKEN_SECRET = 'giUrhFNLthrD8psLeG5vjaEva2AxyVnM0jME9DX0J1vQY'


    def create_index(self):
        if not os.path.exists("twitter_index"):
            os.mkdir("twitter_index")


        schema = fields.Schema(tweet_id=fields.TEXT(stored=True),
                                batch=fields.NUMERIC(stored=True),
                                content=fields.TEXT(stored=True),
                                posted=fields.DATETIME(stored=True),
                                owner_sn=fields.TEXT(stored=True),
                                owner_id=fields.TEXT(stored=True),
                                owner_name=fields.TEXT(stored=True),
                                isRT=fields.BOOLEAN(stored=True),
                                timesRT=fields.NUMERIC(stored=True),
                                timesFav= fields.NUMERIC(stored=True),
                                hashtags=fields.KEYWORD(stored=True),
                                orgnlTweet = fields.TEXT(stored=True),
                                mentions=fields.KEYWORD(stored=True),
                                media = fields.TEXT(stored=True),
                                url = fields.TEXT(stored=True),
                                liwc=fields.TEXT(stored=True))


        self.INDEX = index.create_in("twitter_index", schema, indexname="TWTTR")
        print("New searching index succesfully created")

        return self.INDEX


    def clear_index(self):
        stem = os.getcwd()
        files = os.walk("twitter_index")
        for i in files:
            for j in i[2]:
                try:
                    os.remove(stem+"/twitter_index/"+j)
                except:
                    os.remove(stem+"/twitter_index/TWTTR.tmp/"+j)

        self.create_index()


    def login(self, token_file='out/twitter.oauth'):

        self.TWIT_PIPE = twitter.Api(self.CONSUMER_KEY, self.CONSUMER_SECRET,self.ACCESS_TOKEN, self.ACCESS_TOKEN_SECRET)
        self.TWIT_PIPE.tweet_mode = "extended"


    def cleanName(self, name):

        try:
            if type(name) == int:
                user = self.TWIT_PIPE.GetUser(user_id=int(name))
            else:
                user = self.TWIT_PIPE.GetUser(screen_name=name)
            return user
        except:
            raise ValueError("Could not find a user with name {}".format(name))



    def viewUser(self,name, save=True):

        user_obj = self.cleanName(name)
        data = user_obj.AsDict()
        user_id = data["id"]
        if save:
            self.NET.add_node(user_id)
            self.NET.node[user_id]["friends_count"]=data["friends_count"]
            self.NET.node[user_id]["followers_count"]=data["followers_count"]

        strg = "<p><h3><li>User Name:\t\t{}</li></h3><br>".format(data["screen_name"])
        strg += "<li>User ID:\t\t{}</li>".format(user_id)
        strg += "<li>Tweets:\t\t{}</li>".format(data["statuses_count"])
        strg += "<li> Followers:\t\t{}</li>".format(data["followers_count"])
        strg += "<li> Friends:\t\t{}</li>".format(data["friends_count"])
        strg += "<li> Joined:\t\t{}</li>".format(data["created_at"])
        try:
            strg += "<li> Verified:\t\t{}</li></p>".format(data["verified"])
        except:
            strg += "</p>"

        return strg


    def getFriends(self, name, save=True):

        friends = []
        next_cursor = -1
        while next_cursor != 0 and len(friends) < 30000:
            time.sleep(random.randint(0,15))
            data = self.TWIT_PIPE.GetFriends(screen_name=name,cursor=next_cursor)
            friends += data["ids"]
            next_cursor = data["next_cursor"]

        #print friends
        #print data

        try:
            self.NET.node[id]
        except:
            self.NET.add_node(id)

        if save:
            for i in friends:
                self.NET.add_node(i)
                self.NET.add_edge(i, usn)

            self.NET.node[id]["friends"] = friends

        return friends

    def getFollowers(self,name, save=True):


        followers = []
        next_cursor = -1
        while next_cursor != 0 and len(followers) < 30000:
            time.sleep(random.randint(0,15))
            data = self.TWIT_PIPE.GetFollowerIDs(screen_name=name,cursor=next_cursor)
            followers += data["ids"]
            next_cursor = data["next_cursor"]
        #print followers

        try:
            self.NET.node[id]
        except:
            self.NET.add_node(id)

        if save:
            for i in data:
                self.NET.add_node(i)
                self.NET.add_edge(usn,i)

            self.NET.node[id]["followers"] = followers

        return followers

    def getTweet(self,the_id):

        return self.TWIT_PIPE.GetStatus(the_id)

    def getUsersTweets(self,name, count=200):

        tweets = self.TWIT_PIPE.GetUserTimeline(screen_name=name,count=count)

        cleaned = []
        for tw in tweets:
            i = self.cleanTweet(tw)
            print("__"*15)
            print("TweetID:\t\t", i["tweet_id"])
            print()
            print("User Name:\t",i["user_name"])
            print("screen name:\t",i["user_sn"])
            print("Posted:\t\t",i["posted"])
            print("Text:\t\t",i["text"])
            print("Media?:\t",i["media"])
            print("Mentions:\t", i["mentions"])
            print("Is Retweet:\t", i["isRT"])
            print("Times RT'd:\t", i["rt_count"])
            print("Times Fav'd:\t", i["fav'd"])
            cleaned.append(i)

        return cleaned


    def index_Tweets(self,tweets, batch=1):


        if type(batch) != int:
            print("Invalid batch name. It needs to be a number. Tweets not added to the index.")

        elif type(self.INDEX) == None:
            print("The INDEX has not yet been created")

        else:
            try:
                ix = index.open_dir("twitter_index", indexname="TWTTR")
                w = ix.writer()
            except:
                ix = self.create_index()
                w = ix.writer()
            for tw in tweets:


                #try:
                    w.add_document(tweet_id = str(tw["tweet_id"]),
                                    batch = batch,
                                    content = tw["text"],
                                    posted = tw["posted"],
                                    owner_sn = tw["user_sn"],
                                    owner_name = tw["user_name"],
                                    owner_id = str(tw["user_id"]),
                                    hashtags = tw["hashtags"],
                                    mentions = tw["mentions"],
                                    isRT = bool(tw["isRT"]),
                                    timesRT = int(tw["rt_count"]),
                                    timesFav = int(tw["fav'd"]),
                                    orgnlTweet = str(tw["orig"]),
                                    media = tw["media"],
                                    url = str("./tools/nodata.html"),
                                    liwc = str(tw["liwc"]))
            w.commit()
                #except:
                    #pass

    def decode_text(self,text):

        try:
            clean = str(text.encode('utf-8'))

        except:
            clean = str(text.decode("utf-8",'replace'))

        return clean

    def cleanTweet(self,tweet):
        cleaned = {}

        tw = tweet.AsDict()

        if "retweeted_status" in tw.keys():
            isRT = True
            cleaned["orig"] = tw["retweeted_status"]["id"]
            if "full_text" in tw["retweeted_status"].keys():
                full_rt_text = tw["retweeted_status"]["full_text"]
                cleaned["text"] = tw["retweeted_status"]["full_text"]
        else:
            isRT = False
            cleaned["orig"] = "NA"
            if "truncated" in tw.keys():
                tw = self.TWIT_PIPE.GetStatus(tw["id"]).AsDict()
                cleaned["text"] = w["full_text"]
            else:
                cleaned["text"] = tw["full_text"]
        cleaned["isRT"] = isRT

        cleaned["text"] = cleaned["text"].replace("\"","\'")
        if isRT:
            cleaned["rt_count"] = tw["retweet_count"]
        else:
            cleaned["rt_count"] = 0

        try:
            cleaned["fav'd"] = int(tw["favorite_count"])
        except:
            cleaned["fav'd"] = 0

        try:
            cleaned["media"] = tw["media"][0]["type"]
        except:
            cleaned["media"] = "None"

        #print([(type(x),x) for x in tw["hashtags"]])
        ht = ",".join([x["text"] for x in tw["hashtags"]])
        if ht =='':
            ht = "None"
        cleaned["hashtags"] = ht

        sn = []
        for m in tw["user_mentions"]:
            sn.append(m["screen_name"])
        cleaned["user_id"] = tw["user"]['id']
        cleaned["mentions"] = ",".join(sn)
        cleaned["tweet_id"] = tw["id"]
        cleaned["user_sn"] = tw["user"]["screen_name"]
        cleaned["user_name"] = tw["user"]["name"]
        cleaned["posted"] = self.to_datetime(tw["created_at"])
        cleaned["liwc"] = self.liwc_parse(cleaned["text"])

        return cleaned

    def to_datetime(self,created_at):

        d = created_at.split(" ")
        t = d[3].split(":")

        return datetime.datetime(int(d[5]),int(MONTHS[d[1]]), int(d[2]), int(t[0]),
                                                int(t[1]),int(t[2]),int("00"))


    def search(self,terms, limit=100, time_slice=None, saveAs="search"):

        big_tables = {}
        for i in CATS:
            big_tables[i]=[]

        f = open("./visualizations/"+saveAs+"_results.html", "w+")
        master_str = "<!DOCTYPE html><html><style>hr {border: 4;width: 80%;}</style>"+ "<title>Search Results [term(s): "+terms+"]</title><body><br>"

        ix = index.open_dir("twitter_index", indexname="TWTTR")
        w = ix.writer()
        qp = QueryParser("content", schema=w.schema)
        qp.add_plugin(DateParserPlugin())
        qp.add_plugin(GtLtPlugin())
        q = qp.parse(terms)
        print("search terms", q)
        list_IDs =[]
        with w.searcher() as s:
            results = s.search(q, limit=limit)
            if time_slice != None:
                within = []
                start = int("".join(time_slice[0].split(":")))
                end = int("".join(time_slice[1].split(":")))
                if (0<=start<=2400) and (0 <=end<=2400):
                    for res in results:
                        time = res["posted"]
                        if time.minute < 10:
                            t = int(str(time.hour)+"0"+ str(time.minute))
                        else:
                            t = int(str(time.hour)+ str(time.minute))

                        if start < end and start <= t <=end:
                            within.append(res)
                        elif end < start and (start <= t or t <= end):
                            within.append(res)
                        else:
                            pass

                    results = within
                else:
                    print("Invalid time slice, no results returned.")
                    results = []
            print("%d search results" % len(results))
            print("--"*15)
            for res in results:
                list_IDs.append(int(res["tweet_id"]))
                self.to_nums(res["liwc"], big_tables)
                master_str += self.to_html(res, True)

            master_str += "</body></html>"
            f.write(master_str)
            f.close()

            res_str = "<!DOCTYPE html><html><title>LIWC statistics for term(s):"+terms+"</title><body><br>"
            res_str += "<table><tr>"+("<th>Category&nbsp;</th><th>Average</th><th>Std Dev</th><th>Max&nbsp</th><th>Min&nbsp</th>"*3)+"</tr>"
            count = 0
            for_later = {}
            for j in list(big_tables.keys()):
                vals = big_tables[j]
                #print j, vals
                outputs = []
                if len(vals) != 0:
                    avg = sum(vals)/float(len(vals))
                    outputs.append(round(avg,4))
                    var = [(i-avg)**2 for i in vals]
                    std = math.sqrt(sum(var)/len(var))
                    outputs.append(round(std,4))
                    outputs.append(round(max(vals),4))
                    outputs.append(round(min(vals),4))
                else:
                    outputs = ["NA","NA","NA","NA"]
                if count%3 == 0:
                    res_str+= "<tr>"


                res_str += "<td>"+str(j)+"</td><td>"+str(outputs[0])+"</td><td>"+str(outputs[1])
                res_str += "</td><td>"+str(outputs[2])+"</td><td>"+str(outputs[3])+"</td>"
                count +=1
                if count%3 == 0:
                    res_str+= "</tr>"
                for_later[j] = outputs

            res_str+="</table>"

            if big_tables["WC"] == []:
                big_tables = ""
                res_str = "<!DOCTYPE html><html><title>LIWC statistics for term(s): "
                res_str += terms+"</title><body><br>"
                res_str += "<p>No matches found </p></body></html>"

            t = open("./visualizations/"+ saveAs +"_averages.html", "w+")
            t.write(res_str)
            t.close()

            self.graph_Tweets(results,saveAs)

        return res_str, for_later, master_str, list_IDs

    def to_nums(self, strg, tables):
        chk = strg[1:-1].split("],[")

        vals = chk[0].split(",")
        for i in range(len(vals)):
            tables[CATS[i]].append(float(vals[i]))


    def to_html(self,tweet, withtable):
        """ tweet is a dictionary"""


        print(tweet["owner_name"], " : ", tweet["content"])
        print()

        try:
            big_str =  "<h2 style=\"color:DarkBlue\">"+str(tweet["owner_name"])+"</h2>"
        except:
            big_str = "<h2>Error parsing title</h2>"

        big_str += "<p>TweetID: "+str(tweet["tweet_id"])+"</p>"
        try:
            big_str += "<p><h3>"+tweet["content"]+"</h3></p>"
        except:
            big_str += "<h2>Error parsing tweet text</h2>"

        try:
            big_str += "<li>Posted "+str(tweet["posted"])+"</li>"
            big_str += "<li>Hashtags: " + str(tweet["hashtags"]) + "</li>"
            big_str += "<li>Is a retweet?: " + str(tweet["isRT"]) + "</li>"
            big_str += "<li>Original TweetID: " +str(tweet["orgnlTweet"])+"</li>"
            big_str += "<li>Times retweeted: " + str(tweet["timesRT"]) + "</li>"
            big_str += "<li>Times favorited: " + str(tweet["timesFav"]) + "</li>"
            big_str += "<li>Mentions: " + str(tweet["mentions"]) + "</li>"
            #big_str += "<li>URL:\t\t"+str(tweet["url"])+"</li>"

        except:
            big_str += "<li>Date error, but it's still searchable</li>"
        if withtable:
            #print tweet["liwc"]
            i = tweet["liwc"].replace("[", "").replace("]","")
            big_str += "<p>"+self.liwc_str_to_html_table(i)+"</p>"

        big_str += "<br><hr><br>"


        return big_str


    def liwc_str_to_html_table(self,strng):
        bos  = "<table><tr>"+("<th>Category&nbsp;&nbsp;</th><th>Percent&nbsp;&nbsp;</th>"*6)+"</tr>"
        count = 0
        ss = strng.split(",")
        #print ss
        for i in range(len(ss)):
            if count%6 == 0:
                bos+= "<tr>"

            if float(ss[i]) != 0.0:
                bos += "<td>"+str(CATS[i])+"</td><td>"+str(ss[i])+"</td>"
                count +=1
            if count%6 == 0:
                bos+= "</tr>"
        bos+="</table>"

        return bos

    def liwc_parse(self,sentence):
        counts = liwc.from_text(sentence)
        reordered = []
        for j in CATS:
            try:
                reordered.append(round(counts[j],4))
            except:
                reordered.append(0)

        return reordered


    def inspectRetweets(self,ids):

        self.loadNetwork()

        ix = index.open_dir("twitter_index", indexname="TWTTR")

        retweets = ids

        for i in retweets:
            print("Inspecting Tweet #"+str(i))
            htmlname = int(i)
            node_dic = {}
            edges = []
            nodes = []
            count = 0
            isRetweet = True


            docs_to_update = []
            docs_to_update.append(i)
            # this gets us the "downstream" tweets
            rts = [tw.AsDict() for tw in self.TWIT_PIPE.GetRetweets(statusid=i, count=100)]

            orig = int(i)
            j = i
            #print("first rts", type(rts))
            while isRetweet:
                #This gets us the upstream tweet(s)
                rttw = self.TWIT_PIPE.GetStatus(status_id=j).AsDict()
                #print(rttw)
                try:
                    j = rttw["retweeted_status"]["id"]
                    #print("j in try loop",j)
                    retweets = [tw.AsDict() for tw in self.TWIT_PIPE.GetRetweets(statusid=j, count=100)]
                    #print("retweets in try",len(retweets))
                    rts.extend(retweets)

                except:
                    #print("in except loop")
                    if j != orig:
                        rts.extend(rttw)
                        docs_to_update.append(j)
                    isRetweet = False


            #print("second",len(rts))

            final = int(j)
            for j in docs_to_update:
                s = ix.searcher()

                if s.document(tweet_id=str(j)) == None:
                    predoc = self.TWIT_PIPE.GetStatus(status_id=j)
                    out = self.index_Tweets([self.cleanTweet(predoc)])

                try:    #print(out)
                    doc = s.document(tweet_id=str(j))
                    #print doc
                    post_time = doc["posted"]
                    name = "@"+doc["owner_sn"]
                    nodes.append("{\"id\":\""+name+"\",\"value\":8,\"color\":\"gray\"}")
                    owner_sn = doc["owner_sn"]
                    owner_id = doc["owner_id"]

                    ownerhtml = self.viewUser(int(owner_id))

                    node_dic[owner_id] = count
                    count += 1
                    url = "visualizations/"+str(htmlname)+".html"
                    #print("new url",url)
                    w = ix.writer()
                    w.update_document(tweet_id = doc["tweet_id"],
                                            batch = doc["batch"],
                                            content = doc["content"],
                                            posted = doc["posted"],
                                            owner_name = doc["owner_name"],
                                            owner_sn = doc["owner_sn"],
                                            owner_id = doc["owner_id"],
                                            hashtags =doc["hashtags"],
                                            mentions = doc["mentions"],
                                            isRT = doc["isRT"],
                                            timesRT = doc["timesRT"],
                                            timesFav = doc["timesFav"],
                                            orgnlTweet = doc["orgnlTweet"],
                                            media = doc["media"],
                                            url = str(url),
                                            liwc = doc["liwc"])


                    w.commit()
                except:
                    pass
            i = int(final)
            retweeters1 = []
            times = []
            delta_avg = []
            for j in rts:
                if type(j) == dict():
                    retweeters1.append(j["user"]["id"])
                    times.append(j["created_at"])
                    delta = self.to_datetime(j["created_at"]) - post_time

                    diff = int((24*delta.days) + (delta.seconds/3600.))
                    delta_avg.append(diff)
                    #print val
                    try:
                        val = node_dic[int(j["user"]["id"])]
                    except:
                        val =int(count)
                        node_dic[int(j["user"]["id"])] = count
                        count += 1
                    edges.append("{\"source\":"+str(node_dic[owner_id])+",\"target\":"+str(val)
                                    +",\"length\":"+str(diff)+"}")

                    poster_id = j["retweeted_status"]["user"]["id"]

            counts = [0,0,0]
            if retweeters1 != []:
                retweeters = []
                for k in range(len(retweeters1)):
                    retweeters.append(k)


                try:
                    friends = self.NET.node[poster_id]["friends"]
                except:
                    friends = self.getFriends(poster_id)
                try:
                    followers = self.NET.node[poster_id]["followers"]
                except:
                    followers = self.getFollowers(poster_id)

                self.saveNetwork()
                #print "friends", friends

                counts = [0,0,0]
                for uid in node_dic:

                    if uid != poster_id:
                        if (uid in retweeters):
                            if uid in followers:

                                if uid in friends:
                                    tw = retweeters1[retweeters.index(uid)]
                                    nodes.append("{\"id\":"+("\"@"+str(tw))
                                                    +"\",\"value\":5,\"color\":\"blue\"}")
                                    counts[1] +=1
                                else:
                                    tw = retweeters1[retweeters.index(uid)]
                                    nodes.append("{\"id\":"+("\"@"+str(tw))
                                                    +"\",\"value\":5,\"color\":\"green\"}")
                                    counts[0] +=1
                            else:
                                tw = retweeters1[retweeters.index(uid)]
                                nodes.append("{\"id\":"+("\"@"+str(tw))
                                                +"\",\"value\":5,\"color\":\"purple\"}")
                                counts[2] +=1
                        else:
                            nodes.append("{\"id\":\"UNKNOWN\",\"value\":5,\"color\":\"purple\"}")
                            counts[2] +=1

            strg = "{\"nodes\":[\n"
            for k in nodes:
                strg += k + ",\n"
            strg = strg[:-2] + "],\n\"links\":["
            for f in edges:
                strg += f+",\n"
            strg = strg[:-2] + "]}"

            newfile = open("./visualizations/"+str(htmlname)+".json", "w+")
            newfile.write(strg)
            newfile.close()

            try:
                dmax = max(delta_avg)
                dmin = min(delta_avg)
                davg = sum(delta_avg)/float(len(delta_avg))
            except:
                dmax,dmin,davg = 0,0,0
            try:
                html = "<p>"+ownerhtml+"<br>"
                html += self.to_html(doc,True)
                html += "<h4><li>Earliest retweet:\t\t"+str(dmin)+" hour(s) after</li>"
                html += "<li>Last retweet:\t\t\t "+str(dmax)+" hour(s) after</li>"
                html += "<li>Average wait before retweet:\t " +str(davg) +" hour(s)</li>"
                html += "<li>All wait times:\t" +str(delta_avg)+ "</li></h4></p>"
                html += "<br><p>NODE COLORS</p>  <p><h3> green: followers ("+str(counts[0])+") &nbsp&nbsp blue: friends ("+str(counts[1])+") &nbsp&nbsp purple: neither ("+str(counts[2])+")</h3></p>"
            except:
                pass


            form = open("./tools/base.html", "r+")
            file2 = open(url, "w+")
            lines = form.readlines()
            for ln in lines:
                if "<body>" in ln:
                    ln = ln + html
                if "fake.json" in ln:
                    ln = ln.replace("fake.json",str(htmlname)+".json")
                file2.write(ln)
            file2.close()
            form.close()


    def tweetSearch(self,terms, tweet_type="recent"):

        tweets = self.TWIT_PIPE.GetSearch(term=terms,result_type=tweet_type, count=100)

        print("{} tweets found".format(len(tweets)))
        cleaned_tweets = []
        for tw in tweets:
            i = self.cleanTweet(tw)

            print("__"*15)
            print("TweetID:\t\t", i["tweet_id"])
            print()
            print("User Name:\t",i["user_name"])
            print("screen name:\t",i["user_sn"])
            print("Posted:\t\t",i["posted"])
            print("Text:\t\t",i["text"])
            print("Media?:\t",i["media"])
            print("Mentions:\t", i["mentions"])
            print("Is Retweet:\t", i["isRT"])
            print("Times RT'd:\t", i["rt_count"])
            print("Times Fav'd:\t", i["fav'd"])

            cleaned_tweets.append(i)

        return cleaned_tweets


    def graph_Tweets(self,results,saveAs):
        owners = {}
        scale = len(results)
        for tweet in results:
            safe_content = tweet["content"].replace("\n","").replace("\r","").replace("<br>","")
            if tweet["owner_name"] in owners.keys():
                owners[tweet["owner_name"]].append([tweet["tweet_id"], tweet["timesRT"], tweet["timesFav"], tweet["url"],safe_content])
            else:
                owners[tweet["owner_name"]] = [[tweet["tweet_id"], tweet["timesRT"], tweet["timesFav"], tweet["url"],safe_content]]


        size_dict = {}
        bs = "{\"name\": \"flare\", \"children\": ["
        for owner,data in owners.items():

            bs += "{\"name\":\""+str(owner)+"\",\"children\": ["
            for tw in data:

                size = tw[1]+8
                bs += "{\"name\":\""+str(tw[0])+"\", \"size\":" + str(size)+", \"text\":\"" + str(tw[4])+"\", \"fvvalue\":" + str(tw[2])+ ",\"url\":\""+str(tw[3])+"\"},"
                #size_list.append(size)
                size_dict[tw[0]] = [size, owner]

            bs = bs[:-1] + "]},"
        bs = bs[:-1]+ "]}"
        sl = sorted(size_dict, key=lambda key: size_dict[key][0], reverse=True)
        doc = open("./visualizations/"+saveAs+".json", "w+")
        doc.write(bs)
        doc.close()
        #sl = sorted(size_list)
        id_strg = "<br><br>"
        space = "&nbsp"*10
        for key in sl:
            v = size_dict[key]
            id_strg += "<p>Owner: "+str(v[1])+space+" Retweets: "+str(v[0]-8)+space+" TweetID: "+str(key)+"</p>"

        form = open("./tools/tweetpack.html", "r+")
        file = open("./visualizations/"+saveAs+".html", "w+")
        lines = form.readlines()
        for ln in lines:
            if "search.json" in ln:
                #print "replaced"
                ln = ln.replace("search.json", saveAs+".json")
            if "</body>" in ln:
                ln = id_strg + "</body>"
            file.write(ln)
        file.close()
        form.close()




    def saveNetwork(self):
        output = open('net.pkl', 'wb')
        pickle.dump(self.NET, output)

    def deleteNetwork(self):
        os.remove("net.pkl")
        self.NET = nx.DiGraph()

    def loadNetwork(self):
        try:
            old_net = open("net.pkl", 'rb')
            self.NET = pickle.load(old_net)
        except:
            self.NET = nx.DiGraph()

    def LIWC_differences(self, data1, data2):

        res_str = "<!DOCTYPE html><html><title>Differences: Avg, StdDev, Max, Min</title><body><br>"
        res_str += "<table><tr>"+("<th>Category&nbsp;</th><th>Average</th><th>Std Dev</th><th>Max&nbsp</th><th>Min&nbsp</th>"*3)+"</tr>"
        count = 0
        for i in CATS:
            val1 = data1[i]
            val2= data2[i]
            res = [j-k for j,k in zip(val1, val2)]

            if count%3 == 0:
                res_str+= "<tr>"


            res_str +="<td>"+str(i)+"</td><td>"+str(res[0])+"</td><td>"+str(res[1])+"</td><td>"
            res_str +=str(res[2])+"</td><td>"+str(res[3])+"</td>"
            count +=1
            if count%3 == 0:
                res_str+= "</tr>"
        res_str+="</table>"

        return res_str


    def LIWC_differences_subset(self,data1, data2, mylist):

        res_str = "<!DOCTYPE html><html><title>Differences: Avg, StdDev, Max, Min</title><body><br>"
        res_str += "<table><tr>"+("<th>Category&nbsp;</th><th>Average</th><th>Std Dev</th><th>Max&nbsp</th><th>Min&nbsp</th>"*3)+"</tr>"
        count = 0
        for i in CATS:
            val1 = data1[i]
            val2= data2[i]
            res = [j-k for j,k in zip(val1, val2)]

            if count%3 == 0:
                res_str+= "<tr>"

            if i in mylist:
                res_str +="<td>"+str(i)+"</td><td>"+str(res[0])+"</td><td>"+str(res[1])+"</td><td>"
                res_str +=str(res[2])+"</td><td>"+str(res[3])+"</td>"
                count +=1

            if count%3 == 0:
                res_str+= "</tr>"
        res_str+="</table>"
        return res_str
