import os
import base64
from bs4 import BeautifulSoup
import re
import httplib2
from googleapiclient import errors
from googleapiclient.discovery import build
from oauth2client import client, tools, file

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

CLIENT_SECRET_FILE = 'client_secret.json'

''' 
FUNCTIONS FOR READING MESSAGES
'''

def get_credentials():
    wd = os.getcwd()
    
    credential_path = os.path.join(wd, 'credentials.json')
    store = file.Storage(credential_path)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    return creds

def ReadMessages(sender):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = build('gmail', 'v1', http=http)
    messages = ListMessages(service, "me", sender)

    if "Nenhuma mensagem encontrada!" not in messages:
        for msg in messages:
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
    
            payload = txt['payload']
            data = payload['body']['data']
            data = data.replace("-","+").replace("_","/")
            decoded_data = base64.b64decode(data)

            soup = BeautifulSoup(decoded_data , "html.parser")
            body = soup.get_text()
    
            name = ''
            company = ''
            e_mail = ''
            phone = ''
            
            try:
                name = str(re.findall(r'Nome:*[ \w\-.].*',body)[0])
                name = name.replace("Nome: ","").replace("</p>","")
                company = str(re.findall(r'Empresa: *[ \w\-.].*',body)[0])
                company = company.replace("Empresa: ","").replace("</p>","")
                e_mail = str(re.findall(r'Email: *[ \w\-.].*',body)[0])
                e_mail = e_mail.replace("Email: ","").replace("</p>","")
                phone = str(re.findall(r'Telefone: *[ \w\-.].*',body)[0])
                phone = phone.replace("Telefone: ","").replace("</p>","")
            except:
                pass

            return {   
                "nome": name,
                "empresa" : company,
                "e_mail" : e_mail,
                "telefone" : phone
            }
    else:
        return messages

def ListMessages(service, user_id, sender):
    try:
        result = service.users().messages().list(userId=user_id, q="from:" + sender + " is:unread").execute()
        messages = result.get('messages')
        if messages is not None:
            return messages
        else:
            return "Nenhuma mensagem encontrada!"
    except errors.HttpError as error:
        return "Ocorreu um erro: %s" % error
    return "OK"

'''
BELOW BEGINS THE SET UP FOR READING EMAILS
'''

sender = '###'

def main():
    print(ReadMessages(sender))

if __name__ == '__main__':
    main()