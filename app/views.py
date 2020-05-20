"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask import Flask, escape, request
from app.forms import LoginForm, Registration, AddFriend, newGroup, joinGrp, createPost, NewPost, ProPicUpload, CEForm
from werkzeug.utils import secure_filename

import mysql.connector
import os
import datetime


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
    if 'username' in session:
        mycursor.execute(
            'SELECT * FROM photo WHERE photo_id = %s', (session['id'],))
        profile_picture = mycursor.fetchone()

        return render_template('home.html', profile_picture=profile_picture)
    else:
        return render_template('home.html')


@app.route('/grpProfile/<grp_id>', methods=['POST', 'GET'])
def grpProfile(grp_id):
    """Render website's group profile page."""
    form = NewPost()
    uploadForm = ProPicUpload()
    ceForm = CEForm()
    session['Group_ID'] = grp_id

    mycursor.execute(
        'SELECT * FROM photo WHERE photo_id = %s', (session['id'],))
    profile_picture = mycursor.fetchone()

    mycursor.execute(
        'SELECT * FROM group_photo WHERE photo_id = %s', (session['Group_ID'],))
    group_picture = mycursor.fetchone()

    mycursor.execute(
        'SELECT * FROM grouped WHERE grp_id = %s', (grp_id,))
    group = mycursor.fetchone()

    mycursor.execute(
        'SELECT posts.post_id, createdPost_date, description, filename FROM create_grp_post join posts on posts.post_id=create_grp_post.post_id and grp_id = %s ORDER BY posts.post_id DESC', (session['Group_ID'],))
    g_posts = mycursor.fetchall()

    mycursor.execute(
        'SELECT DISTINCT username, user.user_id from user join ucg on ucg.user_id = user.user_id or ucg.ce_id=user.user_id where grp_id = %s and ucg.user_id = %s or ce_id = %s', (session['Group_ID'], session['id'], session['id'],))
    valid_editors = mycursor.fetchall()

    if valid_editors:
        # Upload Group Profile Picture
        if request.method == 'POST' and uploadForm.validate_on_submit():
            photo = request.files['profPic']
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if group_picture is None:
                sql = "INSERT INTO group_photo ( photo_id, photo_name) VALUES (%s, %s)"
                val = (session['Group_ID'], filename)
                mycursor.execute(sql, val)
                mydb.commit()
            else:
                sql = "UPDATE group_photo SET photo_name=%s WHERE photo_id = %s"
                val = (filename, session['Group_ID'])
                mycursor.execute(sql, val)
                mydb.commit()

            return redirect(url_for('grpProfile', grp_id=session['Group_ID']))

        # Create a Post
        if request.method == 'POST' and form.validate_on_submit():
            # Get file data and save to your uploads folder
            if form.photo.data:  # for both text and photo
                photo = request.files['photo']
                description = form.description.data

                filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                x = datetime.datetime.now()

                sql = "INSERT INTO posts ( createdPost_date, description, filename) VALUES (%s, %s, %s)"
                val = (x, description, filename)

                mycursor.execute(sql, val)
                mydb.commit()

                sql = "INSERT INTO create_Grp_Post (ce_id, grp_id, post_id) VALUES (%s, %s, %s)"
                val = (session['id'], session['Group_ID'], mycursor.lastrowid)

                mycursor.execute(sql, val)
                mydb.commit()

            else:  # only posts text
                description = form.description.data

                sql = "INSERT INTO posts ( createdPost_date, description) VALUES (%s, %s)"
                val = (datetime.datetime.now(), description)

                mycursor.execute(sql, val)
                mydb.commit()
                sql = "INSERT INTO create_Grp_Post (ce_id, grp_id, post_id) VALUES (%s, %s, %s)"
                val = (session['id'], session['Group_ID'], mycursor.lastrowid)

                mycursor.execute(sql, val)
                mydb.commit()

            return redirect(url_for('grpProfile', grp_id=session['Group_ID']))

        # Add a Content Editor
        if request.method == 'POST' and ceForm.validate_on_submit():
            username = ceForm.CEusername.data
            mycursor.execute(
                'SELECT * from user WHERE username = %s', (username,))
            new_editor = mycursor.fetchone()

            if new_editor is not None:
                sql = "INSERT INTO ucg (user_id, ce_id, grp_id) VALUES (%s, %s, %s)"
                val = (session.get('id'), new_editor[0], grp_id)

                mycursor.execute(sql, val)
                mydb.commit()

                flash('Successfully registered', 'success')

                mycursor.execute(
                    'SELECT username from user join ucg on ucg.ce_id = user.user_id WHERE grp_id = %s', (grp_id,))
                editors = mycursor.fetchall()
            else:
                flash('No such user', 'error')

    return render_template('group_profile.html', uploadForm=uploadForm, form=NewPost(), ceForm=CEForm(), profile_picture=profile_picture, grp_id=grp_id, group=group, valid_editors=valid_editors, group_picture=group_picture, g_posts=g_posts)


