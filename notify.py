import json
import requests
import datetime

def notify_info(user_id: int | str) -> bool:
    user_id = str(user_id)

    with open("json_users_db.json", "r") as f:
        data = json.load(f)
        for user in data:
            if user['tg_id'] == user_id:
                return user['notify']
            
def notify_swith(user_id: int | str):
    user_id = str(user_id)

    with open("json_users_db.json", "r+") as f:
        data = json.load(f)
        for user in data:
            if user['tg_id'] == user_id:
                user['notify'] = not user['notify']
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

def update_marks() -> str:
    msg_text = 'Новые(-ая) оценки(-ка):\n'
    new_marks = []
    with open("json_users_db.json", "r+", encoding='UTF-8') as f:
        data = json.load(f)
        for user in data:
            if user['notify']:
                cookie = user['cookie']
                url = 'https://es.ciur.ru/api/MarkService/GetSummaryMarks?date='+str(datetime.datetime.now().date())
                headers = {'Cookie':cookie}

                post = requests.post(url, headers=headers)
                b = json.loads(post.text )

                for subject in b['discipline_marks']:
                    marks = ''
                    g = subject['discipline'].replace('Иностранный язык (английский)', 'Англ. Яз.').replace('Физическая культура', 'Физ-ра').replace('Литература', 'Литер.').replace('Технология', 'Техн.').replace('Информатика', 'Информ.').replace('Обществознание', 'Обществ.').replace('Русский язык', 'Рус. Яз.').replace('Математика', 'Матем.')
                    while len(g) < 9:
                        g += ' '
                    for i in subject['marks']:
                        marks += f"{i['mark']} "
                        if float(subject['average_mark']) >= 4.5:
                            color_mark = '🟩'
                        else:
                            color_mark = '🟨'
                                
                    new_marks.append(f"{color_mark} {g}│ {subject['average_mark']} │ {marks}\n")

                for item_num in range(len(new_marks)):
                    try:
                        if new_marks[item_num] != user['marks'][item_num]:
                            msg_text += f'++{new_marks[item_num]}'
                    except IndexError:
                        msg_text += f'++{new_marks[item_num]}'

                user['marks'] = new_marks
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()

                print(msg_text)
                return user['tg_id'], msg_text