from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session
import os
import sqlite3
# import time
from sqlalchemy import Table, Column ,create_engine , String, ForeignKey
from typing import List, Optional
from sqlalchemy.orm import DeclarativeBase , sessionmaker, Mapped, mapped_column, relationship
import requests
from flask_restful import Api, Resource



engine = create_engine("sqlite:///users.db", echo=False)

Session = sessionmaker(bind=engine)
#owm key: f68c228a96e5e4ece4a10a990838364c


class Base(DeclarativeBase):
    def createdb(self):
        Base.metadata.create_all(engine)

    def dropdb(self):
        Base.metadata.drop_all(engine)





app = Flask(__name__)
api = Api(app)


app.config['SECRET_KEY'] = "SUSSY-BAKA"
app.config['PERMANENT_SESSION_LIFETIME'] = 3600


class Registred(Base):
    __tablename__ = 'registred'
    email: Mapped[str] = mapped_column(String(30), primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    password: Mapped[str] = mapped_column(String(40))

class Event(Base):
    __tablename__ = 'plans'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(30), ForeignKey('registred.email'))
    event_name: Mapped[str] = mapped_column(String(45))
    event_info: Mapped[Optional[str]] = mapped_column(String(200))
    event_time: Mapped[str] = mapped_column(String(50))


class ToDoes(Base):
    __tablename__ = 'todoes'
    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    email: Mapped[str] = mapped_column(String(70))
    todovalue: Mapped[Optional[str]] = mapped_column(String(50))

def newRegistration(email:str, name:str, password:str):
    with Session() as session:
        new_registration = Registred(email=email, name=name, password=password)
        session.add(new_registration)
        session.commit()

def newToDo(todovalue:str, email:str):
    with Session() as session:
        new_todo = ToDoes(todovalue=todovalue, email=email)
        session.add(new_todo)
        session.commit()

def newEvent(email:str, event:str, info:str, time):
    with Session() as session:
        new_event = Event(email=email, event_name=event, event_info=info, event_time=time)
        session.add(new_event)
        session.commit()



import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(sender_email, sender_password, receiver_email, subject, message):
    # Set up the SMTP server
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # For Gmail

    # Create a MIME object for the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach the message to the email
    msg.attach(MIMEText(message, 'plain'))

    # Log in to the SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Start TLS encryption
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

# Example usage

@app.route("/")
def homepage():

    # session['reg'] = False
    try:
        if session['reg'] == False:
            session['reg'] = False
            print(session['reg'])
    except:
        session['reg'] = False
    if session['reg'] == False:
        return render_template("index.html")
    else:
        return render_template('index.html', logged=1)

@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get('reg') == False:
        if request.method == 'GET':
            return render_template('registration.html')
        else:
            name = request.form['name']
            email = request.form['email']
            pass1 = request.form['pass']
            pass2 = request.form['pass2']
            if pass1 != pass2:
                return render_template("registration.html", passus=1)
            else:

                try:
                    email = email.split("@")
                    email = "__________".join(email)
                    newRegistration(email,name,pass1)
                    session['reg'] = True
                    ses_em = email.split('@')
                    ses_em = "__________".join(ses_em)
                    session['email'] = ses_em
                    return render_template("registration.html", susss=1)
                except Exception as e:
                    print(e)
                    return render_template('registration.html', err=1)
    else:
        return render_template("index.html", loggederr=1)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if session.get('reg') == False:
        if request.method == 'GET':

            return render_template("login.html")


        else:
            good = False
            email = request.form['email']
            email = email.split("@")
            email = "__________".join(email)

            password = request.form['pass']
            with sqlite3.connect('users.db') as cursor:
                info = cursor.execute("select email, password from registred")
            for i in info:
                print(i[0])
                print(i[1])
                if email == i[0] and password == i[1]:
                    good = True
                    break
                else:
                    continue
            if good == True:
                session['reg'] = True
                ses_em = email.split('@')
                ses_em = "__________".join(ses_em)
                session['email'] = ses_em
                return '<meta http-equiv="refresh" content="0; URL=\'/\'" />'
            else:
                return render_template('login.html', err=1)
    else:
        return render_template("index.html", loggederr=1)

@app.route("/account")
def account():
    if session.get('reg') == True:
        return render_template('account.html')
    else:
        return '<meta http-equiv="refresh" content="0; URL=\'/\'" />'

@app.route("/exit")
def exit():
    session['reg'] = False
    return '<meta http-equiv="refresh" content="0; URL=\'/\'" />'


@app.route("/create-plan", methods=['GET', 'POST'])
def create_plan():
    if session.get('reg') == True:
        if request.method == "GET":

            return render_template('newplan.html')
        else:
            email = session.get('email')
            name = request.form['name']
            info = request.form['info']
            time = request.form['event-time']
            print(time)

            newEvent(email, name, info, time)
            return '<meta http-equiv="refresh" content="0; URL=\'/\'" />'
    else:
        return render_template('_notlogged.html')

