"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, login_manager
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask import Flask, escape, request
# from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm, Registration, AddFriend, newGroup, joinGrp, createPost, NewPost, Search, ProPicUpload
from werkzeug.utils import secure_filename
import mysql.connector


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="mybook2020"
)

mycursor = mydb.cursor()

###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    srchForm = Search()
    return render_template('home.html', srchForm=srchForm)

@app.route('/2')
def index2():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    return 'You are not logged in'

@app.route('/about/')
def about():
    """Render the website's about page."""
    srchForm = Search()
    return render_template('about.html', srchForm=srchForm)


@app.route('/register', methods=["GET", "POST"])
def register():
    """Render website's Registration Form."""
    form = Registration()
    mycursor = mydb.cursor()

    if request.method == "POST"  and form.validate_on_submit():
        f_name = form.f_name.data
        l_name = form.l_name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data

        mycursor.execute('SELECT * FROM user WHERE username = %s', (username,))
        user = mycursor.fetchone()
        print(user)
        if user:
            flash(u'This username is already taken', 'error')
        else:
            sql = "INSERT INTO user (f_name, l_name, username, email, password) VALUES (%s, %s, %s, %s, %s)"
            val = (f_name, l_name, username,
                email, password)

            mycursor.execute(sql, val)
            mydb.commit()


            print("1 record inserted, ID:", mycursor.lastrowid)
            flash('Successfully registered', 'success')

            return redirect(url_for("login"))

    # Flash errors in form and redirects to Register Form
    flash_errors(form)
    return render_template('register.html', form=form, srchForm = Search())


# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    srchForm = Search()
    form = LoginForm()
    mycursor = mydb.cursor()

    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        # Check if user exists using MySQL
        mycursor.execute('SELECT * FROM user WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        user = mycursor.fetchone()
        print(user)
        # If user exists in users table in out database

        if user:
            # Create session data, we can access this data in other routes
            session['logged_in'] = True
            session['id'] = user[0]
            session['username'] = request.form['username']
            # Redirect to home page
            flash('Logged in Succesfully', 'success')
            return redirect(url_for("dashboard"))
        else:
            # user does not exist or username/password incorrect
            flash(u'Invalid Credentials', 'error')

    return render_template("login.html", form=form, srchForm=srchForm)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('logged_in', None)
   session.pop('id', None)
   session.pop('username', None)
   flash('Logged out Succesfully', 'success')

   # Redirect to home page
   return redirect(url_for('home'))

@app.route('/addfriend', methods=['GET', 'POST'])
def addfriend():
    # logs = LoginForm()
    if 'username' in session:
        form = AddFriend()  
        mycursor = mydb.cursor()

        # Check if "username" POST requests exist
        if request.method == 'POST' and 'username' in request.form:
            # Create variables for easy access
            username = request.form['username']
            type = request.form['type']

            # Check if user exists using MySQL
            mycursor.execute('SELECT * FROM user WHERE username = %s', (username,))
            # Fetch one record and return result
            friend = mycursor.fetchone()
            print(friend)
            if friend:
                sql = "INSERT INTO friend_of (user_id, friend_id, type) VALUES (%s, %s, %s)"
                val = (session['id'], friend[0], type)

                mycursor.execute(sql, val)
                mydb.commit()

                print(mycursor.rowcount, "record inserted.")
                print("1 record inserted, ID:", mycursor.lastrowid)
                flash('Friend Added', 'success')
            else:
                # user does not exist or username/password incorrect
                flash(u'User does not exist', 'error')

        return render_template('addfriend.html', form = form)
    else:
        return render_template('login.html', form = LoginForm())


@app.route('/createGroup', methods=['GET', 'POST'])
def createGrp():
    if 'username' in session:
        form = newGroup()  
        mycursor1 = mydb.cursor()

        # Check if "username" POST requests exist
        if request.method == 'POST' and form.validate_on_submit():
            # Create variables for easy access
            print("Hereeeee")
            gname = request.form['grp_name']
            purpose = request.form['purpose']
            ce = request.form['CEusername']

            # Check if user exists using MySQL
            mycursor.execute('SELECT * FROM grouped WHERE grp_name = %s', (gname,))
            # Fetch one record and return result
            gp = mycursor.fetchone()
            print(gp)
            if gp is None:
                mycursor1.execute('SELECT * FROM user WHERE username = %s', (ce,))
                # Fetch one record and return result
                content_editor = mycursor1.fetchone()
                print(content_editor)
                if content_editor:
                    sql = "INSERT INTO grouped (grp_name, purpose) VALUES (%s, %s)"
                    val = (gname, purpose)

                    mycursor.execute(sql, val)
                    mydb.commit()

                    print(mycursor.rowcount, "record inserted.")
                    print("1 record inserted, ID:", mycursor.lastrowid)

                    sql = "INSERT INTO ucg (user_id, ce_id, grp_id) VALUES (%s, %s, %s)"
                    val = (session['id'], content_editor[0], mycursor.lastrowid)

                    mycursor1.execute(sql, val)
                    mydb.commit()
                    flash('Group Created', 'success')
                else:
                    flash('Username does not exist', 'error')
            else:
                # user does not exist or username/password incorrect
                flash(u'Group Already Exists', 'error')

        return render_template('createGrp.html', form = form, srchForm = Search())
    else:
        return render_template('login.html', form = LoginForm())

@app.route('/joinGroup', methods=['GET', 'POST'])
def joinGroup():
    if 'username' in session:
        form = joinGrp()  
        mycursor1 = mydb.cursor()

        # Check if "username" POST requests exist
        if request.method == 'POST' and form.validate_on_submit():
            # Create variables for easy access
            gp = request.form['grp_name']

            # Check if group exists using MySQL
            mycursor.execute('SELECT * FROM grouped WHERE grp_name = %s', (gp,))
            # Fetch one record and return result

            existing_gp = mycursor.fetchone()
            print(existing_gp)

            if existing_gp:
                mycursor1.execute('SELECT * FROM join_group WHERE grp_id = %s and user_id = %s', (existing_gp[0], session['id']))  

                member_of_grp = mycursor1.fetchone()
                if not member_of_grp:
                    sql = "INSERT INTO join_group (grp_id, user_id) VALUES (%s, %s)"
                    val = (existing_gp[0], session['id'])

                    mycursor.execute(sql, val)
                    mydb.commit()

                    print(mycursor.rowcount, "record inserted.")
                    print("1 record inserted, ID:", mycursor.lastrowid)
                    flash('You have been added', 'success')
                else:
                    flash('You are already a member of this group')    
            else:
                # Group does not exist
                flash(u'Group does not exist', 'error')

        return render_template('joingrp.html', form = form)
    else:
        return render_template('login.html', form = LoginForm())

@app.route('/newPost')
def newPost():
    form = createPost()
    if form.validate_on_submit():
        f = form.photo.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(
            app.instance_path, 'photos', filename
        ))
        flash('Post has been added', 'success')
        return redirect(url_for('home'))
    return render_template('upload.html', form=form)
    

