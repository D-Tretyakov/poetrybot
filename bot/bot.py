import json
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from random import choice
vk_session = vk_api.VkApi(token='f94737fb6f18c082f839ba01674e08c15109a320a4b5666e65b98adbe5c78648dffbef791e37489f426be')

texts = ["текст 0", "текст 1", "текст 2"]
commands = ["начать", "выбрать текст", "хорошая рифма", "плохая рифма", "вернуться к выбору текста"]
menu = texts + commands
smiles = ["😎", "🙃", "😁", "😐", "🤔", "🤫", "😏", "🤓", "🤠", "😳", "😬", "😕", "🤗", "🤨"]


def update_data(dic, name_of_file):
    with open(name_of_file, 'w', encoding="utf8") as f:
        f.write(json.dumps(dic, ensure_ascii=False))
        f.close()


i = 0
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()
users_data = json.loads(open("users_data.json", encoding="utf8").read())
rhymes = json.loads(open("rhymes.json", encoding="utf8").read())
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        ev_text = event.text.lower()
        if ev_text == "начать":
            mes = "Добро пожаловать..."
            vk.messages.send(user_id=event.user_id, message=mes, random_id=0,
                             keyboard=open("keyboard_texts.json", "r", encoding="utf8").read())
        elif texts.count(ev_text) != 0:
            mes = "Введите строчку"
            vk.messages.send(user_id=event.user_id, message=mes, random_id=0,
                             keyboard=open("keyboard_back.json", "r", encoding="utf8").read())
            users_data[str(event.user_id)] = {"theme": event.text, "last rhyme": None}
            update_data(users_data, 'users_data.json')
        elif menu.count(ev_text) == 0 and event.text != "":
            if list(users_data.keys()).count(str(event.user_id)) != 0 and\
                    users_data[str(event.user_id)]["theme"] is not None:
                mes = "*рифма " + str(i) + "*"
                i += 1
                users_data[str(event.user_id)]["last rhyme"] = [event.text, mes, None]
                if event.text in rhymes.keys() and mes in rhymes[event.text].keys():
                    rhymes[event.text][mes]["nan"] += 1
                else:
                    rhymes[event.text] = {mes: {"nan": 1, "+": 0, "-": 0}}
                update_data(users_data, "users_data.json")
                update_data(rhymes, "rhymes.json")
                vk.messages.send(user_id=event.user_id, message=mes, random_id=0,
                                 keyboard=open("keyboard_rate.json", "r", encoding="utf8").read())
            else:
                mes = "Нужно выбрать текст"
                vk.messages.send(user_id=event.user_id, message=mes, random_id=0)
        elif ev_text == "вернуться к выбору текста":
            mes = "Выберите текст"
            vk.messages.send(user_id=event.user_id, message=mes, random_id=0,
                             keyboard=open("keyboard_texts.json", "r", encoding="utf8").read())
            users_data[str(event.user_id)] = {"theme": None, "last rhyme": None}
            update_data(users_data, 'users_data.json')
        elif ev_text == "хорошая рифма" or ev_text == "плохая рифма":
            adr = users_data[str(event.user_id)]["last rhyme"]
            if adr:
                mes = "Спасибо за отзыв!\nВведите строчку"
                rhymes[adr[0]][adr[1]]["nan"] -= 1
                if ev_text == "хорошая рифма":
                    users_data[str(event.user_id)]["last rhyme"] = None
                    rhymes[adr[0]][adr[1]]["+"] += 1
                elif ev_text == "плохая рифма":
                    users_data[str(event.user_id)]["last rhyme"] = None
                    rhymes[adr[0]][adr[1]]["-"] += 1
                vk.messages.send(user_id=event.user_id, message=mes, random_id=0,
                                 keyboard=open("keyboard_back.json", "r", encoding="utf8").read())
                update_data(users_data, "users_data.json")
                update_data(rhymes, "rhymes.json")
            else:
                vk.messages.send(user_id=event.user_id, message="Ошибка", random_id=0,
                                 keyboard=open("keyboard_back.json", "r", encoding="utf8").read())
        elif event.text == "":
            vk.messages.send(user_id=event.user_id, message=choice(smiles), random_id=0)
            vk.messages.send(user_id=event.user_id, message="Давай ближе к делу🤨.", random_id=0)
