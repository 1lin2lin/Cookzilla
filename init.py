#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect, flash
import bcrypt
import pymysql.cursors

#for uploading photo:
from app import app
from werkzeug.utils import secure_filename
#
# ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
#
# def allowed_image(filename):
#
#     if not "." in filename:
#         return False
#
#     ext = filename.rsplit(".", 1)[1]
#
#     if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
#         return True
#     else:
#         return False
#
#
# def allowed_image_filesize(filesize):
#
#     if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
#         return True
#     else:
#         return False
#
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port = 8889,
                       user='root',
                       password='root',
                       db='cookzilla',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


#Define a route to hello function
@app.route('/')
def hello():
    session['logged_in'] = False
    cursor = conn.cursor()
    query = 'SELECT DISTINCT tagText FROM RecipeTag'
    cursor.execute(query)
    tags = cursor.fetchall()
    cursor.close()
    return render_template('index.html', tags=tags)

@app.post('/search')
def search():
    tags_selected = request.form.getlist('selected_tag')
    rating_selected = request.form.getlist('selected_rating')
    keywords = request.form['keyword'].split()
    tag_query = "SELECT recipeID FROM RecipeTag WHERE "
    if (tags_selected):
        for tag in tags_selected:
            tag_query += "tagText = '"+tag+"' OR "
        size = len(tag_query)
        tag_query = tag_query[:size-4]
    else:
        tag_query = "SELECT recipeID FROM Recipe"

    rating_query = "SELECT recipeID FROM Review WHERE "
    if (rating_selected):
        for rating in rating_selected:
            rating_query += "stars = "+rating+" OR "
        size = len(rating_query)
        rating_query = rating_query[:size-4]
    else:
        rating_query = "SELECT recipeID FROM Recipe"

    keyword_query = "SELECT recipeID FROM Step WHERE "
    if (keywords):
        for keyword in keywords:
            keyword_query += "sDesc LIKE '%"+keyword+"%' OR "
        size = len(keyword_query)
        keyword_query = keyword_query[:size-4]
    else:
        keyword_query = "SELECT recipeID FROM Recipe"
    cursor = conn.cursor()
    query = "SELECT * from Recipe WHERE (recipeID IN ("+tag_query+") AND recipeID IN ("\
            +rating_query+") AND recipeID IN ("+keyword_query+"))"
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('/search_results.html', results=data, auth=session['logged_in'])


@app.route('/home')
def home():
    user_firstname = session['firstname']
    user = session['username']
    cursor = conn.cursor()
    # query for recipes posted by current user
    query_recipe = 'SELECT recipeID, title FROM Recipe WHERE postedBy = %s'
    cursor.execute(query_recipe, (user))
    post_data = cursor.fetchall()
    # query for reviews posted by current user
    query_review = 'SELECT recipeID, revTitle, stars FROM Review WHERE userName = %s'
    cursor.execute(query_review, (user))
    review_data = cursor.fetchall()
    query_tags = 'SELECT DISTINCT tagText FROM RecipeTag'
    cursor.execute(query_tags)
    tags = cursor.fetchall()
    cursor.close()
    return render_template('home.html', firstname=user_firstname, username=user, posts=post_data, reviews=review_data, tags=tags)


@app.route('/viewRecipe')
def viewRecipe():
    id = request.args.get('id')

    cursor = conn.cursor()
    # to obtain person first name and last name
    query = 'SELECT * FROM Person WHERE username = (SELECT postedBy FROM Recipe WHERE recipeID = %s)'
    cursor.execute(query, id)
    person_detail= cursor.fetchone()
    # to obtain recipe title, servings, and posted by
    query = 'SELECT * FROM Recipe WHERE recipeID = %s'
    cursor.execute(query, id)
    recipe_detail = cursor.fetchone()
    # to fetch all ingredients
    query = 'SELECT * FROM RecipeIngredient WHERE recipeID = %s'
    cursor.execute(query, id)
    ingredient_detail = cursor.fetchall()
    # to obtain steps
    query = 'SELECT * FROM Step WHERE recipeID = %s ORDER BY stepNo ASC'
    cursor.execute(query, id)
    step_detail = cursor.fetchall()
    # to obtain related tag
    query = 'SELECT * FROM RecipeTag WHERE recipeID = %s'
    cursor.execute(query, id)
    tag_detail = cursor.fetchall()
    # to obtain related recipe
    query = 'SELECT * FROM RelatedRecipe WHERE recipe1 = %s'
    cursor.execute(query, id)
    related_detail = cursor.fetchall()
    # to obtain the reviews for this recipe by natural joining review table and person table
    query = 'SELECT * FROM Review NATURAL JOIN Person WHERE recipeID = %s'
    cursor.execute(query, id)
    related_review = cursor.fetchall()
    # to obtain the image url
    query = 'SELECT * FROM RecipePicture WHERE recipeID = %s'
    cursor.execute(query, id)
    url = cursor.fetchall()
    # to obtain review pics
    query = 'SELECT * FROM ReviewPicture WHERE recipeID = %s'
    cursor.execute(query, id)
    review_pics = cursor.fetchall()
    cursor.close()
    return render_template('view_recipe.html', person=person_detail, recipes=recipe_detail, ingredients=ingredient_detail,
                           steps=step_detail, tags=tag_detail, related=related_detail, url=url, reviewPics=review_pics,
                           reviews=related_review, auth=session['logged_in'])