@app.route("/create-todo", methods=['GET', 'POST'])
def create_ToDo():
    if session.get('reg') == True:
        if request.method == "GET":

            return render_template('newplan.html')
        else:
            email = session.get('email')
            name = request.form['name']
            info = request.form['info']
            time = request.form['event-time']
            print(time)

            newEvent(email, name, info, time)
            return '<meta http-equiv="refresh" content="0; URL=\'/\'" />'
    else:
        return render_template('_notlogged.html')



@app.route('/plans')
def plans():
    if session.get('reg') == True:
        events2 = []
        events = []
        with sqlite3.connect('users.db') as cursor:


            print(session.get('email'))

            events1 = cursor.execute(f"select * from plans where email = '{str(session.get('email'))}'")
            # with Session() as session1:
            #     events1 = session1.query(Event).filter_by(email = session.get('email')).all()
            #     print(session.get('email'))
            #     print(events1)
        for i in events1:
            print(i)
            events2.append(i)
        print(events2)
        index2 = 0
        for i in events2:

            index = 0
            events.append(dict())

            for j in i:
                # print(int(i[0])-1)
                # print(events[int(i[0])-1])
                print('--------------------')
                print(i)
                print(i[0])
                print(i[0]-1)
                print(events)

                if index == 2:
                    events[index2]['name'] = j
                if index == 3:
                    events[index2]['info'] = j
                if index == 4:
                    time = str(j).split('T')
                    time = " ".join(time)
                    events[index2]['time'] = time



                # print(int(i[0])-1)
                # print(events[int(i[0])-1])
                index+=1
            index2 +=1


        index = 0
        print(events)

        print(len(events))

        return render_template('plans.html', len_events=len(events), events=events)

    else:
        return render_template('_notlogged.html')

@app.route('/todolists', methods=['GET', 'POST'])
def TODO_lists():
    if session.get('reg') == True:
        if request.method == 'GET':

            count = 0
            todovalue = []
            with sqlite3.connect('users.db') as cursor:


                print(session.get('email'))

                todoes = cursor.execute(f"select todovalue from todoes where email = '{str(session.get('email'))}'")
                for i in todoes:
                    for j in i:

                        print(j)
                        todovalue.append(j)
                        count+=1
                print(count)

            return render_template('todolists.html', todovalue=todovalue)
        else:
            value = request.form['todovalue']
            email = session.get('email')

            newToDo(value,email)

            count = 0

            todovalue = []
            with sqlite3.connect('users.db') as cursor:


                print(session.get('email'))

                todoes = cursor.execute(f"select todovalue from todoes where email = '{str(session.get('email'))}'")
                for i in todoes:
                    for j in i:

                        print(j)
                        todovalue.append(j)
                        count+=1
                print(count)

            return render_template('todolists.html', todovalue=todovalue)
        # events2 = []
        # events = []
        # with sqlite3.connect('users.db') as cursor:
        #
        #     print(session['email'])
        #     print(session.get('email'))
        #
        #     events1 = cursor.execute(f"select * from plans where email = '{str(session.get('email'))}'")
        #     # with Session() as session1:
        #     #     events1 = session1.query(Event).filter_by(email = session.get('email')).all()
        #     #     print(session.get('email'))
        #     #     print(events1)
        # for i in events1:
        #     print(i)
        #     events2.append(i)
        # print(events2)
        # index2 = 0
        # for i in events2:
        #
        #     index = 0
        #     events.append(dict())
        #
        #     for j in i:
        #         # print(int(i[0])-1)
        #         # print(events[int(i[0])-1])
        #         print('--------------------')
        #         print(i)
        #         print(i[0])
        #         print(i[0]-1)
        #         print(events)
        #
        #         if index == 2:
        #             events[index2]['name'] = j
        #         if index == 3:
        #             events[index2]['info'] = j
        #         if index == 4:
        #             time = str(j).split('T')
        #             time = " ".join(time)
        #             events[index2]['time'] = time
        #
        #
        #
        #         # print(int(i[0])-1)
        #         # print(events[int(i[0])-1])
        #         index+=1
        #     index2 +=1
        #
        #
        # index = 0
        # print(events)
        #
        # print(len(events))
        #
        # return render_template('events.html', len_events=len(events), events=events)

    else:
        return render_template('_notlogged.html')


@app.route("/delete-todo", methods=['POST'])
def delete_todo():
    if session.get('reg') == True:
        if request.method == 'POST':
            email = session.get('email')
            todovalue = request.json.get('todovalue')
            # Delete the to-do item from the database
            with sqlite3.connect('users.db') as cursor:
                cursor.execute(f"DELETE FROM todoes WHERE email = ? AND todovalue = ?", (email, todovalue))
                # Commit the transaction
                cursor.commit()
            return 'Success', 200
    else:
        return 'Unauthorized', 401


base = Base()
base.createdb()
#base.dropdb()

if __name__ == '__main__':
    app.run(debug=True, host='192.168.1.228')


#app_pass = 'hcis uvvi ildf mhqp' #hcisuvviildfmhqp
# sender_email = 'vladyslav.bankovskyi@gmail.com'
# sender_password = 'hcisuvviildfmhqp'
# receiver_email = 'improvisible.sound@gmail.com'
# subject = 'Test Email'
# message = 'This is a test email sent from Python.'
#
# send_email(sender_email, sender_password, receiver_email, subject, message)