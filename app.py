import database as db

import datetime
from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.exceptions import abort
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'blablablablablablablabla'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///purty.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init(app)

def get_req_hand_cnt(user_id):
    return db.get_all_requests_for_host_user_count(user_id)

def get_req_cnt(user_id):
    return db.get_all_requests_count(user_id)

def get_inv_cnt(user_id):
    return db.get_all_invites_count(user_id)

app.jinja_env.globals.update(get_user_name=db.get_user_name, get_req_hand_cnt=get_req_hand_cnt, get_req_cnt=get_req_cnt, get_inv_cnt=get_inv_cnt)

@app.before_request
def check_session():
    if 'user_id' in session:
        #if somebody tries to access with a session that corresponds to a user
        #that no longer exists, just log them out
        if db.user_exists(session['user_id']) == False:
            session.pop('user_id')

@app.route('/')
def index():
    users = db.get_all_users()
    return render_template('index.html', users=users)

@app.route('/u/<string:user_id>')
def user(user_id):
    user = db.get_user(user_id)
    print(user, file=sys.stderr)
    if user is None:
        abort(404)
    return render_template('user.html', user=user)

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']

        if not email:
            flash('Email is required!')
        else:
            user = db.get_user_from_email(email)
            if user is None:
                flash('User not Found!')
            else:
                session['user_id'] = user['user_id']
            return redirect(url_for('index'))
    else:
        if 'user_id' in session:
            return redirect(url_for('index'))
        else:
            return render_template('login.html')

@app.route('/logout', methods=('GET', 'POST'))
def logout():
    if request.method == 'POST':
        if 'user_id' in session:
            session.pop('user_id')
        return redirect(url_for('login'))
    else:
        if 'user_id' in session:
            return render_template('logout.html')
        else:
            return redirect(url_for('login'))

@app.route('/signup', methods=('GET', 'POST'))
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        age = request.form['age']

        if not name:
            flash('Name is required!')
        elif not email:
            flash('Email is required!')
        elif not age:
            flash('Age is required!')
        else:
            user_id = db.insert_user(name, email, age)
            session['user_id'] = user_id
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))

@app.route('/parties')
def parties():
    parties = db.get_all_parties_with_address()
    return render_template('parties.html', parties=parties)

@app.route('/p/<string:party_id>')
def party(party_id):
    party = db.get_party(party_id)
    users = db.get_party_users(party_id)
    location = db.get_location(party_id)
    
    # print(location, file=sys.stderr)

    current_user_is_host = False
    if 'user_id' in session:
    	current_user_is_host = db.is_host_of_party(session['user_id'], party_id)
    return render_template('party.html', party=party, users=users, location=location, current_user_is_host=current_user_is_host)

@app.route('/p/<string:party_id>/edit_party', methods=('GET', 'POST'))
def edit_party(party_id):
    party = db.get_party(party_id)
    location = db.get_location(party_id)

    if request.method == 'POST':
        current_user_is_host = False
        if 'user_id' in session:
    	    current_user_is_host = db.is_host_of_party(session['user_id'], party_id)    
    	
        name = request.form['name']
        date = request.form['date']
        time = request.form['time']
        description = request.form['description']
        loc = request.form['loc']
        
        if current_user_is_host == False:
    	    flash('Must be host to edit!')
        if not name:
            flash('Name is required!')
        elif not date:
            flash('Date is required!')
        elif not time:
            flash('Time is required!')
        elif not description:
            flash('Description is required!')
        elif not loc:
            flash('Location is required!')
        else:
            db.update_party(party_id, name, date, time, description, loc)
            return redirect(url_for('party', party_id=party_id))

    users = db.get_party_users(party_id)
    return render_template('edit_party.html', party=party, location=location, users=users)
    
@app.route('/new_party', methods=('GET', 'POST'))
def new_party():
    
    
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        time = request.form['time']
        description = request.form['description']
        location_id = request.form['location_id']
        coming_cnt = 0
        likes_cnt = 0

        invitation_date = datetime.date.today().strftime("%m/%d/%y")
        
        users = db.get_all_users()
        invite_list = []
        host_list = []
        for user in users:
            user_id = user.user_id
            if request.form.get('invites') != None:
                if str(user_id) in request.form.getlist('invites'):
                    invite_list.append(user) 
            if request.form.get('hosts') != None:
                if str(user_id) in request.form.getlist('hosts'):
                    host_list.append(user) 
                    # print(user['user_id'], file=sys.stderr)
               
        if [x for x in (name, date, time, description, location_id) if not x]:
            flash('Fill out all forms!')
        elif 'user_id' not in session:
            flash('Please login to create a new party!')
        else:
            party_id = db.insert_party(name, date, time, description, location_id, len(invite_list), coming_cnt, likes_cnt)
            
            db.insert_host(party_id, session['user_id'])
            for user in host_list:
                host_id = db.insert_host(party_id, user.user_id)
            flash('Party added!')
            for user in invite_list:
                db.insert_invite(party_id, user.user_id, invitation_date, '1/1/1', 'pending')
                
            return redirect(url_for('parties'))
            
    users = db.get_all_users()
    return render_template('new_party.html', users=users)

@app.route('/p/<string:party_id>/like', methods=('GET', 'POST'))
def like_party(party_id):
    
    if request.method == 'POST':
        if 'user_id' in session:
            db.like_party(party_id, session['user_id'])
        else:
            flash('Please login to like!')
        
    return redirect(url_for('parties'))
    
