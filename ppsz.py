import requests
import hashlib
import time
import json

from component.toutiao import TTBot
from component.user import TTUser

class PPSZ:
    accessToken = ""
    signToken = "3AE419B5-4CC7-4748-9A24-55E79AABB4CA"

    def __init__(self):
        self.updateToken()

    def _timestamp(self):
        return time.strftime("%Y%m%d%H%M%S", time.localtime())

    def _defaultHeader(self):
        return {
            'deviceType': '1',
            'deviceName': 'x86_64_12.4',
            'appVersion': '2.1.9',
            'accessToken': self.accessToken,
            'Content-Type': 'application/json;charset=UTF-8',
            'deviceId': '3AE419B5-4CC7-4748-9A24-55E79AABB4CA',
            'language': 'zh',
            'sign': ''
        }

    def get(self, url, parma=None):
        requesturl = url
        if parma and len(parma) > 0:
            requesturl = requesturl + "?"
            for key in parma.keys():
                requesturl = requesturl + key + "=" + parma[key] + "&"
            requesturl = requesturl[:len(requesturl)-2]
        else:
            return ""
        timestamp = self._timestamp()
        header = self._defaultHeader()
        header["timestamp"] = timestamp
        token = (timestamp + self.signToken).encode(encoding='utf-8', errors = 'strict')
        token = hashlib.md5(token).hexdigest()
        header["sign"] = token
        res = requests.request("GET", requesturl, headers=header).json()
        return res["retData"]

    def post(self, url, parma=None):
        parmastr = ""
        if parma and len(parma) > 0:
            parmastr = json.dumps(parma)
        else:
            return ""
        timestamp = self._timestamp()
        header = self._defaultHeader()
        header["timestamp"] = timestamp
        token = (timestamp + parmastr + self.signToken).encode(encoding='utf-8', errors = 'strict')
        token = hashlib.md5(token).hexdigest()
        header["sign"] = token
        res = requests.request("POST", url, headers=header, data=parmastr).json()
        return res["retData"]

    def updateToken(self):
        guestLogin = "http://service.paopaosz.com:8080/v2/guestLogin"
        guestLoginPayload = {"push_token":""}
        try:
            retData = self.post(guestLogin,guestLoginPayload)
            print(retData)
            self.accessToken = retData["accessToken"]
            self.signToken = retData["signToken"]
        except Exception as e:
            print(e)
            return False
        else:
            return True
    
    def topTopicList(self, circleid):
        url = "http://service.paopaosz.com:8080/v2/circleTopicList"
        parma = {
            "page": "1",
            "id": circleid,
            "viewType": "3",
            "tag": "",
            "keyword": ""
        }
        return self.post(url, parma=parma)["topics"]

    def fetchOneTopicToPublish(self, topicId = "NWpqNGRkMjY="):
        topicSetPublished = set()
        try:
            with open('./topicSetPublished.json', 'r') as infile:
                topicSetPublished = set(json.load(infile))
        except FileNotFoundError:
            print("need create file topicSetPublished.json")
        
        topTopics = ppsz.topTopicList(topicId)

        oneTopic = ""
        for topic in topTopics:
            images = topic["images"]
            oneTopicId = topic["id"]
            if isinstance(images, list) and len(images) > 0 and topic["isDigest"] == 1 and (oneTopicId not in topicSetPublished):
                topicSetPublished.add(oneTopicId)
                oneTopic = topic
                break

        with open('./topicSetPublished.json', 'w+') as outfile:
            json.dump(list(topicSetPublished), outfile)
        return oneTopic

    def publishTopic(self, topicid):

        pass

if __name__ == '__main__':
    ppsz = PPSZ()
    time.sleep(1)

    topic = ppsz.fetchOneTopicToPublish()
    images = topic["images"]
    content = topic["content"]
    cover_img = images[0]["url"]

    a = TTBot()
    account = a.account
    account.login()
    account.post_article(title=topic["title"],content="",run_ad=False,cover_img=cover_img)    
