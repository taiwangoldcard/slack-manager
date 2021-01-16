import os, time
from slack_sdk import WebClient

cleaner_config = [
    {
        "channel_name"          : "#line",
        "channel_id"            : "C01GPGFS61H",
        "max_messages_allowed"  : 100
    },
    {
        "channel_name"          : "#website-devops",
        "channel_id"            : "C01AS4EGA3E",
        "max_messages_allowed"  : 50
    },
    # {
    #     "channel_name"          : "#faq",
    #     "channel_id"            : "C01E9KCCZUY",
    #     "max_messages_allowed"  : 300
    # },
]

client = WebClient(token=os.environ['SLACK_OAUTH_ACCESS_TOKEN'])

def _deleteLineHistory(channel_id, channel_name, max):
    #set limit to 1000 so I don't have to handle pagination - will not work well if history  > 1000
    response = client.conversations_history(channel=channel_id, limit=1000)
    num_messages = len(response['messages'])
    print("[" + channel_name +"] There is " + str(num_messages) + " messages")
    if num_messages > max:
        print("There is too many messages, let's clean that up")
        # iterate from the first message
        for chat in reversed(response['messages']):
            if num_messages > max:
                # if threaded message 
                if 'thread_ts' in chat:
                    thread = client.conversations_replies(ts=chat['thread_ts'], channel=channel_id)

                    # delete all replies to the thread and the thread itself
                    for reply in thread['messages']:
                        if "hidden" not in reply:
                            print("[" + channel_name +"] [deleting thread replies]: " + str(reply['text']))
                            client.chat_delete(channel=channel_id, ts=reply["ts"])
                            time.sleep(1)

                    num_messages = num_messages - 1
                    continue

                print("[" + channel_name +"] [deleting]: " + str(chat['text']))
                client.chat_delete(channel=channel_id, ts=chat["ts"])
                time.sleep(1)
                num_messages = num_messages - 1



def listChannels():
    response = client.conversations_list()
    conversations = response["channels"]
    for conversation in conversations:
        print(conversation['name'] + " " + conversation['purpose']['value'])
        print(conversation['num_members'])


for channel in cleaner_config:
    _deleteLineHistory(channel['channel_id'], channel['channel_name'] , channel['max_messages_allowed'])
