import ibm_db
from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename

from sendgridsen import sendmail

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

print('kk')
conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=ba99a9e6-d59e-4883-8fc0-d6a8c9f7a08f.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=31321;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=mbs42408;PWD=hMYQwnOc2bfI674f",'','')
print('jj')
def getLoginDetails():
    if 'email' not in session:
        loggedIn = False
        firstName = ''
        noOfItems = 0
    else:
        loggedIn = True
        print(session['email'])
        #return "rrr","ww",12
        sql1=ibm_db.prepare(conn,'SELECT userId, firstName FROM users WHERE email = ?')
        ibm_db.execute(sql1, (session['email'],))
        userId, firstName = ibm_db.fetch_tuple(sql1)
        sql2=ibm_db.prepare(conn,'SELECT count(productId) FROM kart WHERE userId = ?')
        ss=ibm_db.execute(sql2, (userId, ))
        noOfItems = ibm_db.fetch_tuple(sql2)[0]
    return (loggedIn, firstName, noOfItems)

@app.route("/", methods=["GET", "POST"])
def root(conn=conn):
    name = request.args.get('searchQuery')
    if name:
        print(name)
        if(name.isdigit()):
            qr='SELECT productId, name, price, description, image, stock FROM products where name = \''+str(name)+'\''+' or '+'productId = '+str(name)+';'
        else:
            qr='SELECT productId, name, price, description, image, stock FROM products where name = \''+str(name)+'\';'
    else:
        qr='SELECT productId, name, price, description, image, stock FROM products'
    sql1=ibm_db.prepare(conn,qr)
    loggedIn, firstName, noOfItems = getLoginDetails()
    ibm_db.execute(sql1)
    row=ibm_db.fetch_tuple(sql1)
    itemData=[]
    while row:
        itemData.append(row)
        row=ibm_db.fetch_tuple(sql1)
    print(itemData)
    sql2=ibm_db.prepare(conn,'SELECT categoryId, name FROM categories')
    ibm_db.execute(sql2)
    row=ibm_db.fetch_tuple(sql2)
    categoryData =[]
    while row:
        categoryData.append(row)
        row=ibm_db.fetch_tuple(sql2)
    print(categoryData)
    itemData = parse(itemData)
    return render_template('home.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData)

@app.route("/add")
def admin():
    sql2=ibm_db.prepare(conn,'SELECT categoryId, name FROM categories')
    ibm_db.execute(sql2)
    row=ibm_db.fetch_tuple(sql2)
    categories =[]
    while row:
        categories.append(row)
        row=ibm_db.fetch_tuple(sql2)
    print(categories)

    return render_template('add.html', categories=categories)

@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryId = int(request.form['category'])

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename

        ex='INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (\''+str(name)+'\',\''+str(price)+'\',\''+str(description)+'\',\''+str(imagename)+'\',\''+str(stock)+'\',\''+str(categoryId)+'\');'
        print(ex)

        try:
            sql2=ibm_db.prepare(conn,'SELECT categoryId, name FROM categories')
            ibm_db.execute(sql2)
            ibm_db.commit(conn)
            msg="added successfully"
        except:
            msg="error occured"
            ibm_db.rollback(conn)
        print(msg)
        return redirect(url_for('root'))

@app.route("/remove")
def remove(conn=conn):

    sql21=ibm_db.prepare(conn,'SELECT productId, name, price, description, image, stock FROM products')
    ibm_db.execute(sql21)
    row=ibm_db.fetch_tuple(sql21)
    data =[]
    while row:
        data.append(row)
        row=ibm_db.fetch_tuple(sql21)
    print(data)
    return render_template('remove.html', data=data)

@app.route("/removeItem")
def removeItem():
    productId = request.args.get('productId')
    ex='DELETE FROM products WHERE productID = '+str(productId)

    try:
        sql221=ibm_db.prepare(conn,ex)
        ibm_db.execute(sql221)
        ibm_db.commit(conn)
        msg = "Deleted successsfully"
    except:
        ibm_db.rollback(conn)
        msg = "Error occured"
    print(msg)
    return redirect(url_for('root'))

@app.route("/displayCategory")
def displayCategory():
    loggedIn, firstName, noOfItems = getLoginDetails()
    categoryId = request.args.get("categoryId")
    ex='SELECT products.productId, products.name, products.price, products.image, categories.name FROM products, categories WHERE products.categoryId = categories.categoryId AND categories.categoryId ='+str(categoryId)
    sql21=ibm_db.prepare(conn,ex)
    ibm_db.execute(sql21)
    row=ibm_db.fetch_tuple(sql21)
    data =[]
    while row:
        data.append(row)
        row=ibm_db.fetch_tuple(sql21)

    categoryName = data[0][4]
    data = parse(data)
    return render_template('displayCategory.html', data=data, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryName=categoryName)

@app.route("/account/profile")
def profileHome():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    return render_template("profileHome.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/account/profile/edit")
def editProfile():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    ex='SELECT userId, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM users WHERE email =\''+str(session['email'])+'\''
    sql1=ibm_db.prepare(conn,ex)
    ibm_db.execute(sql1)
    profileData=ibm_db.fetch_tuple(sql1)
    return render_template("editProfile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword(conn=conn):
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()

        sql1=ibm_db.prepare(conn,'SELECT userId, password FROM users WHERE email = ?')
        ibm_db.execute(sql1, (session['email'],))
        userId, password = ibm_db.fetch_tuple(sql1)

        ex='UPDATE users SET password = '+str(newPassword)+' WHERE userId = '+str(userId)



        if (password == oldPassword):
            try:
                sql121=ibm_db.prepare(conn,ex)
                ibm_db.execute(sql121)
                ibm_db.commit(conn)
                msg="Changed successfully"
            except:
                ibm_db.rollback(conn)
                msg = "Failed"
            return render_template("changePassword.html", msg=msg)
        else:
            msg = "Wrong password"

        return render_template("changePassword.html", msg=msg)
    else:
        return render_template("changePassword.html")

@app.route("/updateProfile", methods=["GET", "POST"])
def updateProfile():
    if request.method == 'POST':
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']
        ex='UPDATE users SET firstName = \''+str(firstName)+'\''+', lastName = \''+str(lastName)+'\''+', address1 = \''+str(address1)+'\''+', address2 = \''+str(address2)+'\''+', zipcode = \''+str(zipcode)+'\''+', city = \''+str(city)+'\''+', state = \''+str(state)+'\''+', country = \''+str(country)+'\''+', phone = '+str(phone)+'\''+' WHERE email = \''+str(email)+'\''
        try:
            sql34=ibm_db.prepare(conn,ex)
            ibm_db.execute(sql34)

            ibm_db.commit(conn)
            msg = "Saved Successfully"
        except:
            ibm_db.rollback(conn)
            msg = "Error occured"

        return redirect(url_for('editProfile'))

@app.route("/loginForm")
def loginForm():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print('email')
        print(email)
        print('password')
        print(password)

        if is_valid(email, password):
            session['email'] = email
            return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)

@app.route("/productDescription")
def productDescription():
    loggedIn, firstName, noOfItems = getLoginDetails()
    productId = request.args.get('productId')

    sql1=ibm_db.prepare(conn,'SELECT productId, name, price, description, image, stock FROM products WHERE productId = ?')
    ibm_db.execute(sql1, (productId, ))
    productData=ibm_db.fetch_tuple(sql1)
    return render_template("productDescription.html", data=productData, loggedIn = loggedIn, firstName = firstName, noOfItems = noOfItems)

@app.route("/addToCart")
def addToCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        productId = int(request.args.get('productId'))
        sql1=ibm_db.prepare(conn,'SELECT userId FROM users WHERE email = ?')
        ibm_db.execute(sql1, (session['email'], ))
        userId = ibm_db.fetch_tuple(sql1)[0]
        print(userId)
        qw='INSERT INTO kart (userId, productId) VALUES ('+str(userId)+','+str(productId)+')'
        print(qw)
        try:
            sql1=ibm_db.prepare(conn,qw)
            ibm_db.execute(sql1)
            ibm_db.commit(conn)
            print('success')
            msg = "Added successfully"
        except:
            ibm_db.rollback(conn)
            print('error')
            msg = "Error occured"
    return redirect(url_for('root'))

@app.route("/cart")
def cart(conn=conn):
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']

    sql2=ibm_db.prepare(conn,'SELECT userId FROM users WHERE email = ?')
    ibm_db.execute(sql2, (email, ))
    userId = ibm_db.fetch_tuple(sql2)[0]


    sql1=ibm_db.prepare(conn,'SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = ?')
    ibm_db.execute(sql1, (userId, ))
    row=ibm_db.fetch_tuple(sql1)
    products=[]
    while row:
        products.append(row)
        row=ibm_db.fetch_tuple(sql1)
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render_template("cart.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    email = session['email']
    productId = int(request.args.get('productId'))
    sql2=ibm_db.prepare(conn,'SELECT userId FROM users WHERE email = ?')
    ibm_db.execute(sql2, (email, ))
    userId = ibm_db.fetch_tuple(sql2)[0]

    try:
        sql1=ibm_db.prepare(conn,'DELETE FROM kart WHERE userId = ? AND productId = ?')
        ibm_db.execute(sql1, (userId, productId))
        ibm_db.commit(conn)
        msg = "removed successfully"
    except:
        ibm_db.rollback(conn)
        msg = "error occured"
    return redirect(url_for('root'))

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))

def is_valid(email, password):
    sql3=ibm_db.prepare(conn,'SELECT email, password FROM users')
    ibm_db.execute(sql3)
    row=ibm_db.fetch_tuple(sql3)
    while row:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
        row=ibm_db.fetch_tuple(sql3)
    return False

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Parse form data    
        password = request.form['password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']
        ex='INSERT INTO users (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone) VALUES (\''+str(hashlib.md5(password.encode()).hexdigest())+'\',\''+str(email)+'\',\''+str(firstName)+'\',\''+str(lastName)+'\',\''+str(address1)+'\',\''+str(address2)+'\',\''+str(zipcode)+'\',\''+str(city)+'\',\''+str(state)+'\',\''+str(country)+'\',\''+str(phone)+'\');'
        print(ex)
        try:
            sql41=ibm_db.prepare(conn,ex)
            ibm_db.execute(sql41)
            ibm_db.commit(conn)
            msg = "Registered Successfully"
            o=0
        except:
            o=1
            print('llller')
            ibm_db.rollback(conn)
            msg = "Error occured"
        if o==0:
            sendmail(email)
        return render_template("login.html", error=msg)

@app.route("/registerationForm")
def registrationForm():
    return render_template("register.html")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
