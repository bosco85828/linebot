from curses.ascii import isdigit
from enum import Enum
import os 
from flask import Flask, request, abort
import re
import json
from key import key


from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageSendMessage,
)
import random
import gspread
import pandas as pd 
from oauth2client.service_account import ServiceAccountCredentials

apikey=key()

app = Flask(__name__)

line_bot_api = LineBotApi(apikey.api)
handler = WebhookHandler(apikey.line)
path=os.path.dirname(os.path.abspath(__file__))
def gsheet2(value):
    scopes = ["https://spreadsheets.google.com/feeds"]
 
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "{}/credentials.json".format(path), scopes)

    client = gspread.authorize(credentials)

    sheet = client.open_by_key(
            apikey.gsheet).get_worksheet(1)
    
    sheet.append_row(value)

def getsheet2(key):
    scopes = ["https://spreadsheets.google.com/feeds"]
 
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "{}/credentials.json".format(path), scopes)

    client = gspread.authorize(credentials)

    sheet = client.open_by_key(
            apikey.gsheet).get_worksheet(1)
    data=sheet.get_all_records()
    data=pd.DataFrame(data)
    data.columns=['msgID','text']
    limit=data['msgID'] != ""
    data=data[limit]
    condition = data['msgID'] == int(key)
    msg = data[condition]['text']
    msg = msg.to_dict().values()
    msg = list(msg)[0]

    return msg

    

def gsheet(value):
    scopes = ["https://spreadsheets.google.com/feeds"]
 
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "{}/credentials.json".format(path), scopes)

    client = gspread.authorize(credentials)

    sheet = client.open_by_key(
            apikey.gsheet).sheet1
    if value == 'delete' :
        sheet.clear()
    # elif value == "index":
    #     sheet.insert_row(value)
    else :    
        sheet.append_row(value)

def getsheet(key):
    scopes = ["https://spreadsheets.google.com/feeds"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
    "{}/credentials.json".format(path), scopes)

    client = gspread.authorize(credentials)

    sheet = client.open_by_key(
        apikey.gsheet).sheet1
    data=sheet.get_all_records()
    data=pd.DataFrame(data)
    limit=data['Name'] != ""
    data=data[limit]
    if ">" in key  :        
            
        key=str(key).replace(">","")
        condition=data['Value'] > int(key)
        result=data[condition]

    elif "<" in key : 
                
        key=str(key).replace("<","")
        condition=data['Value'] < int(key)
        result=data[condition]

    else:
        name = data['Name']
        condition = data['Name'].str.contains(key)
        result=data[condition]
        sum=data[condition]['Value'].sum()
        if type(sum) == int:
            report = f"""
{result}
==================
???????????? : {sum}
                    """
        else : 
            report = result
        
 
    return report
    
def delsheet(key):
    scopes = ["https://spreadsheets.google.com/feeds"]
 
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "{}/credentials.json".format(path), scopes)

    client = gspread.authorize(credentials)

    sheet = client.open_by_key(
            apikey.gsheet).sheet1
    
    location=sheet.findall(key)
    for a in location : 
        llist=str(a).split(' ')
        num=str(llist[1]).rfind('C')
        dlist=sheet.range('A{}:Z{}'.format(llist[1][1:num],llist[1][1:num]))
        for d in dlist:
            d.value = ""
        sheet.update_cells(dlist)

@app.route("/callback", methods=['POST'])
def callback():
    global data
    global data_type
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    data = json.loads(body)
    data_type = data['events'][0]['type']
    app.logger.info("Request body: " + body)
    print(data)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    try : 
        if data_type == 'unsend' : 

            
            msgID = data['events'][0]['unsend']['messageId']
            groupID = data['events'][0]['source']['groupId']
            userID = data['events'][0]['source']['userId']
            
            usermsg = getsheet2(msgID)
            profile = line_bot_api.get_profile(userID)
            profile = json.loads(str(profile)) 
            userName = profile['displayName']
            msg = f'{userName}????????????:{usermsg}'
            line_bot_api.push_message(groupID, TextSendMessage(text=msg))

        elif data_type == 'message' :
            usermsg = data['events'][0]['message']['text']
            msgID = data['events'][0]['message']['id']
            msglist = [msgID,usermsg]
            gsheet2(msglist)
        
        return 'OK'
    except:
        return 'OK'

    


@app.route("/",methods=['get'])
def index():
    print('Welcome')
    return 'success'

def sendimg(event,msgurl):
    line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(
                    original_content_url=msgurl,
                    preview_image_url=msgurl))
