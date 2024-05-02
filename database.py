from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Numeric, func, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal

# Define the SQLAlchemy engine
# SQLite will create a database file if it doesn't exist
engine = create_engine('sqlite:///budgeting.db')

# Define a declarative base
Base = declarative_base()

# Create the users table
class User(Base):
    __tablename__ = 'Users'

    id = Column(String, primary_key=True, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    recoveryq1 = Column(String, nullable=False)
    recoverya1 = Column(String, nullable=False)
    recoveryq2 = Column(String, nullable=False)
    recoverya2 = Column(String, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

#Updates the password of the given userID assuming it is in the database    
def updatePassword(userID, password):
    new_password_hash = generate_password_hash(password)
    session.query(User).filter_by(id=userID).update({"password_hash": new_password_hash})
    session.commit()
    session.close()

#Returns a boolean concerning whether or not the given userID and password match an entry in the DB   
def checkLogin(userID, password):
    result = session.query(User).filter_by(id=userID).first()
    if result.check_password(password) == True:
        return True

#Returns a boolean on whether or not the recovery answers match for the given userID
def checkRecoveryAnswers(userID, answer1, answer2):
    result = session.query(User).filter_by(id=userID).first()
    if result.recoverya1 == answer1 and result.recoverya2 == answer2:
        return True
    else:
        return False
    
#Returns the two recovery questions chosen by the given userID
def getRecoveryQuestions(userID):
    result = session.query(User).filter_by(id=userID).first()
    answers = [result.recoveryq1, result.recoveryq2]
    return answers

#Creates the Budgeting Data table in the DB
class BudgetData(Base):
    __tablename__ = 'BudgetData'

    id = Column(String, ForeignKey('Users.id'), primary_key=True, nullable=False)
    dataType = Column(String, primary_key=True, nullable=False)
    needs = Column(Numeric(scale=2))
    wants = Column(Numeric(scale=2))
    savings = Column(Numeric(scale=2))




# Create the database and tables
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

#Creates a new user entry in the User table with the given values
def create_new_user(userID, password, recoveryq1, recoverya1, recoveryq2, recoverya2):
    new_user = User(id=userID,
                    password_hash=password,
                    recoveryq1=recoveryq1,
                    recoverya1=recoverya1,
                    recoveryq2=recoveryq2,
                    recoverya2=recoverya2)
    new_user.set_password(password)
    session.add(new_user)
    session.commit()
    session.close()
    create_new_user_data(userID)

#Creates blank entries in the BudgetData table for the given user
def create_new_user_data(id):
    new_user_data = BudgetData(id=id,
                               dataType="m1")
    session.add(new_user_data)
    new_user_data = BudgetData(id=id,
                               dataType="m2")
    session.add(new_user_data)
    new_user_data = BudgetData(id=id,
                               dataType="m3")
    session.add(new_user_data)
    new_user_data = BudgetData(id=id,
                               dataType="m4")
    session.add(new_user_data)
    new_user_data = BudgetData(id=id,
                               dataType="m5")
    session.add(new_user_data)
    new_user_data = BudgetData(id=id,
                               dataType="m6")
    session.add(new_user_data)
    new_user_data = BudgetData(id=id,
                               dataType="m7")
    session.add(new_user_data)
    new_user_data = BudgetData(id=id,
                               dataType="m8")
    session.add(new_user_data)
    new_user_data = BudgetData(id=id,
                               dataType="m9")
    session.add(new_user_data)
    new_user_data = BudgetData(id=id,
                               dataType="m10")
    session.add(new_user_data)
    new_user_data = BudgetData(id=id,
                               dataType="m11")
    session.add(new_user_data)
    new_user_data = BudgetData(id=id,
                               dataType="m12")
    session.add(new_user_data)
    new_user_data = BudgetData(id=id,
                               dataType="LT")
    session.add(new_user_data)
    session.commit()
    session.close()

#Shifts the months recorded for the given user in the BudgetData table to prepare for a new month to be entered
def shift_months(userID):
    old_values = [None, None, None]
    for i in range(12):
        new_string = "m" + str(i + 1)
        values_to_copy = old_values[:]
        result = session.query(BudgetData).filter_by(id=userID, dataType=new_string).first()
        old_values = [result.needs, result.wants, result.savings]
        session.query(BudgetData).filter_by(id=userID, dataType=new_string).update(
            {"needs": values_to_copy[0], "wants": values_to_copy[1], "savings": values_to_copy[2]}
        )
        if old_values[0] == None:
            break
    session.commit()
    session.close()

#Records a new month with the given spending values for the given user
def recordNewMonth(userID, needs, wants, savings):
    result = session.query(BudgetData).filter_by(id=userID, dataType="m1").first()
    if result.needs != None:
        shift_months(userID)
        session.query(BudgetData).filter_by(id=userID, dataType="m1").update({"needs": needs, "wants": wants, "savings": savings})
        session.execute(
            update(BudgetData)
            .where(BudgetData.id == userID, BudgetData.dataType == "LT")
            .values(needs=BudgetData.needs + needs, wants=BudgetData.wants + wants, savings=BudgetData.savings + savings)
        )
    else:
        session.query(BudgetData).filter_by(id=userID, dataType="m1").update({"needs": needs, "wants": wants, "savings": savings})
        session.query(BudgetData).filter_by(id=userID, dataType="LT").update({"needs": needs, "wants": wants, "savings": savings})
    session.commit()
    session.close()

#Returns a list with the most recent month's needs, wants, and savings for the given user
def getLastMonth(userID):
    result = session.query(BudgetData).filter_by(id=userID, dataType="m1").first()
    month_results = [result.needs, result.wants, result.savings]
    if month_results[0] == None:
        month_results[0] = 0.00
        month_results[1] = 0.00
        month_results[2] = 0.00
    return month_results

#Returns a list with the most recent quarter's needs, wants, and savings for the given user
def getLastQuarter(userID):
    zero = Decimal('0.00')
    quarter_results = [zero, zero, zero]
    for i in range(3):
        new_string = "m" + str(i + 1)
        result = session.query(BudgetData).filter_by(id=userID, dataType=new_string).first()
        if result.needs != None:
            quarter_results[0] += result.needs
            quarter_results[1] += result.wants
            quarter_results[2] += result.savings
        else:
            break
    return quarter_results

#Returns a list with the most recent year's needs, wants, and savings for the given user
def getLastYear(userID):
    zero = Decimal('0.00')
    year_results = [zero, zero, zero]
    for i in range(12):
        new_string = "m" + str(i + 1)
        result = session.query(BudgetData).filter_by(id=userID, dataType=new_string).first()
        if result.needs != None:
            year_results[0] += result.needs
            year_results[1] += result.wants
            year_results[2] += result.savings
        else:
            break
    return year_results

#Returns a list with the lifetime needs, wants, and savings for the given user
def getLifeTime(userID):
    result = session.query(BudgetData).filter_by(id=userID, dataType="LT").first()
    lifetime_results = [result.needs, result.wants, result.savings]
    if lifetime_results[0] == None:
        lifetime_results[0] = 0.00
        lifetime_results[1] = 0.00
        lifetime_results[2] = 0.00
    return lifetime_results

#Returns a list with the most recent year's needs, wants, and savings for the given user to be used in the line graph
def getLineGraphInfo(userID):
    lineGraphInfo = []
    for i in range(12):
        new_string = "m" + str(i + 1)
        result = session.query(BudgetData).filter_by(id=userID, dataType=new_string).first()
        if result.needs != None:
            lineGraphInfo += [[result.needs, result.wants, result.savings]]
        else:
            break
    return lineGraphInfo

#Checks if the given userID exists in the User table in the DB
def checkUserNameInDB(userID):
    result = session.query(User).filter_by(id=userID).first()
    return result
