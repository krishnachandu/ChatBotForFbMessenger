
# MyFirstChatBot/fb_MyFirstChatBot/views.py
import json, requests, random, re
import random
from pprint import pprint
from django.utils.datastructures import MultiValueDictKeyError
from django.views import generic
from django.http.response import HttpResponse
from django.http.request import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import sqlite3

#  ------------------------ Fill this with your page access token! -------------------------------
PAGE_ACCESS_TOKEN = "EAANCMbDfMaIBAOwnUqDFi1xPLAiLv7H7jhVzLiL2oVN3o70R97IoPaczErZCS15yam2lrg3FowZAO3xgNRktvneGRmZB41pJbd2LG3lHYXgqdakOQ6Y4gEyESiWqc95rJXSaPjDTb0nZC6yYw5Xeuz0Pwvjh58OFifEgSu1YfQZDZD"
VERIFY_TOKEN = 123456
basic_req=["workexperience","skill","projects","academics","achievements",'ctc']

requestinp={
'experience':'workexperience','work' :'workexperience','workexperience':'workexperience',
'technical':'skills', 'skills':'skills','skill':'skills',
    'python':'skills',
'projects' :'projects','project':'projects',
'study':'academics','academics':'academics',
'college':'academics','cgpa':'academics','engineering':'academics','CGPA':'academics',
'awards':'achievements', 'achievements' :'achievements','rewards':'achievements'
}
fields={'workexperience':' Project_Desc ',"skills":" skillIn,skills ","achievements":"achievements_desc ","academics":'AcademicPeriod,Percentage ','projects':'project_title,project_desc'}
jokes = {
          'hi':["Hi","Hello"],
          'how':["I'm Fine ,Thanks for that ask"],
          'fine':["I'm Fine Too !!"],
           'bye':["Good Bye..See you again","Bye..Hope we Will catchup again"],
            'ctc':["My Current CTC is 7.77 LPA","I'm the one who dont run over money,but i expect that for my wok","I see that the market standard for switching jobs is 30-35 Percent"]
}
def get_response_from_db(recevied_message):
    conn = sqlite3.connect('db1.sqlite3')
    c = conn.cursor()
    if recevied_message=='academics':
        id = str(random.randint(0, 2))
    else:
        id=str(random.randint(0,5))
    sqlresp = c.execute('SELECT '+fields[recevied_message] +' FROM '+recevied_message+" WHERE id=?",id)
    sqlresp=sqlresp.fetchone()
    #for eachresp in  sqlresp:
    c.close()
    return sqlresp
def get_list(basic_req):
    resultstr="";
    for i in range(len(basic_req)):
        resultstr=resultstr+ "\n"+basic_req[i]
    return resultstr
# Helper function
def post_facebook_message(fbid, recevied_message):
    tokens = re.sub(r"[^a-zA-Z0-9\s]", ' ', recevied_message).lower().split()
    #pprint(tokens[0])
    sqlresp=None
    for token in tokens:
        print str(token) in  requestinp
        if str(token) in  requestinp:
            pprint("Im here")
            sqlresp=get_response_from_db(requestinp[str(token)])
            break


    #pprint(sqlresp)
    # Remove all punctuations, lower case the text and split it based on space
    finalresp = "One of Them is \n "
    if sqlresp:
        sqlresp=list(sqlresp)
        for i in range(len(sqlresp)):
            finalresp=finalresp+sqlresp[i].encode('ascii')+"\n"
        sqlresp=finalresp+"\n Hit the same for More"
    response_text = ''
    if not sqlresp:
        for token in tokens:
            if token=='ctc':
                response_text = random.choice(jokes[token])
                response_text=response_text+"..Hit Same to know more about this"
                break
            if token in ['hi','hello','hey']:
                response_text = random.choice(jokes['hi'])
                break
            if token in ['how']:
                response_text = random.choice(jokes['how'])
                break
            if token in jokes:
                response_text = random.choice(jokes[token])
                break

    else:
        response_text=str(sqlresp)
    if not response_text:
        response_text = "oops...! I didn't understand !! Please Ask Something related to me,as Follows:\n"+get_list(basic_req);
    user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid
    user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':PAGE_ACCESS_TOKEN}
    user_details = requests.get(user_details_url, user_details_params).json()
    if token in ['hi','hello','hey']:
        print "llllllllllll"
        response_text =  str(response_text.encode('ascii'))+"...!  "+ user_details.get('first_name', "Chandu")+"...Good to see you"
    else:
        print "---------"
        response_text = str(response_text.encode('ascii'))+"\n"
    response_text=response_text[:320]
    #response_text=response_text.strip()
    print response_text
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":response_text}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    #pprint(status.json())

# Create your views here.CL
class MyFirstChatBotView(generic.View):
    def get(self, request, *args, **kwargs):
        try:
            return HttpResponse(self.request.GET['hub.challenge'])
        except MultiValueDictKeyError as e:
            return HttpResponse('Error, invalid token')
            pass


    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        try:
            incoming_message = json.loads(self.request.body.decode('utf-8'))
            # Facebook recommends going through every entry since they might send
            # multiple messages in a single call during high load
            tempmes=incoming_message['entry'][0]
            #print self.request.body
            message=tempmes['messaging'][0]
            """message=message[0]
            message=incoming_message['entry']['message']
            for entry in incoming_message['entry']:
                print len(incoming_message['entry'])
                print "-----------------------"
                for message in entry['messaging']:
                    # Check to make sure the received call is a message call
                    # This might be delivery, optin, postback for other events"""
            if 'message' in message:
                # Print the message to the terminal
                #pprint(message)
                # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                # are sent as attachments and must be handled accordingly.
                #pprint(message)
                post_facebook_message(message['sender']['id'], message['message']['text'])
            return HttpResponse()
        except MultiValueDictKeyError:
            is_private = False