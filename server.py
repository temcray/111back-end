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

    #Validation
    existing_user = session.query(User).filter_by(username=username).first()
    if existing_user is not None:

    
        return jsonify({"massage": "Username already Taken"})



    print(data)
    print(username)
    print(password)


    new_user = User(username=username, password=password ) #Create new User
    session.add(new_user) #add to session
    session.commit() #commit to DB

    return jsonify({"message": "User reqistered succesfully"}), 201


#Login 
@app.post("/api/login")
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password required"}), 400
    
    user = session.query(User).filter_by(username=username).first()

    if user and user.password == password:
        return jsonify({"message": "Login successfully"}), 200 # ok
    
    return jsonify({"message": "Invaild"}), 401 # 
    #return "401"

    #get user by id
@app.get("/api/users/<user_id>")
def get_user(user_id):
        user = session.query(User).filter_by(id=user_id).first() 

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_data = {"id": user.id, "username": user.username}
        return jsonify(user_data), 200

#Update a user
@app.put("/api/users/<user_id>")
def update_user(user_id):
    data = request.get_json()
    new_username = data.get("username")
    new_password = data.get("password")


    user =session.query(User).filter_by(id=user_id).first()


    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if new_username:
        user.username = new_username
    if new_password:
        user.password = new_password
    session.commit()
    return jsonify({"message": "User updated successfully"}), 200 


#delete user
@app.delete("/api/users/<user_id>")
def delete_user(user_id):
    user = session.query(User).filter_by(id=user_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404
    
    session.delete(user)
    session.commit()

    return jsonify({"message": "User deleted successfully"}), 200


#Validate category
allowed_catalogories = {"Food", 'Education', "Entertainment"}

expenses = [
    {"id": 1, "title": "Lunch", "description": "Pizza and drink", "amount": 13.5, "category": "Food", "user_id": 101},
    {"id": 2, "title": "Book", "description": "Python Programming", "amount": 35.0, "category": "Education", "user_id": 102},
    {"id": 3, "title": "Game", "description": "Xbox 360 Gaming System", "amount": 150.0, "category": "Entertainment", "user_id": 103},
]


#Expense routes
@app.route("/api/expenses")
def add_expenses():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    amount = data.get("amount")
    category = data.get("category")
    user_id = data.get("user_id")

    if category not in add_expenses:
        return jsonify({"error": f"Invalid category {category}"}), 400
    
    new_expense = add_expenses(title=title, description=description, amount=amount, category=category, user_id=user_id) #Create new user
    session.add(new_expense) #add to session
    session.commit() #commit to DB

    return jsonify({"message": "Expense added successfully"}), 201


#Get expense
@app.get("/api/expenses/<expense_id>")
def get_expense(expense_id):
    expense = next((exp for exp in expense if exp["id"] == expense_id), None)
    if not expense: 
        return jsonify({"error": f"Expense with ID {expense_id} not found"}), 404
    return jsonify(expense), 200


# Put expense
@app.put("/api/expenses/<int:expense_id>")
def update_expense(expense_id):
    expense = next((exp for exp in expense if exp["id"] == expense_id), None)
    if not expense:
        return jsonify({"error": f"Expense with ID {expense_id} not found"}), 404
    
    if "title" in expense:
        expense["title"] = expense["title"]
    if "description" in expense:
        expense["description"] = expense["description"]
    if "amount" in expense:
        expense["amount"] = expense["amount"]
    if "category" in expense:
        if expense["category"] not in allowed_catalogories:
            return jsonify({"error": f"Invalid category {expense["category"]}. Allowed: {allowed_catalogories}"}), 400
        expense["category"] = expense["category"]
    if "user_id" in expense:
        expense["user_id"] = expense["user_id"]


    return jsonify({"message": "Expense updated successfully", "expense": expense}), 200


# Delete expense
@app.delete("/api/expenses/<int:expense_id>")
def delete_expense(expense_id):
    global add_expenses
    expense = next((exp for exp in expense if exp["id"] == expense_id), None)
    if not expense:
        return jsonify({"error": f"Expense with ID {expense_id} not found"}), 404
    
    expense = [exp for exp in expense if exp["id"]!= expense_id]
    return jsonify({"message": f"Expense with ID {expense_id} deleted successfully"}), 200

    
#Ensres the server runs only when this script is executed directly
if __name__== "__main__":
    app.run(debug=True)