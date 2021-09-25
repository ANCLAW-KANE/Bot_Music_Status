from vk_api import VkApi, vk_api
from vk_api.bot_longpoll import VkBotEventType , VkBotLongPoll
import time , sqlite3 , re
from  threading import Thread

#def captcha_handler(captcha):
#    key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()
#    return captcha.try_again(key)
triggerCode = False
vk_session: VkApi = vk_api.VkApi(token="18ae9b6d3a66e7d5d1ca36aca453ebffb02de8449c71f871aa1bf6faff7a021eed9416b3e867c1bafe8c3")
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session,206973016)

def get_audio():
    global triggerCode
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
                if TEXT == "/delete":
                    edit.execute("DELETE FROM users where userid = ?", (event.object.message['peer_id'],))
                    BD.commit()
                if TEXT == "/restart":
                    triggerCode = True
                    exit()
                if TEXT == '/help':
                    vk.messages.send(random_id=0, message=f"Команды автостатуса:\n /set-audio токен + ваше аудиовложение\n"
                                                          f"пример: \n/set-audio 1aae9b6d....7c1сafe821\n"
                                                          f"Токен можете взять с сайта >> https://vkhost.github.io/ << \n"
                                                          f"Выберите *Настройки* , в верхней части *Пользователь*\n"
                                                          f"Выберите опции *Статус*, *Доступ в любое время*\n"
                                                          f"И нажмите *Получить* в самом внизу , после на новой странце "
                                                          f"*Разрешить* \nИ в адресной строке скопируйте ключ как с примера (ваш будет другой )"
                                                          f"после access_token= до &expires\n\n"
                                                          f"/мой токен\n"
                                                          f"Команда работает только в лс и гапоминает ваш токен\n"
                                                          f"Удобно при смене аудио, так как не нужно брать новый\n\n"
                                                          f"/delete\n"
                                                          f"Удаляет вас из базы автостатуса\n\n"
							  f"/restart\n Перезагрузка, если установка аудио не срабатывает",peer_id=event.object.message['peer_id'])

def set_audio():
    global triggerCode
    timing = time.time()
    while True:
        if time.time() - timing > 120.0:
            timing = time.time()
            BD = sqlite3.connect('audio.db')
            edit = BD.cursor()
            edit.execute("SELECT * FROM users")
            for data in edit.fetchall():
                try:
                    Vk: VkApi = vk_api.VkApi(token=data[1])
                    vk_audio = Vk.get_api()
                    vk_audio.audio.setBroadcast(audio=data[2])
                except:
                    vk.messages.send(random_id=0, message=f"Невалидная запись:\n {data}", peer_id=388145277)
        time.sleep(1)
        if triggerCode: exit()


Get = Thread(target=get_audio,args=())
Get.start()
SetA = Thread(target=set_audio, args=())
SetA.start()



