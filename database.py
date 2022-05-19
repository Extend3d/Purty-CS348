
import sqlite3
import datetime
import database_orm as db_orm

def init(app):
    global db_orm
    db_orm.init(app)

def get_db_connection():
    conn = sqlite3.connect('purty.db')
    conn.row_factory = sqlite3.Row
    return conn

def user_exists(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT COUNT(*) as count FROM User WHERE user_id = ?',
                        (user_id,)).fetchone()
    conn.close()
    if user['count'] == 0:
        return False
    else:
        return True

def delete_user(user_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM User WHERE user_id = ?',
                        (user_id,))
    conn.commit()
    conn.close()

def get_user_name(user_id):
    return db_orm.User.query.filter_by(user_id = user_id)[0].name

def get_user(user_id):
    # conn = get_db_connection()
    # user = conn.execute('SELECT * FROM User WHERE user_id = ?',
    #                     (user_id,)).fetchone()
    # conn.close()
    return db_orm.User.query.filter_by(user_id = user_id)[0]

def get_user_from_email(email):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM User WHERE email = ?',
                        (email,)).fetchone()
    conn.close()
    return user

def get_party(party_id):
    party = db_orm.Party.query.filter_by(party_id = party_id)[0]
    # conn = get_db_connection()
    # party = conn.execute('SELECT * FROM Party WHERE party_id = ?',
    #                     (party_id,)).fetchone()
    # conn.close()
    if party is None:
        abort(404)
    return party

def is_host_of_party(user_id, party_id):
    conn = get_db_connection()
    is_host = conn.execute(
    """
        SELECT COUNT(*) FROM Host WHERE party_id = ? AND user_id = ?
    """, (party_id, user_id)).fetchone()[0]
    conn.close()
    if is_host == 0:
        return False
    else:
        return True

def get_party_users(party_id):
    conn = get_db_connection()
    users = conn.execute(
    """
        SELECT a.user_id AS user_id, a.is_host AS is_host, b.name AS name, b.email AS email, b.age AS age, a.reply_date as reply_date FROM (
            SELECT user_id, reply_date, MAX(is_host) AS is_host FROM (
                SELECT user_id, reply_date AS reply_date, 0 AS is_host FROM Invites WHERE answer = 1 AND party_id = ?
                UNION ALL SELECT user_id, reply_date AS reply_date, 0 AS is_host FROM Requests WHERE answer = 1 AND party_id = ?
                UNION ALL SELECT user_id, 0 AS reply_date, 1 AS is_host FROM Host WHERE party_id = ?
            )
            GROUP BY user_id
        ) a
        JOIN User b ON a.user_id = b.user_id
        ORDER BY reply_date ASC
    """, (party_id, party_id, party_id)).fetchall()
    
    conn.close()
    return users

def get_location(party_id):
    conn = get_db_connection()

    location_id = conn.execute('SELECT location_id FROM Party WHERE party_id = ?',
                        (party_id,)).fetchone()[0]
    # loc = conn.execute('SELECT * FROM Location WHERE location_id = ?',
    #                     (location_id,)).fetchone()
    loc = db_orm.Location.query.filter_by(location_id=location_id)[0]

    conn.close()
    if loc is None:
        abort(404)
    return loc

def get_location_id(party_id):
    conn = get_db_connection()

    location_id = conn.execute('SELECT location_id FROM Party WHERE party_id = ?',
                        (party_id,)).fetchone()[0]
    conn.close()
    if location_id is None:
        abort(404)
    return location_id