@app.route('/postRecipe')
def postRecipe():
    user = session['username']
    cursor = conn.cursor()
    query_recipe = 'SELECT * FROM Recipe'
    cursor.execute(query_recipe)
    data_recipe = cursor.fetchall()
    cursor.close()
    return render_template('post_recipe.html', user_recipes=data_recipe)

@app.route('/saveRecipe', methods=['GET', 'POST'])
def saveRecipe():
    user = session['username']
    recipe_title = request.form['title']
    numServing = request.form['serving']
    tags = request.form['tags'].split()
    related = request.form.getlist('related')
    url = request.form['url']

    # save recipe into Recipe table in the database
    cursor = conn.cursor()
    ins_Recipe = 'INSERT INTO Recipe(title, numServings, postedBy) VALUES(%s, %s, %s)'
    cursor.execute(ins_Recipe, (recipe_title, numServing, user))
    conn.commit()

    #obtain auto-generated recipeID and save it to session dictionary along with title
    query_id = 'SELECT recipeID FROM Recipe WHERE postedBy = %s and title = %s ORDER BY recipeID DESC'
    cursor.execute(query_id, (user, recipe_title))
    data1 = cursor.fetchone()
    recipe_id = data1['recipeID']
    session['recipeID'] = recipe_id
    session['recipeTitle'] = recipe_title

    # if there are tags, save tags into RecipeTag table
    if (tags):
        for tag in tags:
            ins_tag = 'INSERT INTO RecipeTag VALUES (%s, %s)'
            cursor.execute(ins_tag, (recipe_id, tag))
            conn.commit()

    # if there are related recipes, save into RelatedRecipe table
    if (related):
        for single_related in related:
            ins_tag = 'INSERT INTO RelatedRecipe VALUES (%s, %s)'
            cursor.execute(ins_tag, (recipe_id, single_related))
            conn.commit()

    # if there is an image url, save into RecipePicture
    if (url):
        ins_url = 'INSERT INTO RecipePicture VALUES (%s, %s)'
        cursor.execute(ins_url, (recipe_id, url))
        conn.commit()
    cursor.close()
    return redirect(url_for('Ingredient'))

@app.route('/Ingredient')
def Ingredient():
    recipe_title = session['recipeTitle']

    cursor = conn.cursor()
    query_ingredient = 'SELECT * FROM Ingredient'
    cursor.execute(query_ingredient)
    data_ingred = cursor.fetchall()
    query_unit = 'SELECT * FROM Unit'
    cursor.execute(query_unit)
    data_unit = cursor.fetchall()
    cursor.close()

    return render_template('post_ingredient.html', title=recipe_title, ingredients=data_ingred, units=data_unit)

@app.post('/addIngredient')
def addIngredient():
    recipe_id = session['recipeID']
    recipe_title = session['recipeTitle']
    ing_name = request.form['ingredient']
    ing_qty = request.form['quantity']
    ing_unit = request.form['unit']

    # check if this ingredient had already been entered for this recipe
    cursor = conn.cursor()
    query = 'SELECT * FROM RecipeIngredient WHERE recipeID = %s and iName = %s'
    cursor.execute(query, (recipe_id, ing_name))
    data = cursor.fetchone()
    error = None
    if (data):
        # ingredient had already been entered
        error = "This ingredient has already been entered, please enter a new ingredient"
        query_ingredient = 'SELECT * FROM Ingredient'
        cursor.execute(query_ingredient)
        data_ingred = cursor.fetchall()
        query_unit = 'SELECT * FROM Unit'
        cursor.execute(query_unit)
        data_unit = cursor.fetchall()
        cursor.close()
        return render_template('post_ingredient.html', title=recipe_title, ingredients=data_ingred, units=data_unit, error=error)
    else:
        # we need to check if this is a new ingredient entered by the user, if so, we need insert into Ingredient table
        query_newIng = 'SELECT * FROM Ingredient WHERE iName=%s'
        cursor.execute(query_newIng, ing_name)
        data_old_ing = cursor.fetchone()
        if not (data_old_ing):
            # ingredient not in Ingredient table, so we insert into Ingredient table first
            ins_ing = 'INSERT INTO Ingredient(iName) VALUES (%s)'
            cursor.execute(ins_ing, ing_name)
            conn.commit()
        # now we enter all the info in the RecipeIngredient table
        ins = 'INSERT INTO RecipeIngredient VALUES(%s, %s, %s, %s)'
        cursor.execute(ins, (recipe_id, ing_name, ing_unit, ing_qty))
        conn.commit()
        cursor.close()
        return redirect(url_for('Ingredient'))


