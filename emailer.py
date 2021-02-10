import pandas as pd
import numpy as np

from email.mime.text import MIMEText
import os

import smtplib
from getpass import getpass

SENDER_EMAIL = "" # TODO: fill in with email to send from

df = pd.read_csv('data/matches/matched_pairs_1_22_2021.csv')
full = pd.read_csv('data/responses/responses_1_22_2021.csv')
pas = getpass()

d = {}
for (i, row) in full.iterrows():
    dd = dict(zip(full.columns.tolist(), row.tolist()))

    m_times = dd['What times would you be able to meet? (Pittsburgh time) [Morning]']
    a_times = dd['What times would you be able to meet? (Pittsburgh time) [Afternoon]']
    e_times = dd['What times would you be able to meet? (Pittsburgh time) [Evening]']
    if (m_times is None) or (type(m_times) == float and np.isnan(m_times)):
        m_times = ''
    if (a_times is None) or (type(a_times) == float and np.isnan(a_times)):
        a_times = ''
    if (e_times is None) or (type(e_times) == float and np.isnan(e_times)):
        e_times = ''
    ts = list(['{} Morning'.format(t) for t in m_times.split(';')])
    ts += list(['{} Afternoon'.format(t) for t in a_times.split(';')])
    ts += list(['{} Evening'.format(t) for t in e_times.split(';')])
    ts = ';'.join(ts)

    d[dd['Username']] = {
        'name': dd['Name'],
        'pronoun': dd['Pronouns'],
        'department': dd['SCS Department'],
        'year': dd['What year are you in?'],
        'times': ts,
        'location': dd['Where would you want to be able to meet?'],
        'interaction': dd['What kind of interaction are you after this week?'],
        'hobbies': dd['Hobbies/Interests'],
        'research': dd['Research topics/interests'],
        'mentor/mentee': dd['Would you like to be a mentor and/or mentee?'],
        'background': dd['Background'],
        'other': [dd['Anything else you want us to know for matching purposes?'],
                  dd['Anything else you want us to know for matching purposes?.1'],
                  dd['Anything else you want us to know for matching purposes?.2'],
                  dd['Anything else you want us to know for matching purposes?.3']],
    }

