# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 16:39:44 2022

@author: JulienChapuy
"""

from ShazamAPI import Shazam
from urllib.request import urlopen
import time
# from tqdm import tqdm
import pandas as pd
import smtplib
import ssl
from email.message import EmailMessage
from datetime import date

# import imghdr

def make_row(meta_data):
    
    name_of_service = 'Cacoteo Radio #1 Reggaeton Station Online'
    transmission_category = 'A'
    featured_artist = meta_data['subtitle']
    song_title = meta_data['title']
    album_title = None
    marketing_label = None
    try:
        isrc = meta_data['isrc']
    except:
        isrc = None
        
    row = {
        'Name of service':name_of_service,
        'Transmission category':transmission_category,
        'Artist':featured_artist,
        'Title':song_title,
        'Album title':album_title,
        'Marketing label':marketing_label,
        'ISRC':isrc
        }
    
    return(row)

if __name__ == '__main__':
    
    url = "https://streamingp.shoutcast.com/cacoteo-radio-reggaeton"

    STACK = [{'Title':'%START%'}]

    duration_in_minutes = 2
    pause_in_seconds = 30

    t0 = time.time()
    
    while time.time()-t0 < duration_in_minutes*60:
        
    # for i in range(duration_in_minutes*60 // pause_in_seconds):
        try:
            stream = urlopen(url)
            # la méthode "setText" de QLabel permet de changer
            # le texte de l'étiquette
            print('1/3 - Reading stream...')
            shazam = Shazam(stream.read(200_000))
            
            print('2/3 - Recognizing song...')
            recognize_generator = shazam.recognizeSong()
            meta_data = next(recognize_generator)[1]['track']
            
            row = make_row(meta_data)
            
            string_ = f"{row['Title']} - {row['Artist']}"
            # print(string_) 
            if (row['Title'] not in STACK[-1]['Title']) and (STACK[-1]['Title'] not in row['Title']):
                STACK.append(row)
                print(f'  |  Currently playing: {string_}')
            else:
                print(f'  |  Still playing {string_}')
            print('3/3 - Sleeping...\n')
            time.sleep(pause_in_seconds)
    
        except:
            print('Error: Unkown song')
            
    df = pd.DataFrame(STACK)
    # _, counts = np.unique(df['Title'], return_counts = True)
    # df['Actual performances'] = counts
    df.to_excel('history.xlsx')
    
    # Define email sender and receiver
    email_sender = 'julch.sc@gmail.com'
    email_password = 'fikisnegachrfane'
    email_receiver = ['julien.chapuy@shoutcast.com', 'cyprien.lejeune@shoutcast.com']

    today = date.today()
    
    # Set the subject and body of the email
    subject = f'Royalty Report Cacoteo ({str(today)})'
    body = """
    Please find attached Cacoteo royalty report for today.
    """

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    with open('history.xlsx', 'rb') as f:
        file_data = f.read()
        # file_type = imghdr.what(None, file_data)
        # file_name = f.name
        em.add_attachment(file_data, 
                          maintype='application', 
                          subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                          filename = f"Royalty_Report_Cacoteo_{str(today).replace('-', '')}.xlsx")

    # Add SSL (layer of security)
    context = ssl.create_default_context()

    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
            
        
