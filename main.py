import requests
import random
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
import pytz
import yaml
import time

timez = pytz.timezone('Asia/Shanghai')

sched = BlockingScheduler(timezone=timez)

t = 1

@sched.scheduled_job('cron', id='my_job', hour='6,10,18', minute=40)
def job():
    with open("config.yaml", 'r') as f:
        config = yaml.load(f.read(), Loader=yaml.SafeLoader)
    logging.basicConfig(filename=config['logger_file'], level=logging.INFO)
    for single_id in config['users_id']:
        # print(single_id)
        p = requests.post("http://202.201.13.180:9037/encryption/getMD5",
                          data={'cardId': single_id})
        while p.json()['message'] != '成功':
            time.sleep(t)
            logging.warning( p.json())
            logging.warning(str(single_id) + "getMD5 failed")
            p = requests.post("http://202.201.13.180:9037/encryption/getMD5",
                          data={'cardId': single_id})
            # continue
        r = requests.post("http://202.201.13.180:9037/grtbMrsb/getInfo",
                          data={
                              'cardId': single_id,
                              'md5': p.json()['data']
                          })
        data = r.json()
        # print(data)
        while data['message'] != '成功':
            time.sleep(t)
            logging.warning( r.json())
            logging.warning(str(single_id) + "getInfo failed")
            r = requests.post("http://202.201.13.180:9037/grtbMrsb/getInfo",
                          data={
                              'cardId': single_id,
                              'md5': p.json()['data']
                          })
            data = r.json()
            # continue
        data = data['data']
        data.update(data['list'][0])
        data.pop('list')
        # if data['zcwd'] == 0.0:
        logging.info(data)
        data['zcwd'] = random.randrange(360, 369) / 10
        data['zwwd'] = random.randrange(360, 369) / 10
        data['wswd'] = random.randrange(360, 369) / 10
        ndata = {
            key: value
            for key, value in data.items() if key in config['knames']
        }
        logging.info(ndata)
        f = requests.post("http://202.201.13.180:9037/grtbMrsb/submit",
                          data=ndata)
        # print(f.json())
        while f.json()['message'] != '成功':
            time.sleep(t)
            logging.warning(f.json())
            f = requests.post("http://202.201.13.180:9037/grtbMrsb/submit",
                          data=ndata)
            # print(str(single_id) + "submit failed")
            # continue
        else:
            logging.info(f.json())
        # time.sleep(t)


job()
sched.start()