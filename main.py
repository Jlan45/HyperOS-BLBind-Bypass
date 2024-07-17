import base64
import hashlib
import hmac
import json
import re
from time import sleep
import requests
import adbutils
from Crypto.Cipher import AES
useGloablApi=False
globalApi="https://unlock.update.intl.miui.com/v1/"
localApi="https://unlock.update.miui.com/v1/"
apiUrl=globalApi if useGloablApi else localApi
print(apiUrl)
def decryptData(data):
    data_pass = b"20nr1aobv2xi8ax4"
    data_iv = b"0102030405060708"
    aesObj=AES.new(data_pass,AES.MODE_CBC,iv=data_iv)
    plaindata=aesObj.decrypt(data).decode()
    return plaindata
def signData(data):
    sign_key = "10f29ff413c89c8de02349cb3eb9a5f510f29ff413c89c8de02349cb3eb9a5f5"
    sign_data = "POST\n/v1/unlock/applyBind\ndata="+data+"&sid=miui_sec_android"
    hmac_obj = hmac.new(sign_key.encode(), sign_data.encode(), hashlib.sha1)
    sign = hmac_obj.hexdigest()
    return sign
adbConn=adbutils.AdbClient()
device=""
for i in adbConn.device_list():
    device=i
    break
if device=="":
    print("未找到设备")
    exit()
device.logcat("logcat.txt", clear=True,command="logcat *:S CloudDeviceStatus:V")

print("等待请求中。。。")
header=''
arg=''
while(True):
    sleep(1)
    logContent=open("logcat.txt","r").read()
    # print(logContent)
    args=re.findall(r"args: (.*?)\n",logContent)
    headers=re.findall(r"headers: (.*?)\n",logContent)
    try:
        header=headers[0]
        arg=args[0]
    except:
        continue
    break
print("已获取请求，正在处理。。。")
argd=decryptData(base64.b64decode(arg))
argd=argd[argd.find("{"):argd.rfind("}")+1]
argsData=json.loads(argd)
headerd=decryptData(base64.b64decode(header))
# print(argsData)
argsData["rom_version"]=argsData["rom_version"].replace("V816", "V14")
argsJson=json.dumps(argsData)
sign=signData(argsJson)
cookie=re.findall(r"Cookie=\[(.*)\]",headerd)[0]
resp=requests.post(apiUrl+"unlock/applyBind",data={"data":argsJson,"sid":"miui_sec_android","sign":sign},headers={"Cookie":cookie,"Content-Type":"application/x-www-form-urlencoded"})
if resp.json()["description"]=="成功":
    print("绑定成功")