import json
import sys
sys.dont_write_bytecode = True
import requests
import time
import database

from requests_oauthlib import OAuth1

with open("./config.json","r") as content_file:
    config = json.loads(content_file.read())

#authentication pieces
client_key = config["client_key"]
client_secret = config["client_secret"]
token = config["token"]
token_secret = config["token_secret"]

#setup authentication
oauth = OAuth1(client_key,client_secret,token,token_secret)

#Twitter Request
def send_request(screen_name,rel_type,next_cursor=None):
    url = "https://api.twitter.com/1.1/%s/ids.json?screen_name=%s&count=5000" % (rel_type,screen_name)

    if next_cursor is not None:
        url += "&cursor=%s" % next_cursor

    response = requests.get(url,auth=oauth)

    #Wait to fix request limit
    time.sleep(4)

    if response.status_code == 200:
        result = json.loads(response.content)
        return result
    else:
        print "[-] Connection Failed Waiting 15 Minutes To Retry"
        time.sleep(900)
        url = "https://api.twitter.com/1.1/%s/ids.json?screen_name=%s&count=5000" % (rel_type,screen_name)

        if next_cursor is not None:
            url += "&cursor=%s" % next_cursor

        response = requests.get(url,auth=oauth)

        if response.status_code == 200:
            result = json.loads(response.content)
            return result
        else:
            print "[-] Connection Failed"
            print "[-] Check Network Connection or Authorization Tokens"
            return None

#users that the user follows
def get_user_friend_list(screen_name):
    print "Screen Name Called: " + screen_name
    friend_list = []
    next_cursor = None

    #Init Request
    friends = send_request(screen_name,"friends")

    #If data is returned start collection loop
    if friends is not None:
        friend_list.extend(friends["ids"])
        print "[*] Download %d friends" % len(friend_list)

        #while we have a valid cursor value download friends
        while friends["next_cursor"] != 0 and friends["next_cursor"] != -1:
            friends = send_request(screen_name,"friends",friends["next_cursor"])

            if friends is not None:
                friend_list.extend(friends["ids"])
                print "[*] Download %d friends" % len(friend_list)
            else:
                break

        return friend_list

#users that follow user
def get_user_follower_list(screen_name):
    follower_list = []
    next_cursor = None

    #Init Request
    followers = send_request(screen_name,"followers")

    #If data is returned start collection loop
    if followers is not None:
        follower_list.extend(followers["ids"])
        print "[*] Download %d followers" % len(follower_list)

        #while we have a valid cursor value download followers
        while followers["next_cursor"] != 0 and followers["next_cursor"] != -1:
            followers = send_request(screen_name,"followers",followers["next_cursor"])

            if followers is not None:
                follower_list.extend(followers["ids"])
                print "[*] Download %d followers" % len(follower_list)
            else:
                break

        return follower_list

def get_user_info_from_id(user_id):
    print "[+] Getting User Info"
    url = "https://api.twitter.com/1.1/users/lookup.json?user_id=%s" % user_id
    response = requests.get(url, auth=oauth)
    if response.status_code == 200:
        return json.loads(response.content)
    else:
        print "[-] Connection Failed Waiting 15 Minutes"
        time.sleep(900)
        response = requests.get(url, auth=oauth)
        if response.status_code == 200:
            return json.loads(response.content)
        else:
            print "[-] Check Network Connection or Authorization Tokens"
            return None


def save_data(data):
    f = open("Twitter_Crawler_" + time.strftime("%d-%m-%Y") + ".json","w")
    f.write(data)
    f.close()

def process_ids(ids):
    result = []
    for item in ids:
        temp = get_user_info_from_id(item)
        time.sleep(4)
        result.extend([temp[0]["screen_name"]])
    return result

def is_numeric(value):
    try:
        float(value)
        return True
    except:
        return False

def check_user(degree,data,endpoint):
    print "[+] Called Degree %d" % degree
    if degree <= 0:
        return data
    else:
        for user in data:
            name = get_user_info_from_id(user)[0]["screen_name"]
            if name not in endpoint:
                print "Screen_name: " + name
                temp = check_user(degree -1,get_user_friend_list(name),endpoint)
                if temp is not None:
                    endpoint[name] = temp
                else:
                    endpoint[name] = []

def main():
    print "[+] Starting Twitter Crawler Bot"
    user_input = ""
    while True:
        print "[*] Please Input Degree Limit"
        user_input = raw_input(">> ")
        if is_numeric(user_input):
            break
        else:
            print "[-] Must Be Integer"

    degree = int(user_input)

    user_input = ""
    while user_input == "":
        print "[*] Please Input Starting Node Screen Name"
        user_input = raw_input(">> ")

    init_list = get_user_friend_list(user_input)
    network_list = {}
    network_list[user_input] = init_list
    try:
        check_user(degree,init_list,network_list)
    except KeyboardInterrupt:
        print "[-] Program Interrupted Dumping Data"

    for user in network_list:
        network_list[user] = process_ids(network_list[user])

    save_data(json.dumps(network_list))
    print "[+] Data Saved"

if __name__ == "__main__":
    main()
