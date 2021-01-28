import tweepy,json,os,time

def limit_handled(cursor):
    while True:
        try:
            yield next(cursor)
        except tweepy.RateLimitError:
            print("Waiting 15min...")
            time.sleep(15 * 60)
        except StopIteration:
            break

class EmojiMashupBot():
    def __init__(self,access_tokens,store_file="tweets.json"):
        auth = tweepy.OAuthHandler(access_tokens["CONSUMER_KEY"], access_tokens["CONSUMER_SECRET"])
        auth.set_access_token(access_tokens["ACCESS_KEY"], access_tokens["ACCESS_SECRET"])
        self.api = tweepy.API(auth)
        self.store_file=store_file
        
        if not os.path.exists(self.store_file):
            self.tweets=list()
            self.get_tweets()
        else:
            self.get_config()

    def get_tweets(self):
        tweets=list()
        index=0
        print("Début du téléchargement")
        for status in limit_handled(tweepy.Cursor(self.api.user_timeline,id="EmojiMashupBot").items()):
            if status.text.count("+")==1 and "media" in status.entities and len(status.entities["media"])==1:
                tweets.append({"id":status.id,"text":status.text,"rt":status.retweet_count,"likes":status.favorite_count,"image":status.entities["media"][0]["media_url"]})
            index+=1
            print("Téléchargement du tweet {}".format(index), end='\r')
        self.data={"last_id":tweets[0]["id"],"tweets":tweets,"last_updated":time.time()}
        self.save_config()
        print("Fin du téléchargement")

    def update_tweets(self):
        print("Début de la mise à jour")
        last_id=self.data["last_id"]
        for status in limit_handled(tweepy.Cursor(self.api.user_timeline,id="EmojiMashupBot",since_id=last_id).items()):
            if self.data["last_id"]==last_id: self.data["last_id"]=status.id
            if status.text.count("+")==1 and "media" in status.entities and len(status.entities["media"])==1:
                self.data["tweets"].append({"id":status.id,"text":status.text,"rt":status.retweet_count,"likes":status.favorite_count,"image":status.entities["media"][0]["media_url"]})
            
        print("Fin de la mise à jour")

        self.save_config()
        
    def get_top_tweets(self,top=5,exclude_ids=None):
        if exclude_ids is None:
            sorted_tweets=sorted(self.data["tweets"],reverse=True,key=lambda x: x["rt"]+x["likes"])
        else:
            sorted_tweets=sorted([tweet for tweet in self.data["tweets"] if tweet["id"] not in exclude_ids],reverse=True,key=lambda x: x["rt"]*2+x["likes"])
        return sorted_tweets[:top]

    def get_config(self):
        with open(self.store_file,'r',encoding='utf-8') as f:
            self.data=json.load(f)

    def save_config(self):
        with open(self.store_file,'w',encoding='utf-8') as f:
            json.dump(self.data,f)

if __name__ == "__main__":
    with open("config.json") as f:
        mashup=EmojiMashupBot(json.load(f)["twitter"])

    print(mashup.get_top_tweets(1)[0]["image"])
