from flask import Flask, jsonify, request
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Date,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import date

#Create Flask app instance
app = Flask(__name__)

#Database Setup
engine = create_engine("sqlite:///budget_manager.db") #way to connect to db
Base = declarative_base() #Base to define models, all models inherit from this
Session = sessionmaker(bind=engine) #session factory, prepare sessions
session = Session() #Create a session intance to interact with the db(add,commit,...)

#Define models
class User(Base):
    __tablename__="users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(30), nullable=False)
    expenses = relationship("Expense", back_populates="user") #user.expenses, list all

    class Expense(Base):
        __tablename__ = "expenses"
        id = Column(Integer, primary_key=True)
        title = Column(String(100), nullable=False)
        description  = Column(String(200))
        amount = Column(Float, nullable=False)
        date = Column(Date, nullable=False, default=date.today)
        category = Column(Enum("Food", "Education", "Enterainment"), nullable=False)
        user_id = Column(Integer, ForeignKey("users.id")) #Foreign key to user table
        user =relationship("User", back_populates="expenses") #expenses.user.username
#Crate tables
Base.metadata.create_all(engine)

#Health check route
@app.get("/api/health")
def health_check():
    return jsonify({"status": "ok"}), 200

#User routes
@app.post("/api/register")
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    print(data)
    #print(username)
    #print(password)


    new_user = User(username=username, password=password ) #Create new User
    session.add(new_user) #add to session
    session.commit() #commit to DB

    return "Created",201


#Ensres the server runs only when this script is executed directly
if __name__== "__main__":
    app.run(debug=True)