@app.route('/Steps', methods=['GET'])
def Steps():
    user = session['username']
    recipe_title = session['recipeTitle']
    recipe_id = session['recipeID']

    cursor = conn.cursor()
    query_steps = 'SELECT * FROM Step WHERE recipeID = %s ORDER BY stepNo ASC'
    cursor.execute(query_steps, (recipe_id))
    data_steps = cursor.fetchall()
    cursor.close()
    return render_template('post_step.html', title=recipe_title, steps=data_steps)

@app.route('/addStep', methods=['GET','POST'])
def addStep():
    recipe_id = session['recipeID']
    recipe_title = session['recipeTitle']
    step_no = request.form['stepNo']
    step_desc = request.form['stepDesc']

    #save step into database
    cursor = conn.cursor()
    query = 'SELECT * FROM Step WHERE recipeID = %s and stepNo = %s'
    cursor.execute(query, (recipe_id, step_no))
    data = cursor.fetchone()
    error = None
    if (data):
        query_steps = 'SELECT * FROM Step WHERE recipeID = %s ORDER BY stepNo ASC'
        cursor.execute(query_steps, (recipe_id))
        data_steps = cursor.fetchall()
        error = f"Step number {step_no} has already been entered, please enter a new step"
        return render_template('post_step.html', title=recipe_title, steps=data_steps, error=error)
    else:
        ins = 'INSERT INTO Step VALUES(%s, %s, %s)'
        cursor.execute(ins, (step_no, recipe_id, step_desc))
        conn.commit()
        cursor.close()
        return redirect(url_for('Steps'))

@app.route('/selectReview')
def selectReview():
    user = session['username']
    cursor = conn.cursor()
    query = 'SELECT * FROM Recipe WHERE postedBy != %s'
    cursor.execute(query, user)
    data = cursor.fetchall()
    cursor.close()
    return render_template('post_review.html', user_recipes=data)

@app.post("/postReview")
def postReview():
    user = session['username']
    recipe_id = request.form.get('selected_recipe')
    title = request.form['revTitle']
    desc = request.form['revDesc']
    rating = int(request.form.get('select_star'))
    urls = request.form['urls'].split()

    cursor = conn.cursor()
    # check if the user already reviewed this recipe
    query = 'SELECT * FROM Review WHERE userName = %s and recipeID = %s'
    cursor.execute(query, (user, recipe_id))
    data = cursor.fetchone()
    if (data):
        flash("You have already posted a review for this recipe, please choose a different recipe")
        return redirect(url_for('selectReview'))
    else:
        ins = 'INSERT INTO Review VALUES (%s, %s, %s, %s, %s)'
        cursor.execute(ins, (user, recipe_id, title, desc, rating))
        conn.commit()
        if (urls):
            for url in urls:
                query = 'SELECT * FROM ReviewPicture WHERE pictureURL = %s'
                cursor.execute(query, url)
                data_url = cursor.fetchone()
                if not data_url:
                    ins = 'INSERT INTO ReviewPicture VALUES (%s, %s, %s)'
                    cursor.execute(ins, (user, recipe_id, url))
                    conn.commit()
        cursor.close()
        return redirect(url_for('home'))

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')


#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    username = request.form['username']
    password = request.form['password']

    passwordBytes = password.encode('utf-8')

    # cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM Person WHERE userName = %s'
    cursor.execute(query, (username))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if (data):
        hashedBytes = data['password'].encode('utf-8')
        passwordMatch = bcrypt.checkpw(passwordBytes, hashedBytes)
        if (passwordMatch):
            #creates a session for the the user
            #session is a built in
            session['username'] = username
            session['firstname'] = data['fName']
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            # returns an error message to the html page
            error = 'Invalid login or username, please try again.'
            return render_template('login.html', error=error)
    else:
        # returns an error message to the html page
        error = 'Invalid login or username, please try again.'
        return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    fname = request.form['firstname']
    lname = request.form['lastname']
    email = request.form['email']
    profile = request.form['profile']

    passwordBytes = password.encode('utf-8')
    hashedPassword = bcrypt.hashpw(passwordBytes, bcrypt.gensalt())

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT * FROM Person WHERE userName = %s'
    cursor.execute(query, (username))
    # stores the results in a variable
    data = cursor.fetchone()
    error = None
    if (data):
        # user already exists
        error = "This user already exists, please enter a unique username"
        return render_template('register.html', error=error)
    else:
        ins = 'INSERT INTO Person VALUES(%s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, hashedPassword, fname, lname, email, profile))
        conn.commit()
        cursor.close()
        return redirect('/')

@app.route('/logout')
def logout():
    session.pop('username')
    session.pop('firstname')
    recipeID = session['recipeID']
    recipeTitle = session['recipeTitle']
    if (recipeID):
        session.pop('recipeID')
    if (recipeTitle):
        session.pop('recipeTitle')
    return redirect('/')

if __name__ == "__main__":
    app.run('127.0.0.1', 8000, debug = True)