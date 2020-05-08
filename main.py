import requests
import random
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
import pytz

timez = pytz.timezone('Asia/Shanghai')
logging.basicConfig(filename='out.log', level=logging.INFO)

knames = [
    "bh", "xykh", "twfw", "sfzx", "sfgl", "szsf", "szds", "szxq", "sfcg",
    "cgdd", "gldd", "jzyy", "bllb", "sfjctr", "jcrysm", "xgjcjlsj", "xgjcjldd",
    "xgjcjlsm", "zcwd", "zwwd", "wswd", "sbr", "sjd"
]
persons_id = [220170918811, 220170918911, 220170918711, 220170918721, 220170918421, 220170919001]

sched = BlockingScheduler(timezone=timez)

@sched.scheduled_job('cron', id='my_job', hour='6,10,18', minute=40)
def job():
    for single_id in persons_id:
        p = requests.post("http://202.201.13.180:9037/encryption/getMD5",
                        data={'cardId': single_id})
        if p.json()['code'] != 1:
            logging.warning(str(single_id) + "getMD5 failed")
            continue
        r = requests.post("http://202.201.13.180:9037/grtbMrsb/getInfo",
                        data={
                            'cardId': single_id,
                            'md5': p.json()['data']
                        })
        data = r.json()
        if data['code'] != 1:
            logging.warning(str(single_id) + "getInfo failed")
            continue
        data = data['data']
        data.update(data['list'][0])
        data.pop('list')
        # if data['zcwd'] == 0.0:
        logging.info(data)
        data['zcwd'] = random.randrange(360, 369) / 10
        data['zwwd'] = random.randrange(360, 369) / 10
        data['wswd'] = random.randrange(360, 369) / 10
        ndata = {key : value for key, value in data.items() if key in knames}
        logging.info(ndata)
        f = requests.post("http://202.201.13.180:9037/grtbMrsb/submit", data=ndata)
        # print(f.json())
        if f.json()['code'] != 1:
            logging.warning(f.json())
            # print(str(single_id) + "submit failed")
            continue
        else:
            logging.info(f.json())

sched.start()