@app.route('/p/<string:party_id>/delete', methods=('GET', 'POST'))
def delete_party(party_id):
    
    if request.method == 'POST':
        if 'user_id' in session:
            db.delete_party(party_id)
            db.delete_all_hosts(party_id)
            return redirect(url_for('parties'))
    party = db.get_party(party_id)        
    user = db.get_host_account(party_id)            
    return render_template('party.html', party=party, user=user)

@app.route('/p/<string:party_id>/set_host/<string:user_id>/<string:make_host>', methods=('POST',))
def set_party_host(party_id, user_id, make_host):
    
    current_user_is_host = False
    if 'user_id' in session:
    	current_user_is_host = db.is_host_of_party(session['user_id'], party_id)
    
    if current_user_is_host == False:
        flash("Only party hosts can change user's host status")
    else:
        if(make_host == '1'):
            db.insert_host(party_id, user_id)
            db.decrement_coming(party_id, user_id)
        else:
            db.delete_host(party_id, user_id)
    return redirect(url_for('edit_party', party_id=party_id))
    

@app.route('/p/<string:party_id>/request', methods=('GET', 'POST'))
def request_to_join(party_id):
    current_user_is_host = False
    if 'user_id' in session:
    	current_user_is_host = db.is_host_of_party(session['user_id'], party_id)

    
    if request.method == 'POST':
        if 'user_id' in session:
            user_id = session['user_id']
            if db.is_invited(party_id, user_id) == 0 and db.is_requested(party_id, user_id) == 0:
                request_date = datetime.date.today().strftime("%m/%d/%y")

                db.insert_request(party_id, user_id, request_date, '1/1/1', 'pending')
                return redirect(url_for('requests'))

            elif current_user_is_host == True:
                flash('You cannot request to join this party because you are a host')
                return redirect(url_for('party', party_id=party_id))

            else:
                flash('You cannot request to join this party because you either are invited or requested before')
                return redirect(url_for('party', party_id=party_id))
               
    return render_template('requests.html')
    
@app.route('/u/<string:user_id>/edit_user', methods=('GET', 'POST'))
def edit_user(user_id):
    user = db.get_user(user_id)

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        age = request.form['age']

        if not name:
            flash('Name is required!')
        elif not email:
            flash('Email is required!')
        elif not age:
            flash('Age is required!')
        else:
            db.update_user(user_id, name, email, age)
            return redirect(url_for('user', user_id=user_id))

    return render_template('edit_user.html', user=user)

@app.route('/u/<string:user_id>/delete_user', methods=('GET', 'POST'))
def delete_user(user_id):
    if request.method == 'POST':
        db.delete_user(user_id)
        return redirect(url_for('index'))
    else:
        return redirect(url_for('edit_user', user_id=user_id))

@app.route('/handle_requests', methods=('GET', 'POST'))
def handle_requests():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    requests = db.get_all_requests_for_host_user(user_id)
    req_cnt = len(requests)
    page_data = []
    for request in requests:
        party = db.get_party(request['party_id'])
        user = db.get_user(request['user_id'])
        page_data.append((party, request, user))

    return render_template('handle_requests.html', page_data=page_data, req_cnt=req_cnt) 
      

@app.route('/handle_requests/h_accept/<int:user_id>', methods=('GET', 'POST'))
def h_accept(user_id):
    if request.method == 'POST':
        db.accept_request(request.form['party_id'], user_id)

    return redirect(url_for('handle_requests'))

@app.route('/handle_requests/h_reject/<int:user_id>', methods=('GET', 'POST'))
def h_reject(user_id):
    if request.method == 'POST':
        db.reject_request(request.form['party_id'], user_id)
    return redirect(url_for('handle_requests'))     

@app.route('/requests', methods=('GET', 'POST'))
def requests():
    if 'user_id' not in session:
        return redirect(url_for('login')) 

    requests = db.get_all_requests(session['user_id'])

    req_cnt = len(requests)
    page_data = []
    for request in requests:
        party = db.get_party(request['party_id'])
        page_data.append((party, request))

    return render_template('requests.html', page_data=page_data, req_cnt=req_cnt)
        
@app.route('/invites', methods=('GET', 'POST'))
def invites():

    if 'user_id' not in session:
        return redirect(url_for('login')) 
    invites = db.get_all_invites(session['user_id'])

    inv_cnt = len(invites)
    page_data = []
    for invite in invites:
        party = db.get_party(invite['party_id'])
        page_data.append((party, invite))

    return render_template('invites.html', page_data=page_data, inv_cnt=inv_cnt)  

@app.route('/invites/accept', methods=('GET', 'POST'))
def accept():
    if request.method == 'POST':
        db.accept_invite(request.form['party_id'], session['user_id'])

    return redirect(url_for('invites'))

@app.route('/invites/reject', methods=('GET', 'POST'))
def reject():
    if request.method == 'POST':
        db.reject_invite(request.form['party_id'], session['user_id'])
    return redirect(url_for('invites'))

@app.route('/empty', methods=('GET', 'POST'))
def empty():
    if request.method == 'POST':
        db.empty_table(request.form['table'])
        
    return redirect(url_for('index'))          

        
        