@app.route('/administrator/')
def admin():
    """Render the website's admin page."""
    mycursor = mydb.cursor()
    mycursor.execute('SELECT * FROM user WHERE username != %s', ('admin',))
    allusers = mycursor.fetchall()

    if 'username' in session and session['username'] == 'admin':
        return render_template('admin.html', allusers=allusers)
    else:
        return render_template('home.html')


@app.route('/administrator/friendreport/<user_id>')
def friendreport(user_id):
    """Render the website's admin friend report page."""

    mycursor = mydb.cursor()

    mycursor.execute(
        'SELECT * FROM friend_of JOIN user on friend_of.friend_id = user.user_id WHERE friend_of.user_id = %s', (user_id,))
    allfriends = mycursor.fetchall()

    if 'username' in session and session['username'] == 'admin':
        return render_template('friend_report.html', allfriends=allfriends)
    else:
        return render_template('home.html')


@app.route('/administrator/postreport/<user_id>')
def postreport(user_id):
    """Render the website's admin post report page."""

    mycursor = mydb.cursor()

    mycursor.execute('SELECT posts.post_id, createdPost_date, description, filename FROM posts join create_post on create_post.post_id=posts.post_id and user_id = %s ORDER BY posts.post_id DESC', (user_id,))
    allposts = mycursor.fetchall()

    if 'username' in session and session['username'] == 'admin':
        return render_template('post_report.html', allposts=allposts)
    else:
        return render_template('home.html')


