from bottle import route, run, template, static_file, request, error
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, session, relationship

Base = declarative_base()
engine = create_engine('mysql://root:coderslab@localhost:3306/school')
Session = sessionmaker(bind=engine)
session = Session()
metadata = MetaData()

conn = engine.connect()

# enter index.html
@route("/")
def index():
    return template('index')


# take all of the bootstrap files  from the static folder
@route('/static/<filename:path>')
def server_static(filename):
    return static_file(filename, root='./static')


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    login = Column(String(255), unique=true)
    password = Column(String(255))
    email = Column(String(255), unique=True)
    sale = relationship("Sala")
    saleZ = relationship("Sala", back_populates="user")

    @route("/registerUser", method="POST")
    def registerUser():
        conn.execute('INSERT INTO User(login, password ,email ) VALUES(%s,%s,%s) ',
                     (request.forms["login"], request.forms["password"],
                      request.forms["email"]))
        allEvents={}
        userAfterRegestrationTakeLogin = User()
        session.add(userAfterRegestrationTakeLogin)
        allEvents["allEvents"] = conn.execute("SELECT  * FROM sala where user_id = (%s)", (User.id))
        return template('afterUserIsRegisteredOrLoggedIn', allEvents)

    @route("/login")
    def loginUser():
        return template('loginUser')

    @route("/loginS", method="POST")
    def okUser():
        loginMyUser = conn.execute("SELECT login  , password FROM user")
        validUsernames = [u[0] for u in loginMyUser.fetchall()]
        if (request.forms["login"] and request.forms["password"]) in validUsernames:
            userAfterRegestrationTakeLogin = User()
            session.add(userAfterRegestrationTakeLogin)
            # user =session.query(User, User.login)
            allEvents = {}
            allEvents["allEvents"] = conn.execute("SELECT  * FROM sala where user_id = (%s)", (User.id))
            return template('afterUserIsRegisteredOrLoggedIn', allEvents)
        else:
            return template('index')


class Sala(Base):
    __tablename__ = 'sala'
    id = Column("id", Integer, primary_key=True, autoincrement=True, nullable=False)
    type = Column("type", String(255))
    name = Column("name", String(255))
    date = Column("date", Date)
    time = Column("time", Time)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="sale")
    address = Column("address", String(255))

    @route("/sala", method="POST")
    def addNewSala():
        takeaddress = conn.execute('SELECT address FROM salaDatabase WHERE name = (%s)', (request.forms["name"]))
        my_user = session.query(User).join(Sala, User.id == Sala.user)
        my_user=my_user.fetchall()

        conn.execute(
            'INSERT INTO Sala(type , name , date , time, user_id , address ) Values(%s,%s,%s,%s,%s,(SELECT address FROM salaDatabase WHERE name = (%s)))',
            (request.forms["type"], request.forms["name"],
             request.forms["date"], request.forms["time"], my_user, request.forms["name"],))
        allEvents = {}
        allEvents["allEvents"] = conn.execute(
            "SELECT type , name , address , date , time  FROM sala  where user_id = (%s)" , (my_user,))
        return template('afterUserIsRegisteredOrLoggedIn', allEvents)

    @route("/showsala", method="get")
    def userAddNewEventOnExistingSala():
        typeForSalaDropDownList = {}
        allEvents = {}
        nameForSalaDropDownList = {}
        allEvents["allEvents"] = conn.execute("SELECT type , name FROM salaDatabase ")
        typeForSalaDropDownList["typeFromAll"] = conn.execute("SELECT type FROM salaDatabase ")
        nameForSalaDropDownList["nameFromAll"] = conn.execute("SELECT  name FROM salaDatabase ")
        return template('sala', allEvents, typeForSalaDropDownList, nameForSalaDropDownList)