@app.route('/myFriends')
def myFriends():
    # Check if user is loggedin
    if 'username' in session:
        # We need all the user info for the user so we can display it on the profile page
        mycursor.execute('select type, f_name, l_name from user join friend_of on user.user_id=friend_of.friend_id where friend_of.user_id = %s', (session['id'],))

        # Fetches all friends of the user who is logged in
        users = mycursor.fetchall()

        # Show the friends page with user info
        return render_template('myfriends.html', users=users, srchForm = Search())

    # User is not loggedin redirect to login page
    else:
        return redirect(url_for('login'))

# @app.route('/profile')
# def profile():
#     # Check if user is loggedin
#     if 'username' in session:
#         # We need all the user info for the user so we can display it on the profile page
#         mycursor.execute('SELECT * FROM user WHERE id = %s', (session['id'],))
#         user = mycursor.fetchone()
#         # Show the profile page with user info
#         return render_template('profile.html', user=user)
#     # User is not loggedin redirect to login page
#     return redirect(url_for('login'))

@app.route('/myGroups', methods=['POST', 'GET'])
def myGroups():
    if 'username' in session:
        mycursor.execute('select grp_name from grouped join ucg on grouped.grp_id=ucg.grp_id where ucg.user_id = %s', (session['id'],))
        groups = mycursor.fetchall()
        print(groups)

        return render_template('myGroups.html', srchForm = Search(), groups = groups)
    else:
        return redirect(url_for('login'))

@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    srchForm = Search()
    form = NewPost()

    mycursor.execute('select grp_name from grouped join ucg on grouped.grp_id=ucg.grp_id where ucg.user_id = %s', (session['id'],))
    groups = mycursor.fetchall()
    print(groups)

    if request.method == 'POST' and srchForm.validate_on_submit():
        term = srchForm.searchTerm.data 
        results(term)
           
    if request.method == 'POST' and form.validate_on_submit():
        # Get file data and save to your uploads folder
        if form.photo.data: #for both text and photo
            photo = form.photo.data 
            description = form.description.data

            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify(message = [{"message" : "File Upload Successful", "filename": filename, "description": description}])
        
        else: #only posts text
            description = form.description.data 
            return jsonify(message = [{"message" : "Post Successful", "description": description}])
           
    return render_template('dashboard.html', form=form, srchForm = srchForm, group = groups)


@app.route('/friends/')
def friends():
    """Render the website's friends page."""
    if 'username' in session:
        # We need all the user info for the user so we can display it on the profile page
        mycursor.execute('select type, f_name, l_name from user join friend_of on user.user_id=friend_of.friend_id where friend_of.user_id = %s', (session['id'],))

        # Fetches all friends of the user who is logged in
        users = mycursor.fetchall()
        print(users)

        # Show the friends page with user info
        # return render_template('myfriends.html', users=users, srchForm = Search())
        return render_template('friends.html', srchForm = Search(), users=users)

    # User is not loggedin redirect to login page
    else:
        return redirect(url_for('login'))

    


@app.route('/results/')
def results():
    srchForm = Search()
    return render_template('results.html', srchForm = srchForm)


@app.route('/profile/')
def profile():
    """Render website's home page."""
    srchForm = Search()
    form = NewPost()
    uploadForm = ProPicUpload()

    if request.method == 'POST' and form.validate_on_submit():
        # Get file data and save to your uploads folder
        if form.photo.data: #for both text and photo
            photo = form.photo.data 
            description = form.description.data

            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify(message = [{"message" : "File Upload Successful", "filename": filename, "description": description}])
        
        else: #only posts text
            description = form.description.data 
            return jsonify(message = [{"message" : "Post Successful", "description": description}])

    if request.method == 'POST' and uploadForm.validate_on_submit(): 
        propic = uploadForm.propic.data 
        filename = secure_filename(propic.filename)
        propic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return render_template('profile.html', srchForm=srchForm, uploadForm = uploadForm, form = form)

###
# The functions below should be applicable to all Flask apps.
###


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)

# Flash errors from the form if validation fails


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    srchForm = Search()
    return render_template('404.html', srchForm=srchForm), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")
