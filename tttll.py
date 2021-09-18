from vk_api import VkApi, vk_api
from vk_api.bot_longpoll import VkBotEventType , VkBotLongPoll
import time , sqlite3 , re
from  threading import Thread

vk_session: VkApi = vk_api.VkApi(token="")
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session,#id_группы)

def get_audio():
    BD = sqlite3.connect('audio.db')
    edit = BD.cursor()
    edit.execute("""CREATE TABLE IF NOT EXISTS users( userid INT PRIMARY KEY, token TEXT, audio_id TEXT); """)
    BD.commit()
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if 0 < int(event.object.message['peer_id']) < 2000000000:
                TEXT = event.object.message['text']
                TEXTSplit = str(TEXT).split(sep=' ')
                OBJ = event.object.message
                if TEXTSplit[0] == '/set-audio' and TEXTSplit[1] == re.findall("[0-9a-f]{85}",TEXTSplit[1])[0] and OBJ.get('attachments',False):
                    audio = OBJ['attachments'][0]['audio']
                    audio_id = str(audio['owner_id']) + "_" + str(audio['id'])
                    print(event.object.message['peer_id'], " ::: ",audio_id)
                    try:
                        data = (event.object.message['peer_id'], TEXTSplit[1], audio_id)
                        edit.execute("INSERT INTO users VALUES(?, ?, ?)",data)
                    except:
                        data = (TEXTSplit[1],audio_id,event.object.message['peer_id'])
                        edit.execute("UPDATE users SET token = ?, audio_id = ? where userid = ?",data)
                    BD.commit()
                if TEXT == "/мой токен":
                    token = edit.execute("SELECT token FROM users where userid = ?",(event.object.message['peer_id'],))
                    vk.messages.send(random_id=0,message=token,peer_id = event.object.message['peer_id'])

def set_audio():
    timing = time.time()
    while True:
        if time.time() - timing > 120.0:
            timing = time.time()
            BD = sqlite3.connect('audio.db')
            edit = BD.cursor()
            edit.execute("SELECT * FROM users")
            for data in edit.fetchall():
                try:
                    print(data)
                    Vk: VkApi = vk_api.VkApi(token=data[1])
                    vk_audio = Vk.get_api()
                    vk_audio.audio.setBroadcast(audio=data[2])
                except:
                    vk.messages.send(random_id=0, message=f"Невалидная запись:\n {data}", peer_id=#peer_id)
        time.sleep(1)

if __name__ == '__main__':
    Get = Thread(target=get_audio,args=())
    Get.start()
    SetA = Thread(target=set_audio, args=())
    SetA.start()
    if not Get.join(): exit()
    if not SetA.join(): exit()