class Admin(Base):
    __tablename__ = 'admin'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    login = Column(String(255))
    password = Column(String(255))

    @route("/admin")
    def admin():
        selectAllFromSalaDatabase = {}
        selectAllEventsThatAraInDatabase ={}
        objectWithAllEvents={}
        selectAllFromSalaDatabase["records"] = conn.execute("Select id , type , name , address from salaDatabase ORDER  BY id desc")
        selectAllEventsThatAraInDatabase["users"] = conn.execute("Select login , email , id from USER order by id desc")
        objectWithAllEvents["events"] = conn.execute("Select name , date , time , user_id , id from Sala order by DATE  ")

        return template('adminSignIn' , selectAllFromSalaDatabase, selectAllEventsThatAraInDatabase, objectWithAllEvents)


    @route("/addNewRecord")
    def adminAddNewRecord():
        return template('newRecord')

    @route("/adminSi", method="POST")
    def okAdmin():
        loginMyAdmin = conn.execute("SELECT login  , password FROM admin")
        validAdmin = [u[0] for u in loginMyAdmin.fetchall()]
        if (request.forms["login"] and request.forms["password"]) in validAdmin:
            selectAllFromSalaDatabase = {}
            selectAllEventsThatAraInDatabase = {}
            objectWithAllEvents = {}
            selectAllFromSalaDatabase["records"] = conn.execute("Select id , type , name , address from salaDatabase ORDER  BY id desc")
            selectAllEventsThatAraInDatabase["users"] = conn.execute("Select login , email , id from USER  order by id desc")
            objectWithAllEvents["events"] = conn.execute("Select name , date , time , user_id , id from Sala order by id desc")
            return template('admin',  selectAllFromSalaDatabase, selectAllEventsThatAraInDatabase, objectWithAllEvents)

        else:
            return template('adminSignIn')

    @route("/recordAdded", method="POST")
    def addNewRecordAdmin():
        conn.execute('INSERT INTO salaDatabase (type, name, address) VALUES (%s,%s,%s)',
                     (request.forms["type"], request.forms["name"], request.forms["address"]))
        selectAllFromSalaDatabase = {}
        selectAllEventsThatAraInDatabase = {}
        objectWithAllEvents = {}
        selectAllFromSalaDatabase["records"] = conn.execute("Select id , type , name , address from salaDatabase ORDER  BY id desc")
        selectAllEventsThatAraInDatabase["users"] = conn.execute("Select login , email , id from USER order by id desc")
        objectWithAllEvents["events"] = conn.execute("Select name , date , time , user_id , id from Sala order by id desc")
        return template('admin', selectAllFromSalaDatabase, selectAllEventsThatAraInDatabase, objectWithAllEvents )

    @route('/deleterecord/<id>', method="POST")
    def deleteRecord(id):
        conn.execute('DELETE FROM  salaDatabase WHERE id=(%s)', (id,))
        selectAllFromSalaDatabase = {}
        selectAllEventsThatAraInDatabase = {}
        objectWithAllEvents = {}
        selectAllFromSalaDatabase = {}
        selectAllEventsThatAraInDatabase["users"] = conn.execute("Select login , email , id from USER ")
        objectWithAllEvents["events"] = conn.execute("Select name , date , time , user_id , id from Sala")
        selectAllFromSalaDatabase["records"] = conn.execute(
            "Select id , type , name , address from salaDatabase ORDER  BY id desc")
        return template('admin', selectAllFromSalaDatabase, selectAllEventsThatAraInDatabase, objectWithAllEvents)

    @route('/deleteuser/<id>', method="POST")
    def deleteUser(id):
        conn.execute('DELETE FROM user WHERE id=(%s)', (id,))
        selectAllFromSalaDatabase = {}
        selectAllEventsThatAraInDatabase= {}
        objectWithAllEvents = {}
        selectAllFromSalaDatabase = {}
        selectAllEventsThatAraInDatabase["users"] = conn.execute("Select login , email , id from USER ")
        objectWithAllEvents["events"] = conn.execute("Select name , date , time , user_id , id from Sala")
        selectAllFromSalaDatabase["records"] = conn.execute(
            "Select id , type , name , address from salaDatabase ORDER  BY id desc")
        return template('admin', selectAllFromSalaDatabase, selectAllEventsThatAraInDatabase, objectWithAllEvents)

    @route('deleteevent/<id>', method="POST")
    def deleteEvent(id):
        conn.execute('DELETE FROM sala WHERE id=(%s)', (id,))
        selectAllFromSalaDatabase = {}
        selectAllEventsThatAraInDatabase = {}
        objectWithAllEvents = {}
        selectAllFromSalaDatabase = {}
        selectAllEventsThatAraInDatabase["users"] = conn.execute("Select login , email , id from USER ")
        objectWithAllEvents["events"] = conn.execute("Select name , date , time , user_id , id from Sala")
        selectAllFromSalaDatabase["records"] = conn.execute(
            "Select id , type , name , address from salaDatabase ORDER  BY id desc")
        return template('admin', selectAllFromSalaDatabase, selectAllEventsThatAraInDatabase, objectWithAllEvents)

    @route('/<id>/updaterecord', method="POST")
    def updateEvent(id):
        selectAllFromSalaDatabase = {}
        selectAllFromSalaDatabase["records"] = conn.execute("Select id , type , name , address from salaDatabase where id = (%s)" , (id,))
        return template('updateRecord' , selectAllFromSalaDatabase)


    @route('/<id>/updateuser', method="POST")
    def updateEvent(id):
        selectAllEventsThatAraInDatabase = {}
        selectAllEventsThatAraInDatabase["users"] = conn.execute("Select login , email , id from USER where id = (%s)" , (id,))
        return template('updateUser' , selectAllEventsThatAraInDatabase)

    @route('/<id>/updateevent', method="POST")
    def updateEvent(id):
        objectWithAllEvents = {}
        objectWithAllEvents["events"] = conn.execute("Select name , date , time , user_id , id from Sala WHERE  id = (%s)" , (id,))
        return template('updateEvent', objectWithAllEvents)

    @route('/<id>/update/record', method="POST")
    def updateRecord(id):
        conn.execute('UPDATE salaDatabase SET type = (%s), name = (%s), address = (%s) where id=(%s)',
            (request.forms["type"], request.forms["name"], request.forms["address"], id))
        selectAllFromSalaDatabase = {}
        selectAllEventsThatAraInDatabase = {}
        objectWithAllEvents = {}
        selectAllFromSalaDatabase["records"] = conn.execute("Select id , type , name , address from salaDatabase ORDER  BY id desc")
        selectAllEventsThatAraInDatabase["users"] = conn.execute("Select login , email , id from USER order by id desc")
        objectWithAllEvents["events"] = conn.execute("Select name , date , time , user_id , id from Sala order by id desc")
        return template('admin', selectAllFromSalaDatabase , selectAllEventsThatAraInDatabase , objectWithAllEvents)

    @route('/<id>/update/user', method="POST")
    def updateUser(id):
        conn.execute('UPDATE user SET login = (%s), email = (%s) where id=(%s)',
            (request.forms["login"], request.forms["email"], id))
        selectAllFromSalaDatabase = {}
        selectAllEventsThatAraInDatabase = {}
        objectWithAllEvents = {}
        selectAllFromSalaDatabase["records"] = conn.execute("Select id , type , name , address from salaDatabase ORDER  BY id desc")
        selectAllEventsThatAraInDatabase["users"] = conn.execute("Select login , email , id from USER order by id desc")
        objectWithAllEvents["events"] = conn.execute("Select name , date , time , user_id , id from Sala order by id desc")
        return template('admin', selectAllFromSalaDatabase , selectAllEventsThatAraInDatabase , objectWithAllEvents)

    @route('/<id>/update/event', method="POST")
    def updateEvent(id):
        conn.execute('UPDATE sala SET name = (%s), date = (%s) , time = (%s), user_id = (%s) where id=(%s)',
            (request.forms["name"], request.forms["date"] , request.forms["time"], request.forms["user_id"], id))
        selectAllFromSalaDatabase = {}
        selectAllEventsThatAraInDatabase = {}
        objectWithAllEvents = {}
        selectAllFromSalaDatabase["records"] = conn.execute("Select id , type , name , address from salaDatabase ORDER  BY id desc")
        selectAllEventsThatAraInDatabase["users"] = conn.execute("Select login , email , id from USER order by id desc")
        objectWithAllEvents["events"] = conn.execute("Select name , date , time , user_id , id from Sala order by id desc")
        return template('admin', selectAllFromSalaDatabase , selectAllEventsThatAraInDatabase , objectWithAllEvents)

class salaDatabase(Base):
    __tablename__ = 'salaDatabase'
    id = Column("id", Integer, primary_key=True, autoincrement=True, nullable=False)
    type = Column("type", String(255))
    name = Column("name", String(255))
    address = Column("address", String(255))


Base.metadata.create_all(engine)


# error messages method

@error(403)
@error(404)
def mistake(code):
    return 'There is something wrong!'

# @error(500)
# def retard(code):
#     return "You'd better look into calendar!"


# method that loads all the data



run(host='localhost', port=8080)