def insert_party(name, date, time, description, location, invited_cnt, coming_cnt, likes_cnt):
    
    conn = get_db_connection()
    cursor = conn.cursor()
    party_id = cursor.lastrowid
    if party_id == None:
        max_id = cursor.execute('SELECT MAX(party_id) FROM Party').fetchone()[0]
        if max_id == None:
            party_id = 0
        else:
            party_id = max_id + 1

    max_id = None

    
    max_id = cursor.execute('SELECT MAX(location_id) FROM Location').fetchone()[0]
    if max_id == None:
        location_id = 0
    else:
        location_id = max_id + 1

    
    cursor.execute('INSERT INTO Location VALUES (?, ?)',
                    (location_id, location))
    
    cursor.execute('INSERT INTO Party VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (party_id, name, date, time, description, location_id, invited_cnt, coming_cnt, likes_cnt))
    
    cursor.close()
    conn.commit()
    conn.close()
    return party_id
    
def delete_party(party_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    location_id = cursor.execute('SELECT location_id from Party WHERE party_id = ?', (party_id)).fetchone()[0]

    cursor.execute('DELETE FROM Location WHERE location_id = ?',
                   (location_id,))

    cursor.execute('DELETE FROM Party WHERE party_id = ?',
                   (party_id,))

    cursor.execute('DELETE FROM Invites WHERE party_id = ?',
                   (party_id,))

    cursor.execute('DELETE FROM Requests WHERE party_id = ?',
                   (party_id,))

    conn.execute('DELETE FROM Likes WHERE party_id = ?',
                   (party_id,))               
    cursor.close()
    conn.commit()
    conn.close()

def like_party(party_id, user_id):
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    liked = conn.execute('SELECT * FROM Likes WHERE party_id = ? AND user_id = ?',
                        (party_id, user_id)).fetchone()   
    if liked is not None:

        conn.execute('DELETE FROM Likes WHERE party_id = ? AND user_id = ?',
                    (party_id, user_id))
        conn.commit()
        cnt = conn.execute('SELECT likes_cnt FROM Party WHERE party_id = ?',
                            (party_id,)).fetchone()['likes_cnt']
        conn.execute('UPDATE Party SET likes_cnt = ?'
                     ' WHERE party_id = ?',
                     (cnt-1, party_id))        
        cursor.close()             
        conn.commit()
        conn.close() 
        return party_id

    cnt = conn.execute('SELECT likes_cnt FROM Party WHERE party_id = ?',
                        (party_id,)).fetchone()['likes_cnt']
                        
    conn.execute('UPDATE Party SET likes_cnt = ?'
                 ' WHERE party_id = ?',
                 (cnt+1, party_id))

    cursor.execute('INSERT INTO Likes VALUES (?, ?, ?)',
                    (party_id, user_id, 1))
                    
    cursor.close()             
    conn.commit()
    conn.close()             
    return party_id

def update_party(party_id, name, date, time, description, loc):
    conn = get_db_connection()
    conn.execute('UPDATE Party SET name = ?, date = ?, time = ?, description = ?'
                 ' WHERE party_id = ?',
                 (name, date, time, description, party_id))

    loc_id = conn.execute('SELECT location_id FROM Party WHERE party_id = ?', (party_id,)).fetchone()[0]

    conn.execute('UPDATE Location SET address = ?'
                 ' WHERE location_id = ?',
                 (loc, loc_id))

    conn.commit()
    conn.close()
    
def insert_host(party_id, user_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('INSERT INTO Host(party_id, user_id) VALUES (?, ?)',
                    (party_id, user_id))
    cursor.close()
    conn.commit()
    conn.close()

def delete_host(party_id, user_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM Host WHERE party_id=? AND user_id=?',
                    (party_id, user_id))
    cursor.close()
    conn.commit()
    conn.close()
    
def delete_all_hosts(party_id):

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Host WHERE party_id = ?',
                   (party_id,))
    cursor.close()
    conn.commit()
    conn.close() 
  
def get_all_users():
    return db_orm.User.query.all()
    
    #conn = get_db_connection()
    #users = conn.execute('SELECT * FROM User').fetchall();
    #conn.close()
    #return users

def insert_user(name, email, age):
    conn = get_db_connection()
    cursor=conn.cursor()
    cursor.execute('INSERT INTO User (name, email, age) VALUES (?, ?, ?)',
                 (name, email, age, ))
    user_id = cursor.lastrowid
    cursor.close()
    conn.commit()
    conn.close()
    return user_id

def get_all_parties_with_address():
    conn = get_db_connection()
    parties = conn.execute('SELECT party_id, name, date, time, description, location_id, invited_cnt, coming_cnt, likes_cnt, address FROM Party NATURAL JOIN Location').fetchall()
    conn.close()
    return parties

def update_user(user_id, name, email, age):
    conn = get_db_connection()
    conn.execute('UPDATE User SET name = ?, email = ?, age = ?'
                 ' WHERE user_id = ?',
                 (name, email, age, user_id))
    conn.commit()
    conn.close()

def insert_request(party_id, user_id, request_date, reply_date, answer):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Requests VALUES (?, ?, ?, ?, ?)',
                  (party_id, user_id, request_date, reply_date, answer))
    cursor.close()
    conn.commit()
    conn.close()
    return user_id

def get_all_requests(user_id):
    conn = get_db_connection()
    if user_id is None:
        requests = conn.execute('SELECT * FROM Requests').fetchall()
    else:
        requests = conn.execute('SELECT * FROM Requests WHERE user_id = ?',
                              (user_id,)).fetchall()
    conn.close()                          
    return requests

def get_all_requests_count(user_id):
    conn = get_db_connection()
    conn.execute("PRAGMA read_uncommitted = true;")

    if user_id is None:
        cnt = conn.execute('SELECT COUNT(*) FROM Requests').fetchone()[0]
    else:
        cnt = conn.execute('SELECT COUNT(*) FROM Requests WHERE user_id = ?',
                              (user_id,)).fetchone()[0]
    conn.close()                          
    return cnt

def get_all_requests_for_host_user(user_id):

    conn = get_db_connection()
    
    requests = conn.execute('SELECT r.user_id AS user_id, r.party_id AS party_id, r.request_date AS request_date, r.reply_date AS reply_date, r.answer AS answer FROM Host h JOIN Requests r ON r.party_id = h.party_id WHERE h.user_id = ? ',
                              (user_id,)).fetchall()
    conn.close()                          
    return requests

def get_all_requests_for_host_user_count(user_id):
    conn = get_db_connection()
    conn.execute("PRAGMA read_uncommitted = true;")
    
    cnt = conn.execute('SELECT COUNT(*) FROM Host h JOIN Requests r ON r.party_id = h.party_id WHERE h.user_id = ? ',
                              (user_id,)).fetchone()[0]
    conn.close()                          
    return cnt

def delete_request(party_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Requests WHERE party_id = ? and user_id = ?',
                   (party_id, user_id))
    cursor.close()
    conn.commit()
    conn.close()

def accept_request(party_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    reply_date = datetime.date.today().strftime("%m/%d/%y")

    cursor.execute('UPDATE Requests SET answer = 1, reply_date = ? WHERE party_id = ? and user_id = ?',
                   (reply_date, party_id, user_id))

    coming = conn.execute('SELECT coming_cnt FROM Party WHERE party_id = ?',
                   (party_id)).fetchone()[0]

    coming = coming + 1

    conn.execute('UPDATE Party SET coming_cnt = ? WHERE party_id = ?',
                   (coming, party_id))

    cursor.close()
    conn.commit()
    conn.close()

def reject_request(party_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    reply_date = datetime.date.today().strftime("%m/%d/%y")

    cursor.execute('UPDATE Requests SET answer = 0, reply_date = ? WHERE party_id = ? and user_id = ?',
                   (reply_date, party_id, user_id))
    cursor.close()
    conn.commit()
    conn.close()

def is_invited(party_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    is_invited_answer = cursor.execute('SELECT COUNT(*) FROM Invites WHERE party_id = ? AND user_id = ?',
                   (party_id, user_id)).fetchone()[0]
    cursor.close()
    conn.commit()
    conn.close()
    if is_invited_answer == 0:
        return False
    else:
        return True

def is_requested(party_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    is_requested_answer = cursor.execute('SELECT COUNT(*) FROM Requests WHERE party_id = ? AND user_id = ?',
                   (party_id, user_id)).fetchone()[0]
    cursor.close()
    conn.commit()
    conn.close()
    if is_requested_answer == 0:
        return False
    else:
        return True

def get_all_invites(user_id):

    conn = get_db_connection()
    if user_id is None:
        invites = conn.execute('SELECT * FROM Invites').fetchall()
    else:
        invites = conn.execute('SELECT * FROM Invites WHERE user_id = ?',
                              (user_id,)).fetchall()
    conn.close()                          
    return invites

def get_all_invites_count(user_id):
    conn = get_db_connection()
    conn.execute("PRAGMA read_uncommitted = true;")

    if user_id is None:
        cnt = conn.execute('SELECT COUNT(*) FROM Invites').fetchone()[0]
    else:
        cnt = conn.execute('SELECT COUNT(*) FROM Invites WHERE user_id = ?',
                              (user_id,)).fetchone()[0]
    conn.close()                          
    return cnt
    
def insert_invite(party_id, user_id, invitation_date, reply_date, answer):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Invites VALUES (?, ?, ?, ?, ?)',
                  (party_id, user_id, invitation_date, reply_date, answer))
    cursor.close()
    conn.commit()
    conn.close()
    return user_id

def delete_invite(party_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Invites WHERE party_id = ? and user_id = ?',
                   (party_id, user_id))
    cursor.close()
    conn.commit()
    conn.close()

def accept_invite(party_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    reply_date = datetime.date.today().strftime("%m/%d/%y")

    cursor.execute('UPDATE Invites SET answer = 1, reply_date = ? WHERE party_id = ? and user_id = ?',
                   (reply_date, party_id, user_id))

    coming = conn.execute('SELECT coming_cnt FROM Party WHERE party_id = ?',
                   (party_id)).fetchone()[0]

    coming = coming + 1

    conn.execute('UPDATE Party SET coming_cnt = ? WHERE party_id = ?',
                   (coming, party_id))
    
    cursor.close()
    conn.commit()
    conn.close()
    
def reject_invite(party_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    reply_date = datetime.date.today().strftime("%m/%d/%y")

    cursor.execute('UPDATE Invites SET answer = 0, reply_date = ? WHERE party_id = ? and user_id = ?',
                   (reply_date, party_id, user_id))
    cursor.close()
    conn.commit()
    conn.close()

def increment_coming(party_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()


    coming = conn.execute('SELECT coming_cnt FROM Party WHERE party_id = ?',
                   (party_id)).fetchone()[0]

    coming = coming + 1

    conn.execute('UPDATE Party SET coming_cnt = ? WHERE party_id = ?',
                   (coming, party_id))
    
    cursor.close()
    conn.commit()
    conn.close()

def decrement_coming(party_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()


    coming = conn.execute('SELECT coming_cnt FROM Party WHERE party_id = ?',
                   (party_id)).fetchone()[0]

    coming = coming - 1

    conn.execute('UPDATE Party SET coming_cnt = ? WHERE party_id = ?',
                   (coming, party_id))
    
    cursor.close()
    conn.commit()
    conn.close()
    
def empty_table(table):
    print(table)
    conn = get_db_connection()
    sql = "DELETE FROM " + table
    conn.execute(sql)
    conn.commit()
    conn.close()    
    
