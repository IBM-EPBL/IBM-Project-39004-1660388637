from flask import Flask, render_template, redirect, url_for, request
from flask_db2 import DB2

app = Flask(__name__)
app.config['DB2_DATABASE'] = 'sample'
app.config['DB2_HOSTNAME'] = 'localhost'
app.config['DB2_PORT'] = 25000
app.config['DB2_PROTOCOL'] = 'TCPIP'
app.config['DB2_USER'] = 'db2admin'
app.config['DB2_PASSWORD'] = 'Harsha8'

db = DB2(app)


@app.route('/', methods=['GET', 'POST'])
def register():
    error=None
    check=False
    cheins=False
    cheex=False
    if request.method == 'POST':
        error=None
        check=False
        cheins=False
        cheex=False
        uname=request.form['name']
        passw=request.form['password']
        r_no=request.form['r_no']
        email=request.form['email']
        print(uname+'   '+passw+'  '+r_no+'  '+email)
        if (len(uname)>0 and len(passw)>0 and len(r_no)>0 and len(email)>0):
            check=True
            cur = db.connection.cursor()
            cur.execute('select * from user where username=\''+uname+'\' or email=\''+email+'\' or roll_number=\''+r_no+'\';')
            s=cur.fetchall()
            print(s)
            print('  hiiiiiiiiiiiiiiiiiiiiiiii')
            if(len(s)==0):
                cheex=True
                cheins=cur.execute('INSERT INTO user(email, username, roll_number, password) VALUES (\''+email+'\', \''+uname+'\','+r_no+', \''+passw+'\');')
        if check and cheins and cheex:
            error=error
            return redirect(url_for('login'))
        else:
            if not check:
                error = 'ENTER ALL DATA.'
            elif not cheex:
                error = 'DATA ALREADY exist.'
            else:
                error = 'TRY AFTER SOME TIME'
    return render_template('index.html', error=error)



@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    print("fff")
    if request.method == 'POST':
        cur = db.connection.cursor()
        cur.execute('select * from user;');
        #print(cur.execute('INSERT INTO user(email, username, roll_number, password) VALUES (\'harsha.yerneni1179@gmail.com\', \'Harsha\', 1905084, \'Harsha84\');'))
        s=cur.fetchall()

        cur.close()

        username=request.form['username']
        password=request.form['password']
        print(s)
        check=False
        for st in s:

            if(len(st)>3 and st[0]==username and st[3]==password):
                # 0 email 1 username 2 roll no 3 password 4 index
                check=True
                print('done')
                error='WELCOME '+st[1]+' you are LOGINED'
                break

        if check:
            error=error
            return render_template('welcome.html',error=error)
        else:
            error = 'Invalid Credentials. Please try again.'

    return render_template('login.html', error=error)
if __name__ == "__main__":
    app.run()
