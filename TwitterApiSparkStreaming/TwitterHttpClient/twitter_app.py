import socket
import sys
import requests
import json
import filtered_stream as tweet_api


def send_tweets_to_spark(http_resp, tcp_connection):
    for line in http_resp.iter_lines():
        try:
            full_tweet = json.loads(line).get("data")
            tweet_text = full_tweet.get('text') + "\n"
            tweet_text = tweet_text.encode("utf-8")
            print ("------------------------------------------\n")
            print (tweet_text)
            print ("------------------------------------------\n")
            tcp_connection.send(tweet_text)
        except:
            e = sys.exc_info()[0]
            print("ERROR in STREAM: %s" % e)
            print("ERROR in STREAM: %s" % sys.exc_info()[1])


def get_tweets():

    rules = tweet_api.get_rules()
    delete = tweet_api.delete_all_rules(rules)
    rules_set = tweet_api.set_rules(delete)
    response = tweet_api.get_stream(rules_set)

    return response



TCP_IP = "localhost"
TCP_PORT = 9999
conn = None
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
print("Waiting for TCP connection...")
conn, addr = s.accept()
print("Connected... Starting getting tweets.")
data = get_tweets()
send_tweets_to_spark(data,conn)




