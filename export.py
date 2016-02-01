#!/usr/bin/python
import json
import sys
sys.dont_write_bytecode = True
import database

def main():
    print "[+] Starting Twitter Crawler Export Tool"
    result = []
    user_list = database.get_users()
    for user in user_list:
        print "[+] Proccessing User: %s" % user

        try:
            friends = database.get_friends(user)
        except:
            print "[-] Error No Friend Data Found For %s Omitting" % user
            friends = []

        try:
            followers = database.get_followers(user)
        except:
            print "[-] Error No Follower Data Found For %s Omitting" % user
            followers = []

        result.append({"screen_name": user, "friends": friends, "followers": followers})

    file = open("export.json", "w")
    file.write(json.dumps(result))
    file.close()
    print "[+] Success Data Saved As export.json"

if __name__ == "__main__":
    main()