@app.route('/administrator/commentreport/<user_id>')
def commentreport(user_id):
    """Render the website's admin comment report page."""

    mycursor = mydb.cursor()

    mycursor.execute(
        'SELECT posts.post_id, comment FROM cv_post join posts on cv_post.post_id=posts.post_id where user_id = %s ORDER BY posts.post_id DESC', (user_id,))
    allcomments = mycursor.fetchall()

    if 'username' in session and session['username'] == 'admin':
        return render_template('comment_report.html', allcomments=allcomments)
    else:
        return render_template('home.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    """Render website's Registration Form."""
    form = Registration()
    mycursor = mydb.cursor()

    if request.method == "POST" and form.validate_on_submit():
        f_name = form.f_name.data
        l_name = form.l_name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data

        mycursor.execute('SELECT * FROM user WHERE username = %s', (username,))
        user = mycursor.fetchone()
        if user:
            flash(u'This username is already taken', 'error')
        else:
            sql = "INSERT INTO user (f_name, l_name, username, email, password) VALUES (%s, %s, %s, %s, AES_ENCRYPT (%s, 'key'))"
            val = (f_name, l_name, username,
                   email, password)

            mycursor.execute(sql, val)
            mydb.commit()

            flash('Successfully registered', 'success')

            return redirect(url_for("login"))

    # Flash errors in form and redirects to Register Form
    flash_errors(form)
    return render_template('register.html', form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    mycursor = mydb.cursor()

    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        # Check if user exists using MySQL
        mycursor.execute(
            "SELECT * FROM user WHERE username = %s and password = AES_DECRYPT(%s, 'key')", (username, password))
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
            if session['username'] == 'admin':
                return redirect(url_for("admin"))
            else:
                return redirect(url_for("dashboard"))
        else:
            # user does not exist or username/password incorrect
            flash(u'Invalid Credentials', 'error')

    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('logged_in', None)
    session.pop('id', None)
    session.pop('username', None)
    # flash('Logged out Succesfully', 'success')

    # Redirect to home page
    return redirect(url_for('home'))


@app.route('/addfriend', methods=['GET', 'POST'])
def addfriend():
    # logs = LoginForm()
    if 'username' in session:
        form = AddFriend()
        mycursor = mydb.cursor()

        mycursor.execute(
            'SELECT * FROM photo WHERE photo_id = %s', (session['id'],))
        profile_picture = mycursor.fetchone()

        # Check if "username" POST requests exist
        if request.method == 'POST' and 'username' in request.form:
            if form.validate_on_submit():
                # Create variables for easy access
                username = request.form['username']
                type = request.form['type']

                # Check if user exists using MySQL
                mycursor.execute(
                    'SELECT * FROM user WHERE username = %s', (username,))
                # Fetch one record and return result
                friend = mycursor.fetchone()
                if friend:
                    sql = "INSERT INTO friend_of (user_id, friend_id, type) VALUES (%s, %s, %s)"
                    val = (session['id'], friend[0], type)

                    mycursor.execute(sql, val)
                    mydb.commit()

                    # LAZY WAY OF ENSURING FRIENDS REFLECTS ON BOTH USERS
                    sql = "INSERT INTO friend_of (user_id, friend_id, type) VALUES (%s, %s, %s)"
                    val = (friend[0], session['id'], type)

                    mycursor.execute(sql, val)
                    mydb.commit()

                    flash('Friend Added', 'success')
                else:
                    # user does not exist or username/password incorrect
                    flash('User does not exist', 'error')
            else:
                flash_errors(form)

        return render_template('addfriend.html', form=form, profile_picture=profile_picture)
    else:
        return render_template('login.html', form=LoginForm())


@app.route('/Groups', methods=['GET', 'POST'])
def createGrp():
    if 'username' in session:
        form = newGroup()
        mycursor1 = mydb.cursor()

        mycursor.execute(
            'SELECT DISTINCT grp_name, grouped.grp_id from join_group join grouped on join_group.grp_id = grouped.grp_id where user_id = %s', (session['id'],))
        groups = mycursor.fetchall()

        mycursor.callproc('GetGroupAmount', (session['id'], ))
        for result in mycursor.stored_results():
            result_args = result.fetchall()

        mycursor.execute(
            'SELECT * FROM photo WHERE photo_id = %s', (session['id'],))
        profile_picture = mycursor.fetchone()

        # Check if "username" POST requests exist
        if request.method == 'POST' and form.validate_on_submit():
            # Create variables for easy access
            gname = request.form['grp_name']
            purpose = request.form['purpose']
            ce = request.form['CEusername']

            # Check if user exists using MySQL
            mycursor.execute(
                'SELECT * FROM grouped WHERE grp_name = %s', (gname,))
            # Fetch one record and return result
            gp = mycursor.fetchone()
            if gp is None:
                mycursor1.execute(
                    'SELECT * FROM user WHERE username = %s', (ce,))
                # Fetch one record and return result
                content_editor = mycursor1.fetchone()
                if content_editor:
                    sql = "INSERT INTO grouped (grp_name, purpose) VALUES (%s, %s)"
                    val = (gname, purpose)

                    mycursor.execute(sql, val)
                    mydb.commit()

                    sql = "INSERT INTO ucg (user_id, ce_id, grp_id) VALUES (%s, %s, %s)"
                    val = (session['id'], content_editor[0],
                           mycursor.lastrowid)

                    mycursor1.execute(sql, val)
                    mydb.commit()

                    sql = "INSERT INTO join_group (grp_id, user_id) VALUES (%s, %s)"
                    val = (mycursor.lastrowid, session['id'])

                    mycursor1.execute(sql, val)
                    mydb.commit()

                    sql = "INSERT INTO join_group (grp_id, user_id) VALUES (%s, %s)"
                    val = (mycursor.lastrowid, content_editor[0])

                    mycursor1.execute(sql, val)
                    mydb.commit()
                    flash('Group Created', 'success')
                    return redirect(url_for('createGrp'))
                else:
                    flash('Username does not exist', 'error')
            else:
                # user does not exist or username/password incorrect
                flash(u'Group Already Exists', 'error')

        return render_template('createGrp.html', form=form, profile_picture=profile_picture, groups=groups, result_args=result_args[0][0])
    else:
        return render_template('login.html', form=LoginForm())


@app.route('/joinGroup', methods=['GET', 'POST'])
def joinGroup():
    if 'username' in session:
        form = joinGrp()
        mycursor1 = mydb.cursor()

        mycursor.execute(
            'SELECT * FROM photo WHERE photo_id = %s', (session['id'],))
        profile_picture = mycursor.fetchone()

        # Check if "username" POST requests exist
        if request.method == 'POST' and form.validate_on_submit():
            # Create variables for easy access
            gp = request.form['grp_name']

            # Check if group exists using MySQL
            mycursor.execute(
                'SELECT * FROM grouped WHERE grp_name = %s', (gp,))
            # Fetch one record and return result

            existing_gp = mycursor.fetchone()

            if existing_gp:
                mycursor1.execute(
                    'SELECT * FROM join_group WHERE grp_id = %s and user_id = %s', (existing_gp[0], session['id']))

                member_of_grp = mycursor1.fetchone()
                if not member_of_grp:
                    sql = "INSERT INTO join_group (grp_id, user_id) VALUES (%s, %s)"
                    val = (existing_gp[0], session['id'])

                    mycursor.execute(sql, val)
                    mydb.commit()

                    flash('You have been added', 'success')
                else:
                    flash('You are already a member of this group')
            else:
                # Group does not exist
                flash(u'Group does not exist', 'error')

        return render_template('joingrp.html', form=form, profile_picture=profile_picture)
    else:
        return render_template('login.html', form=LoginForm())


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


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    form = NewPost()

    mycursor.execute(
        'select grp_name, ucg.grp_id from grouped join ucg on grouped.grp_id=ucg.grp_id where ucg.user_id = %s', (session['id'],))
    groups = mycursor.fetchall()

    if groups == []:
        mycursor.execute(
            'select grp_name, join_group.grp_id from grouped join join_group on grouped.grp_id=join_group.grp_id where join_group.user_id = %s', (session['id'],))
        groups = mycursor.fetchall()

    mycursor.execute(
        'SELECT * FROM photo WHERE photo_id = %s', (session['id'],))
    profile_picture = mycursor.fetchone()
    mycursor.execute(
        'SELECT * FROM posts join create_post on create_post.post_id=posts.post_id join friend_of on friend_of.friend_id = create_post.user_id join user on user.user_id = friend_of.friend_id WHERE friend_of.user_id = %s ORDER BY posts.createdPost_date DESC', (session['id'],))
    allposts = mycursor.fetchall()

    if request.method == 'POST' and form.validate_on_submit():
        # Get file data and save to your uploads folder
        if form.photo.data:  # for both text and photo
            photo = request.files['photo']
            description = form.description.data

            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            x = datetime.datetime.now()

            sql = "INSERT INTO posts ( createdPost_date, description, filename) VALUES (%s, %s, %s)"
            val = (x, description, filename)

            mycursor.execute(sql, val)
            mydb.commit()

            sql = "INSERT INTO create_post (user_id, post_id) VALUES (%s, %s)"
            val = (session['id'], mycursor.lastrowid)

            mycursor.execute(sql, val)
            mydb.commit()

        else:  # only posts text
            description = form.description.data

            sql = "INSERT INTO posts ( createdPost_date, description) VALUES (%s, %s)"
            val = (datetime.datetime.now(), description)

            mycursor.execute(sql, val)
            mydb.commit()
            sql = "INSERT INTO create_post (user_id, post_id) VALUES (%s, %s)"

            val = (session['id'], mycursor.lastrowid)
            mycursor.execute(sql, val)
            mydb.commit()

            redirect(url_for('dashboard'))

    return render_template('dashboard.html', form=form, group=groups, profile_picture=profile_picture, allposts=allposts)


@app.route('/friends/')
def friends():
    """Render the website's friends page."""
    if 'username' in session:
        # We need all the user info for the user so we can display it on the profile page
        mycursor.execute(
            'select type, f_name, l_name, username, friend_of.friend_id from user join friend_of on user.user_id=friend_of.friend_id where friend_of.user_id = %s', (session['id'],))

        # Fetches all friends of the user who is logged in
        users = mycursor.fetchall()

        mycursor.execute(
            'SELECT * FROM photo WHERE photo_id = %s', (session['id'],))
        profile_picture = mycursor.fetchone()

        mycursor.callproc('GetNumberFriends', [session['id'], ])
        for result in mycursor.stored_results():
            result_args = result.fetchall()

        # Show the friends page with user info
        return render_template('friends.html', users=users, profile_picture=profile_picture, result_args=result_args[0][0])

    # User is not loggedin redirect to login page
    else:
        return redirect(url_for('login'))


@app.route('/edit/<post_id>', methods=['POST', 'GET'])
def edit_post(post_id):
    npost = NewPost()

    mycursor.execute(
        'SELECT * FROM photo WHERE photo_id = %s', (session['id'],))
    profile_picture = mycursor.fetchone()

    mycursor.execute(
        'SELECT * FROM posts WHERE post_id = %s', (post_id,))
    oldpost = mycursor.fetchone()

    if request.method == 'POST' and npost.validate_on_submit():
        # Get file data and save to your uploads folder
        if npost.photo.data:  # for both text and photo
            photo = request.files['photo']
            description = npost.description.data

            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            sql = "UPDATE posts SET description = %s, filename = %s WHERE post_id = %s"
            val = (description, filename, post_id)

            mycursor.execute(sql, val)
            mydb.commit()

            return redirect(url_for('profile'))

        else:  # only posts text
            description = npost.description.data

            sql = "UPDATE posts SET description = %s WHERE post_id = %s"
            val = (description, post_id)
            mycursor.execute(sql, val)
            mydb.commit()

            return redirect(url_for('profile'))

    return render_template('edit_post.html', profile_picture=profile_picture, npost=npost, oldpost=oldpost)


@app.route('/profile/', methods=['POST', 'GET'])
def profile():
    """Render website's home page."""
    npost = NewPost()
    friend_post = NewPost()
    uploadForm = ProPicUpload()

    mycursor.execute(
        'SELECT posts.post_id, createdPost_date, description, filename FROM posts join create_post on create_post.post_id=posts.post_id and user_id = %s ORDER BY posts.post_id DESC', (session['id'],))
    posts = mycursor.fetchall()

    mycursor.execute(
        'SELECT * FROM photo WHERE photo_id = %s', (session['id'],))
    profile_picture = mycursor.fetchone()

    mycursor.execute(
        'SELECT * from posts join cv_post on posts.post_id=cv_post.post_id join user on user.user_id = cv_post.user_id')
    comments = mycursor.fetchall()

    if request.method == 'POST' and uploadForm.validate_on_submit():
        photo = request.files['profPic']
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if profile_picture is None:
            sql = "INSERT INTO photo ( photo_id, photo_name) VALUES (%s, %s)"
            val = (session['id'], filename)
        else:
            sql = "UPDATE photo SET photo_name=%s WHERE photo_id = %s"
            val = (filename, session['id'])
        mycursor.execute(sql, val)
        mydb.commit()

        return redirect(url_for('profile'))

    if request.method == 'POST' and npost.validate_on_submit():
        # Get file data and save to your uploads folder
        if npost.photo.data:  # for both text and photo
            photo = request.files['photo']
            description = npost.description.data

            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            x = datetime.datetime.now()

            sql = "INSERT INTO posts ( createdPost_date, description, filename) VALUES (%s, %s, %s)"
            val = (x, description, filename)

            mycursor.execute(sql, val)
            mydb.commit()

            sql = "INSERT INTO create_post (user_id, post_id) VALUES (%s, %s)"
            val = (session['id'], mycursor.lastrowid)

            mycursor.execute(sql, val)
            mydb.commit()

        else:  # only posts text
            description = npost.description.data

            sql = "INSERT INTO posts ( createdPost_date, description) VALUES (%s, %s)"
            val = (datetime.datetime.now(), description)

            mycursor.execute(sql, val)
            mydb.commit()
            sql = "INSERT INTO create_post (user_id, post_id) VALUES (%s, %s)"

            val = (session['id'], mycursor.lastrowid)
            mycursor.execute(sql, val)
            mydb.commit()

        return redirect(url_for('profile'))
    return render_template('profile.html', npost=NewPost(), uploadForm=ProPicUpload(), filename='', posts=posts, profile_picture=profile_picture, friend_post=NewPost(), username=session.get('username'))


@app.route('/comment<post_id>/', methods=['POST', 'GET'])
def comments(post_id):
    friend_post = NewPost()
    if request.method == 'POST' and friend_post.validate_on_submit():
        description = friend_post.description.data

        sql = "INSERT INTO cv_post (user_id, post_id,comment) VALUES (%s, %s, %s)"
        val = (session['id'], post_id, description)

        mycursor.execute(sql, val)
        mydb.commit()

        return redirect(url_for('dashboard'))


@app.route('/<username>Profile/', methods=['POST', 'GET'])
def friend_profile(username):
    """Render website's home page."""
    npost = NewPost()
    friend_post = NewPost()
    uploadForm = ProPicUpload()

    mycursor.execute('SELECT * FROM user WHERE username = %s', (username,))
    friend = mycursor.fetchone()

    mycursor.execute(
        'SELECT * FROM photo WHERE photo_id = %s', (session['id'],))
    profile_picture = mycursor.fetchone()

    mycursor.execute(
        'SELECT posts.post_id, createdPost_date, description, filename FROM posts join create_post on create_post.post_id=posts.post_id and user_id = %s ORDER BY posts.post_id DESC', (friend[0],))
    posts = mycursor.fetchall()

    mycursor.execute(
        'SELECT * from posts join cv_post on posts.post_id=cv_post.post_id join user on user.user_id = cv_post.user_id')
    comments = mycursor.fetchall()

    mycursor.execute('SELECT * FROM photo WHERE photo_id = %s', (friend[0],))
    friend_profile_picture = mycursor.fetchone()

    #     return redirect(url_for('friend_profile', username = username))
    return render_template('profile.html', npost=NewPost(), filename='', posts=posts, friend=friend, profile_picture=profile_picture, uploadForm=ProPicUpload(), friend_post=NewPost(), username=username, friend_profile_picture=friend_profile_picture, comments=comments)


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
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")