groups = []
N = 0
for (i, row) in df.iterrows():
    print('\n\n=============================================================\n\n')
    print(row.tolist())
    email1, email2, email3, email4 = row.tolist()

    name1 = d[email1]['name'].strip().split(' ')
    name1 = ' '.join(name1[:max(1, len(name1) - 1)])
    name2 = d[email2]['name'].strip().split(' ')
    name2 = ' '.join(name2[:max(1, len(name2) - 1)])
    if type(email3) == str:
        name3 = d[email3]['name'].strip().split(' ')
        name3 = ' '.join(name3[:max(1, len(name3) - 1)])
    if type(email4) == str:
        name4 = d[email4]['name'].strip().split(' ')
        name4 = ' '.join(name4[:max(1, len(name4) - 1)])

    pronoun1 = d[email1]['pronoun'].split(' ')[0]
    pronoun2 = d[email2]['pronoun'].split(' ')[0]
    if type(email3) == str:
        pronoun3 = d[email3]['pronoun'].split(' ')[0]
    if type(email4) == str:
        pronoun4 = d[email4]['pronoun'].split(' ')[0]

    t1 = set(d[email1]['times'].split(';'))
    t2 = set(d[email2]['times'].split(';'))
    time = t1.intersection(t2)
    if type(email3) == str:
        t3 = set(d[email3]['times'].split(';'))
        time = time.intersection(t3)
    if type(email4) == str:
        t4 = set(d[email4]['times'].split(';'))
        time = time.intersection(t4)
    if len(time) == 0:
        time = None
        print('NO TIME')
        print(row)
    else:
        time = ', '.join(list(time))

    l1 = set(d[email1]['location'].split(';'))
    l2 = set(d[email2]['location'].split(';'))
    loc = l1.intersection(l2)
    if type(email3) == str:
        l3 = set(d[email3]['location'].split(';'))
        loc = loc.intersection(l3)
    if type(email4) == str:
        l4 = set(d[email4]['location'].split(';'))
        loc = loc.intersection(l4)
    if len(loc) == 0:
        loc = None
        print('NO LOCATION')
        print(row)
    else:
        location = ' or '.join(list(loc))

    interactions = []
    interactions.append(d[email1]['interaction'])
    interactions.append(d[email2]['interaction'])

    if type(email4) == str:
        s = "\nHi {name1}, {name2}, {name3}, and {name4},<br><br>".format(name1=name1, name2=name2, name3=name3, name4=name4)
        N += 4
        interactions.append(d[email3]['interaction'])
    elif type(email3) == str:
        s = "\nHi {name1}, {name2}, and {name3},<br><br>".format(name1=name1, name2=name2, name3=name3)
        N += 3
        interactions.append(d[email3]['interaction'])
    else:
        s = "\nHi {name1} and {name2},<br><br>".format(name1=name1, name2=name2)
        N += 2

    s += 'Thank you for participating in the SCS Coffee Chats program!<br><br>'

    # interaction type
    interactions = set([itr.replace('Random/Other', 'Random') for itr in interactions])
    s += "This week, we've matched you on the theme(s) of: <b>{}</b>.<br><br>".format(', '.join(interactions))

    if type(email4) == str:
        s += "{name1} ({pronoun1}) is in year {year1} of PhD in the {department1}, {name2} ({pronoun2}) is in year {year2} of PhD in the {department2}, {name3} ({pronoun3}) is in year {year3} of PhD in the {department3}, and {name4} ({pronoun4}) is in year {year4} of PhD in the {department4}.<br><br>".format(
            name1=name1, pronoun1=pronoun1, year1=d[email1]['year'], department1=d[email1]['department'],
            name2=name2, pronoun2=pronoun2, year2=d[email2]['year'], department2=d[email2]['department'],
            name3=name3, pronoun3=pronoun3, year3=d[email3]['year'], department3=d[email3]['department'],
            name4=name4, pronoun4=pronoun4, year4=d[email4]['year'], department4=d[email4]['department'])
    elif type(email3) == str:
        s += "{name1} ({pronoun1}) is in year {year1} of PhD in the {department1}, {name2} ({pronoun2}) is in year {year2} of PhD in the {department2}, and {name3} ({pronoun3}) is in year {year3} of PhD in the {department3}<br><br>".format(
            name1=name1, pronoun1=pronoun1, year1=d[email1]['year'], department1=d[email1]['department'],
            name2=name2, pronoun2=pronoun2, year2=d[email2]['year'], department2=d[email2]['department'],
            name3=name3, pronoun3=pronoun3, year3=d[email3]['year'], department3=d[email3]['department'])
    else:
        s += "{name1} ({pronoun1}) is in year {year1} of PhD in the {department1}, and {name2} ({pronoun2}) is in year {year2} of PhD in the {department2}<br><br>".format(
            name1=name1, pronoun1=pronoun1, year1=d[email1]['year'], department1=d[email1]['department'],
            name2=name2, pronoun2=pronoun2, year2=d[email2]['year'], department2=d[email2]['department'])

    if time is None:
        s += "Since your availability didn't overlap, we'll leave the scheduling to you this time.<br>"
        s += "However, you've all selected to meet <b>{}</b><br>".format(location)

    else:
        s += "You are all available at: <b>{}</b>,<br>".format(time)
        s += "and can meet <b>{}</b><br>".format(location)

    if 'In-person' in location:
        s += 'If meeting in person, remember to bring a mask and follow social distancing guidelines (https://www.cdc.gov/coronavirus/2019-ncov/prevent-getting-sick/prevention.html).<br>'
    s += '<br>'

    s += "Note: Please be respectful of each other's time, and try to confirm with your partner(s) in a timely manner. If you don't receive a response and would like to be re-matched, let us know and we can see if we can rematch you.<br><br>"

    if len(interactions) > 1:
        interactions = list([i for i in interactions if i not in ['Random/Other', 'Random']])
    if len(interactions) > 1:
        import pdb; pdb.set_trace()
    # interaction = list(interactions)[0]  # main interaction

    # interests/ topics
    # if interaction == 'Friendship outside of work':
    if 'Friendship outside of work' in interactions:
        h1 = d[email1]['hobbies']
        h1 = h1 if type(h1) == str else 'N/A'
        h2 = d[email2]['hobbies']
        h2 = h2 if type(h2) == str else 'N/A'
        s += "{name1}'s hobbies/interests include:<br>{hobbies1}<br><br>".format(name1=name1, hobbies1=h1)
        s += "{name2}'s hobbies/interests include:<br>{hobbies2}<br><br>".format(name2=name2, hobbies2=h2)
        if type(email3) == str:
            h3 = d[email3]['hobbies']
            h3 = h3 if type(h3) == str else 'N/A'
            s += "{name3}'s hobbies/interests include:<br>{hobbies3}<br><br>".format(name3=name3, hobbies3=h3)
        if type(email4) == str:
            h4 = d[email4]['hobbies']
            h4 = h4 if type(h4) == str else 'N/A'
            s += "{name4}'s hobbies/interests include:<br>{hobbies4}<br><br>".format(name4=name4, hobbies4=h4)
        # elif interaction == 'Research topic':
    if 'Research topic' in interactions:
        t1 = d[email1]['research']
        t1 = t1 if type(t1) == str else 'N/A'
        t2 =d[email2]['research']
        t2 = t2 if type(t2) == str else 'N/A'
        s += "{name1}'s research topics/interests include:<br>{t1}<br><br>".format(name1=name1, t1=t1)
        s += "{name2}'s research topics/interests include:<br>{t2}<br><br>".format(name2=name2, t2=t2)
        if type(email3) == str:
            t3 = d[email3]['research']
            t3 = t3 if type(t3) == str else 'N/A'
            s += "{name3}'s research topics/interests include:<br>{t3}<br><br>".format(name3=name3, t3=t3)
        if type(email4) == str:
            t4 = d[email4]['research']
            t4 = t4 if type(t4) == str else 'N/A'
            s += "{name4}'s research topics/interests include:<br>{t4}<br><br>".format(name4=name4, t4=t4)
        #elif interaction == 'PhD mentorship':
    if 'PhD mentorship' in interactions:
        m1 = d[email1]['mentor/mentee']
        m1 = m1 if type(m1) == str else 'N/A'
        m2 = d[email2]['mentor/mentee']
        m2 = m2 if type(m2) == str else 'N/A'
        roles = set([m1, m2])
        s += "{name1} has selected to be a: {m1}<br>".format(name1=name1, m1=m1)
        s += "{name2} has selected to be a: {m2}<br>".format(name2=name2, m2=m2)
        if type(email3) == str:
            m3 = d[email3]['mentor/mentee']
            m3 = m3 if type(m3) == str else 'N/A'
            s += "{name3} has selected to be a: {m3}<br>".format(name3=name3, m3=m3)
            roles.add(m3)
        if type(email4) == str:
            m4 = d[email4]['mentor/mentee']
            m4 = m4 if type(m4) == str else 'N/A'
            s += "{name4} has selected to be a: {m4}<br>".format(name4=name4, m4=m4)
            roles.add(m4)
        if 'Mentor' not in roles:
            s += "<br>Note: We didn't have enough mentors enter the pool this week, but nevertheless we hope that you are able to share your experiences with each other and help each other grow!<br>"
        s += '<br>'
    # else:
    #     assert(interaction == 'Random/Other' or interaction == 'Random')
    
    s += "To help kick off the conversation, here are some <b>optional icebreaker questions/activities</b> for when you meet:<br>"
    s += "1. What's the best piece of advice you've ever heard?<br>"
    s += "2. If you had 25 hours a day, how would you use your extra time?<br>"
    s += "3. Do a short workout together (e.g. 10 jumping jacks, 10 pushups, 10 sit ups).<br>"
    s += "4. What have been your most memorable moments this year? In PhD?<br>"
    s += "5. Take a creative selfie/screenshot and send it to us! (feel free to use this email thread)<br>"

    s += "<br>Finally, once you've had your coffee chat <b>we'd love to hear how it went</b> & any feedback/suggestions you might have: <b><a href='https://forms.gle/qVjwminy82hFuYPo7'>link</a><br></b>"

    s += '<br>Happy coffee-chatting!<br><br>Social Connectedness Working Group (part of the <a href="https://scs-phd-deans-committee.github.io/">SCS PhD Advisory Committee</a>)'

    print(s.replace('<br>', '\n'))
    ps = input('Any changes?')
    if ps is not None and len(ps) > 1:
        s += '<br><br>P.S. ' + ps
        print(s.replace('<br>', '\n'))

    if input('Skip? (y/n)') == 'y':
        print('SKIPPED!')
        continue

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        usr = SENDER_EMAIL # input('gmail user: ')
        server.login(usr, pas)

        # s = smtplib.SMTP('smtp.uk.xensource.com')
        # s.set_debuglevel(1)
        msg = MIMEText(s, 'html')
        sender = SENDER_EMAIL
        recipients = [email1, email2]
        if type(email3) == str:
            recipients += [email3]
        if type(email4) == str:
            recipients += [email4]

        print(recipients)
        msg['Subject'] = "SCS PhD Coffee Chat Match!"
        msg['From'] = SENDER_EMAIL
        msg['To'] = ", ".join(recipients)
        import pdb; pdb.set_trace()
        #server.sendmail(sender, recipients, msg.as_string())  # TODO: uncomment when sending
        print('sent!')
    except Exception as e:
        print(e)
        print('Something went wrong...')


import pdb; pdb.set_trace()
