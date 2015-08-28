#!/usr/bin/env python
import sys
import imaplib
import getpass
import email
import email.header
import datetime
import re
import requests
import random
import ast
import time
EMAIL_ACCOUNT = "abcdefghijklmnopqrst@gmail.com"
EMAIL_FOLDER = "INBOX"

emailList = []

def insertDots(str,at):
    if at ==0 or str.count('.')==3:
        emailList.append(str)
        return
    newStr = str[:at]+"."+str[at:]
    for i in range(at):
        insertDots(newStr,i)

def allDots(str):
    for i in range(len(str)):
        insertDots(str,i)

headers = {
        'host':'invites.oneplus.net',
        'connection':'keep-alive',
        'accept':'*/*',
        'accept-encoding':'gzip,deflate,sdch',
        'accept-language' : 'en-US,en;q=0.8',
         'user-agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537/36(KHTML, like Gecko) Chrome/44.0.2403.107 Safari/537.36',
         'Referer':'http://oneplus.net/invites?kolid=JLAX2O'
}

def make_request(url):
    for i in range(1):
        r = requests.get(url,headers=headers)
        if r.status_code == requests.codes.ok:
            response = r.text.replace('null','"hagga"')
            print response
            response = ast.literal_eval(response)
            print response
            if response['ret'] ==0 and 'hagga' in response['errMsg']:
                print 'Email seems has been sent, will retry'
                continue
            elif response['ret'] == -1 and 'e-mail' in response['errMsg']:
                print response['errMsg']
                break
            else:
                print 'Status Unknown, will retry'
                return False
    return True

def process_mailbox(M):
    """
    Do something with emails messages in the folder.  
    For the sake of this example, print some headers.
    """

    rv, data = M.search(None, 'SUBJECT', "Confirm your email")
    if rv != 'OK':
        print "No messages found!"
        return
    num = data[0].split()
    mails = data[0].split()
    if len(num)==0:
        return
    num =num[len(num)-1]
    rv, data = M.fetch(num, "(RFC822)")
    if rv != 'OK':
        print "ERROR getting message", num
        return

    msg = email.message_from_string(data[0][1])
    date_tuple = email.utils.parsedate_tz(msg['Date'])
    if date_tuple:
        local_date = datetime.datetime.fromtimestamp(
            email.utils.mktime_tz(date_tuple))
        print "Local Date:", \
            local_date.strftime("%a, %d %b %Y %H:%M:%S")
    if msg.get_content_maintype() == 'multipart': #If message is multi part we only want the text version of the body, this walks the message and gets the body.
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
                body = str(body)
                print body
                matchObj = re.search( r'(https://invites.*)(\.)', body,re.M|re.I)
                print "matchObj.group() : ", matchObj.group(1)
                url =  str(matchObj.group(1))
                r = requests.get(url)
                if r.status_code == requests.codes.ok:
                    print('Confirmation done')
            else:
                pass
    for num in mails:
        M.store(num, '+FLAGS', '\\Deleted')
    M.expunge()
    '''
    #matchObj = re.match( r'invites\.oneplus\.net/confirm/', line)
    print str(msg)
    decode = email.header.decode_header(msg['Subject'])[0]
    subject = unicode(decode[0])
    print 'Message %s: %s' % (num, subject)
    print 'Raw Date:', msg['Date']
    # Now convert to local date-time
    date_tuple = email.utils.parsedate_tz(msg['Date'])
    if date_tuple:
        local_date = datetime.datetime.fromtimestamp(
            email.utils.mktime_tz(date_tuple))
        print "Local Date:", \
            local_date.st  rftime("%a, %d %b %Y %H:%M:%S")
    '''

allDots('abcdefghijklmnopqrst'.replace('.',''))
emailList=list(sorted(set(emailList), key=lambda mail: mail.count('.')))
M = imaplib.IMAP4_SSL('imap.gmail.com',993)

try:
    rv, data = M.login(EMAIL_ACCOUNT, getpass.getpass())
except imaplib.IMAP4.error:
    print "LOGIN FAILED!!! "
    sys.exit(1)

print rv, data

rv, mailboxes = M.list()
if rv == 'OK':
    print "Mailboxes:"
    print mailboxes

with open('latest2.out','r') as latest:
    count=int(latest.readline())

while(count<=len(emailList)):
    mail = emailList[count]
    url = 'https://invites.oneplus.net/index.php?r=share/signup&email={0}@gmail.com&koid=JLAX2O&_={1}'
    timestamp = int((datetime.datetime.utcnow() - datetime.datetime(1970,1,1)).total_seconds()*1000)
    print timestamp
    print mail
    url = url.format(mail,timestamp)
    print url
    if make_request(url):
        time.sleep(5)
        rv, data = M.select(EMAIL_FOLDER)
        if rv == 'OK':
            print "Processing mailbox...\n"
            process_mailbox(M)
            time.sleep(5)
        else:
            print "ERROR: Unable to open mailbox ", rv
    else:
        time.sleep(5)
    with open('latest2.out','w') as latest:
        latest.write(str(count))
    count-=1
M.close()
M.logout()