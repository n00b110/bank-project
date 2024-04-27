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
    #username = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    recoveryq1 = Column(String, nullable=False)
    recoverya1 = Column(String, nullable=False)
    recoveryq2 = Column(String, nullable=False)
    recoverya2 = Column(String, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
def checkLogin(userID, password):
    result = session.query(User).filter_by(id=userID).first()
    if result.check_password(password) == True:
        return True

def checkRecoveryAnswers(userID, answer1, answer2):
    result = session.query(User).filter_by(id=userID).first()
    if result.recoverya1 == answer1 and result.recoverya2 == answer2:
        return True
    else:
        return False
    
def getRecoveryQuestions(userID):
    result = session.query(User).filter_by(id=userID).first()
    answers = [result.recoveryq1, result.recoveryq2]
    return answers


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


def create_new_user(userID, password, recoveryq1, recoverya1, recoveryq2, recoverya2):
    #new_id = get_next_id()
    new_user = User(id=userID,
                    #username=username,
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

def getLastMonth(userID):
    result = session.query(BudgetData).filter_by(id=userID, dataType="m1").first()
    month_results = [result.needs, result.wants, result.savings]
    if month_results[0] == None:
        month_results[0] = 0.00
        month_results[1] = 0.00
        month_results[2] = 0.00
    return month_results

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

def getLifeTime(userID):
    result = session.query(BudgetData).filter_by(id=userID, dataType="LT").first()
    lifetime_results = [result.needs, result.wants, result.savings]
    if lifetime_results[0] == None:
        lifetime_results[0] = 0.00
        lifetime_results[1] = 0.00
        lifetime_results[2] = 0.00
    return lifetime_results

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

#print(session.query(User).filter_by(id="testusername@email.com").first())
#create_new_user('CperksTestUser', 'password123', 'What is your favorite color?', 'Blue', 'What is your pet\'s name?', 'Spot') 
#session.query(User).filter_by(id=2).delete()
# recordNewMonth("testusername4@email.com", 45, 52, 3)
# recordNewMonth("testusername4@email.com", 41, 35, 24)
# recordNewMonth("testusername4@email.com", 84, 53, 78)
# recordNewMonth("testusername4@email.com", 12, 87, 45)
# recordNewMonth("testusername4@email.com", 49, 65, 74)
# recordNewMonth("testusername4@email.com", 24, 41, 32)
# recordNewMonth("testusername4@email.com", 91, 8, 1)
# recordNewMonth("testusername4@email.com", 23, 56, 95)
# recordNewMonth("testusername4@email.com", 4, 72, 12)
# recordNewMonth("testusername4@email.com", 107, 45, 99)
# recordNewMonth("testusername4@email.com", 84, 53, 78)
# recordNewMonth("testusername4@email.com", 584, 300, 245)
# recordNewMonth(1, 45, 52, 3)
# recordNewMonth(1, 58, 30, 12)
# session.commit()
# session.close()
#print(session.query(BudgetData).filter_by(id="testusername@email.com").first().needs)
#print(session.query(User).filter_by(id="CperksTestUser").first())
#print(checkLogin("test", "testpassword"))
# result = session.query(BudgetData).filter_by(id="testusername4@email.com")
# for month in result:
#     print (month.dataType, month.needs, month.wants, month.savings)

# print(getLastYear("testusername4@email.com"))
'''
session.query(BudgetData).delete()
session.commit()
session.close()
session.query(User).delete()
session.commit()
session.close()
users = session.query(User).all()
users_data = session.query(BudgetData).all()


for user in users:
    print(user.id, user.recoveryq1, user.recoverya1)
'''
'''
users_data = session.query(BudgetData).all()
for data in users_data:
    print(data.id, data.needs)
session.commit()
session.close()
'''
'''
users = session.query(User).all()
users_data = session.query(BudgetData).all()


for user in users:
    print(user.id, user.username)

for data in users_data:
    print(data.id, data.needs)


session.commit()
session.close()
print("DONE")
'''

