import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

token = '60862f3243f359ace66938d48e75f0942e9122c653732b64defbb101c3d6fa7f7a4568acaed9766723587'
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)

class Interface:
    def __init__(self):
        pass

def send_msg(user_id, random_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, "random_id": random_id})


def main():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                try:
                    send_msg(event.user_id, event.random_id, event.text)
                except (KeyError, TypeError) as e:
                    print(e)

if __name__ == '__main__':
    main()