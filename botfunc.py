import asyncio
import json
import sys

import aiomysql
import portalocker
import redis
import requests_cache
import yaml
from loguru import logger

print ("Initializing data...")
def safe_file_read(filename: str, encode: str = "UTF-8", mode: str = "r") -> str or bytes:
    if mode == 'r':
        with open(filename, mode, encoding=encode) as file:
            portalocker.lock(file, portalocker.LOCK_EX)
            tmp = file.read()
            portalocker.unlock(file)
    else:
        with open(filename, mode) as file:
            portalocker.lock(file, portalocker.LOCK_EX)
            tmp = file.read()
            portalocker.unlock(file)

    return tmp


def safe_file_write(filename: str, s, mode: str = "w", encode: str = "UTF-8"):
    if 'b' not in mode:
        with open(filename, mode, encoding=encode) as file:
            portalocker.lock(file, portalocker.LOCK_EX)
            file.write(s)
            portalocker.unlock(file)
    else:
        with open(filename, mode) as file:
            portalocker.lock(file, portalocker.LOCK_EX)
            file.write(s)
            portalocker.unlock(file)


loop = asyncio.get_event_loop()
config_yaml = yaml.safe_load(open('config.yaml', 'r', encoding='UTF-8'))
try:
    cloud_config_json = json.load(open('cloud.json', 'r', encoding='UTF-8'))
except FileNotFoundError:
    safe_file_write('cloud.json', """{
    "QCloud_Secret_id": "",  # QCloud用户ID，可留空
    "QCloud_Secret_key": "", # QCloud密钥ID，可留空
    "MySQL_User": "" # 你的MySQL用户
    "MySQL_Pwd": "", # 你的MySQL密码
    "MySQL_Port": 3306, # 你的MySQL端口，一般都是3306，如果是其他的需要修改
    "MySQL_Host": "localhost", # MySQL主机
    "MySQL_db": "", # MySQL数据库名称
    "Redis_Host": "localhost", # Redis主机
    "Redis_port": 6379  # Redis主机端口，一般都是6379
  }
# 最后配置完后，请把所有的注释和#全部删除，避免发生错误（包括本条)""")
    logger.error(
        'cloud.json 未创建，程序已自动创建，请参考 https://github.com/daizihan233/KuoHuBit/issues/17 填写该文件的内容')
    sys.exit(1)
try:
    dyn_yaml = yaml.safe_load(open('dynamic_config.yaml', 'r', encoding='UTF-8'))
except FileNotFoundError:
    safe_file_write('dynamic_config.yaml', """mute:
- none
word:
- none""")
    logger.warning('dynamic_config.yaml 已被程序自动创建')
    dyn_yaml = yaml.safe_load(open('dynamic_config.yaml', 'r', encoding='UTF-8'))
try:
    emma_khapi_yaml = yaml.safe_load(open('yamls/khapi.yml', 'r', encoding='UTF-8'))
except FileNotFoundError:
    safe_file_write('yamls/khapi.yml', """# This file is generated by OpenLightBit
# Address can connect to khapi
khbit-api-ip: 0.0.0.0
# Port can connect to khapi
khbit-api-port: 8989""")
    logger.success('./yamls/khapi.yml 已被程序自动创建')
    emma_khapi_yaml = yaml.safe_load(open('./yamls/khapi.yml', 'r', encoding='UTF-8'))

def get_config(name: str):
    try:
        return config_yaml[name]
    except KeyError:
        logger.error(f'{name} 在配置文件中找不到')
        return None


def get_cloud_config(name: str):
    try:
        return cloud_config_json[name]
    except KeyError:
        logger.error(f'{name} 在配置文件中找不到')
        return None


def get_dyn_config(name: str):
    try:
        return dyn_yaml[name]
    except KeyError:
        logger.error(f'{name} 在配置文件中找不到')
        return None


async def select_fetchone(sql, arg=None):
    conn = await aiomysql.connect(host=get_cloud_config('MySQL_Host'),
                                  port=get_cloud_config('MySQL_Port'),
                                  user=get_cloud_config('MySQL_User'),
                                  password=get_cloud_config('MySQL_Pwd'), charset='utf8mb4',
                                  db=get_cloud_config('MySQL_db'), loop=loop)

    cur = await conn.cursor()
    if arg:
        await cur.execute(sql, arg)
    else:
        await cur.execute(sql)
    result = await cur.fetchone()
    await cur.close()
    conn.close()
    return result


async def select_fetchall(sql, arg=None):
    conn = await aiomysql.connect(host=get_cloud_config('MySQL_Host'),
                                  port=get_cloud_config('MySQL_Port'),
                                  user=get_cloud_config('MySQL_User'),
                                  password=get_cloud_config('MySQL_Pwd'), charset='utf8mb4',
                                  db=get_cloud_config('MySQL_db'), loop=loop)

    cur = await conn.cursor()
    if arg:
        await cur.execute(sql, arg)
    else:
        await cur.execute(sql)
    result = await cur.fetchall()
    await cur.close()
    conn.close()
    return result


async def run_sql(sql, arg):
    conn = await aiomysql.connect(host=get_cloud_config('MySQL_Host'),
                                  port=get_cloud_config('MySQL_Port'),
                                  user=get_cloud_config('MySQL_User'),
                                  password=get_cloud_config('MySQL_Pwd'), charset='utf8mb4',
                                  db=get_cloud_config('MySQL_db'), loop=loop)

    cur = await conn.cursor()
    await cur.execute(sql, arg)
    await cur.execute("commit")
    await cur.close()
    conn.close()


async def get_all_admin() -> list:
    tmp = await select_fetchall("SELECT uid FROM admin")
    t = []
    for i in tmp:
        t.append(i[0])
    logger.debug(t)
    return list(t)


async def get_all_sb() -> list:
    tmp = await select_fetchall('SELECT uid FROM blacklist')
    t = []
    for i in tmp:
        t.append(i[0])
    return t


backend = requests_cache.RedisCache(host=get_cloud_config('Redis_Host'), port=get_cloud_config('Redis_port'))
session = requests_cache.CachedSession("global_session", backend=backend, expire_after=360)

p = redis.ConnectionPool(host=get_cloud_config('Redis_Host'), port=get_cloud_config('Redis_port'))
r = redis.Redis(connection_pool=p, decode_responses=True)