def sendtext(event,msg):
    line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=msg))



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(event)
    msg_text= event.message.text
    msg_type= event.type
    


    if re.search(r'^write.*$',msg_text):
        vlist=msg_text.split(',')
        gsheet(vlist[1:])
        sendtext(event,'append success')
    elif msg_text == "clear":
        gsheet('delete')
        sendtext(event,'clear success')

    elif re.search(r'^search.*$',msg_text):
        vlist=msg_text.split(',')
        text=str(getsheet(vlist[1]))

        sendtext(event,text)
    
    elif re.search(r'^delete.*$',msg_text):
        vlist=msg_text.split(',')
        delsheet(vlist[1])
        sendtext(event,'delete success')
    
    elif msg_text =="??????":
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="""
                ???????????????06/30
                ?????????05/05
                ?????????06/09
                ?????????06/18
                ?????????09/04
                ?????????08/28
                ?????????12/05
                P?????????03/18
                ????????????11/10
                """))# TextSendMessage(text=event.message.text))
    
    elif msg_text == "!????????????" : 
            lowest=0
            highest=100 
            count=os.path.getsize("{}/answer.txt".format(path))
            count2=os.path.getsize("{}/range.txt".format(path))
            with open('{}/answer.txt'.format(path),'a+') as anser :
                anser.seek(0)
                # print(anser.read())
                if count == 0 :
                    anser.write(str(random.randint(lowest+1,highest-1)))
                    with open('{}/range.txt'.format(path),'a+') as range : 
                        range.seek(0)
                        if count2 == 0 : 
                            range.write("{},{}\n".format(lowest,highest))
                        else :
                            # print('?????????????????????')
                            sendtext(event,'?????????????????????')
                            os._exit()
                        range.close()
                    # print('??????????????????')
                    sendtext(event,'??????????????????')
                else : 
                    # print('?????????????????????')
                    sendtext(event,'?????????????????????')
                    
                
                
                os._exit()
    elif msg_text.isdigit() :
        
        guess=int(msg_text)
        
            
        count=os.path.getsize("{}/answer.txt".format(path))
        count2=os.path.getsize("{}/range.txt".format(path))




        with open('{}/answer.txt'.format(path),'a+') as anser:
            anser.seek(0)
            # print(anser.read())
            num=int(anser.read())

            if guess == num :
                # print('Bingo')
                sendtext(event,'Bingo')
                
                anser.truncate(0)
                with open('{}/range.txt'.format(path),'a+') as range : 
                    range.truncate(0)
                    
                os._exit()




        with open('{}/range.txt'.format(path),'a+') as range :
            range.seek(0)
            if count2 != 0 : 
                text=range.readlines()
                last=text[-1]
                last=last.split(',')
                low=int(last[0])
                high=int(last[1])

                if guess < low or guess > high :
                    # print("?????????{}-{}???????????????".format(low,high))
                    sendtext(event,"?????????{}-{}???????????????".format(low,high))
                    os._exit()
                
                elif  guess < num :
                    low = msg_text
                else :
                    high = msg_text

                range.write("{},{}\n".format(low,high))
                # print("????????????{}-{}???????????????".format(low,high))
                sendtext(event,"????????????{}-{}???????????????".format(int(low),int(high)))
                os._exit()    
    elif msg_text == "??????-??????" or msg_text == "??????-??????" or msg_text == "??????-???":
        final=[
            'win',
            'lose',
            'tie',
        ]

        result=random.choice(final)
        if result == "win" and msg_text.count('??????'):
            # print('?????????')
            # print('you win')
            sendtext(event,"""
            ?????????
            you win """)
        elif result == 'win' and msg_text.count('??????'):
            # print('????????????')
            # print('you win')
            sendtext(event,"""
            ????????????
            you win """)
        elif result == 'win' and msg_text.count('???'):
            # print('????????????')
            # print('you win')
            sendtext(event,"""
            ????????????
            you win """)
        elif result == 'tie' :
            hand=msg_text.split('-')
            # print('??????{}'.format(hand[1]))
            # print('??????')
            sendtext(event,"""
            ??????{}
            ?????? """.format(hand[1]))
        elif result == 'lose' and msg_text.count('??????'):
            # print('????????????')
            # print('you lose')
            sendtext(event,"""
            ????????????
            you lose """)
        elif result =='lose' and msg_text.count('??????'):
            # print('?????????')
            # print('you lose')
            sendtext(event,"""
            ?????????
            you lose """)
        elif result == 'lose' and msg_text.count('???'):
            # print('????????????')
            # print('you lose')
            sendtext(event,"""
            ????????????
            you lose """)
    
    elif "!????????????" in msg_text : 
        sendtext(event,"???????????????????????????>>\n??????,????????????,???????????????")


    elif re.search(r'^\d+\,\d+\,\d+$',msg_text) :
        plist=msg_text.split(',')


        worktime = int(plist[1])
        pay = int(plist[0])
        basic = int(plist[2])*8
        OTtime = worktime - basic
        if OTtime < 0 :
            sendtext(event,"?????????????????? ${}".format(pay))
        else :
            daypay=pay/30
            OTpay=OTtime/8*daypay

            
            if OTtime > int(plist[2])*2 :
                OT1 = int(plist[2])*2/8*daypay*0.33
                OT2 = (OTtime-int(plist[2])*2)/8 * daypay *0.66
            else :
                OT1 = OTtime/8 * daypay * 0.33
                OT2 = 0 

            OTall= OT1+OT2

            final_pay=pay+OTpay+OTall

            sendtext(event,"""
????????????: {} hr
????????????: ${}
????????????: {} hr
??????????????? : {}
????????????: ${}

=====================

    ????????????

??????????????????: ${}
( ????????????/8 * ?????? )

    ????????????

?????????2??????: ${}
( (?????????*2hr/8 * ??????)*0.33 ) 

????????????2??????: ${}
( (???????????? - ?????????*2hr)/8 *??????*0.66 )

=====================

?????????: ${}
( ?????? + ?????????????????? + ????????????)

            """.format(worktime,int(pay),OTtime,int(plist[2]),int(daypay),int(OTpay),int(OT1),int(OT2),int(final_pay)))



    elif msg_text =="!??????":
        sendtext(event,"""
1. !????????????
2. !????????????
3. ??????
4. ???????????????????????????
???????????? : write,????????????,??????
???????????? : search,????????????
        """)

    








                



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)