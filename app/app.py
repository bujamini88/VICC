from flask import Flask, render_template, request, redirect, url_for, session as flask_session, flash
import sqlalchemy
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from sqlalchemy import DateTime

engine = sqlalchemy.create_engine("mariadb+mariadbconnector://root:Password@db:3306/mysql")
Base = declarative_base()

class User(Base):  
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    vorname = sqlalchemy.Column(sqlalchemy.String(length=100))
    nachname = sqlalchemy.Column(sqlalchemy.String(length=100))
    email = sqlalchemy.Column(sqlalchemy.String(length=100))
    password = sqlalchemy.Column(sqlalchemy.String(length=100))



class Post(Base):
    __tablename__ = 'posts'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String(length=100))
    content = sqlalchemy.Column(sqlalchemy.String(length=1000))
    public = sqlalchemy.Column(sqlalchemy.Boolean, default=True)  # True für public, False für private Posts
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))  # User identifikation pro Post
    created_at = sqlalchemy.Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine) # DB Verbindung
db_session = Session() 

def addUser(vorname, nachname, email, password):
   newUser = User(vorname=vorname, nachname=nachname, email=email, password=password)  
   db_session.add(newUser)
   db_session.commit()

# Neuer Post
def addPost(title, content, public, user_id=None):
    newPost = Post(title=title, content=content, public=public, user_id=user_id)
    db_session.add(newPost)
    db_session.commit()

app = Flask(__name__)
app.secret_key = '94b8f1a06e8a4e09614cb6335e7af197'  # Secret für Session MGMT

@app.route("/")
def index():
    user = None
    public_posts = db_session.query(Post).filter_by(public=True).all()
    private_posts = [] 

    if 'user_id' in flask_session:
        user_id = flask_session['user_id']
        user = db_session.query(User).filter_by(id=user_id).first()
        private_posts = db_session.query(Post).filter_by(public=False).all()

    return render_template('index.html', public_posts=public_posts, private_posts=private_posts, user=user)

@app.route("/create_post", methods=["GET", "POST"])
def create_post():
    if 'user_id' not in flask_session:
        # Redirect zum Login
        return redirect(url_for("login"))
    
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        public = request.form.get("public") == 'on'
        user_id = get_logged_in_user_id() 
        addPost(title, content, public, user_id)
        return redirect(url_for("index"))
    return render_template("create_post.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = db_session.query(User).filter_by(email=email, password=password).first()
        if user:
            flask_session['user_id'] = user.id  # user ID speichern
            flash('Login Successful') 
            return redirect(url_for("index"))
        else:
            flash('Invalid Credentials')  # Error handling
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        vorname = request.form["vorname"]
        nachname = request.form["nachname"]
        email = request.form["email"]
        password = request.form["password"]
        addUser(vorname, nachname, email, password)
        flash('Signup Successful') 
        return redirect(url_for("index"))
    return render_template("signup.html")

@app.route("/logout")
def logout():
    flask_session.pop('user_id', None)  # Logout löschen der Session
    return redirect(url_for("index"))

def get_logged_in_user_id():
    return flask_session.get('user_id')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
