# Cookzilla
This is a database project using Flask with python, mysql and html. 

#index page: 
Users are greeted by the website and have the option to 1) search for recipe 2) login or 3) register a new user.
Both registered and non-registered users can use the search function. Only difference is that if a user use the search function after they already logged in, they can return to their personalized homepage from the search results page, whereas a non-registered user can only return to the index page from the search results page. The search function can be a combination of searching by tags, ratings and/or keywords. Queries will be dynamically compiled based on user's search input. If no search criteria is selected, the search will return all recipes in the database. Recipes in the search result page will be ordered by recipeID as well as display the recipe title. Each recipeID can be clicked by user which will take the user to see details of the selected recipe. 

#log in:
Users are prompted to enter their username and password. Entered passwords are checked against the hashed password stored in the database. If no username is found or the password does not match, an error message will be shown and user will be prompted to try logging in again. 

#Register new user: 
New users need to enter their username, password, first and last name, email, and a short profile to register with Cookzilla. If the same username already existed, an error message will be displayed and user need to enter a different username. Passwords are hashed before stored in the database. 

#Personal homepage: 
After a registered user logged in, the user is directed to the user's personalized homepage. This homepage will 
  1) greet the user by user's first name; 
  2) give the user options to either post a new recipe or post a new review; 
  3) display all previous recipes that were posted by this user. Recipes are ordered by order ID, and each ID can be clicked to take the user to the recipe    detail page. 
  4) display a summarized view of all previous reviews posted by this user, ordered by recipe ID. Again, each recipe ID can be clicked to take the user to      see details of each recipe.
  5) let current user search for more recipes based on a combination of tags, ratings and/or keywords. This is the same search function provided to           non-registered users at the index page.
  6) log out

#Recipe page: 
This page will display all the details of the selected recipe. Details include recipe pictures (if any), user who posted this recipe, serving size, recipe tags, other recipes that are related to the current recipe, a display of all ingredients and quantity, steps on how to make the recipe, reviews, and review pictures posted by reviewsers. 

#Post a new recipe: 
When user clicked on this link on homepage, it will direct user to the Post recipe page, where user can enter a title, serving size, create tags, select any related recipes (from all other recipes in the database), and enter an image url. 
After information has been entered, user click on "continue to add ingredients" to be directed to the "ingredient" page. 
On this page, user can choose from a list of ingredients that are already stored in the database, and select the quantity and unit associated with the ingredient. If user entered an ingredient that does not exist in the databse, the new ingredient will be added. After all ingredients have been added, user will proceed to add detailed steps.
When adding steps, user can choose a step number and enter the description of the step. If the same step number had already been entered, an error message will display to let the user choose a new step. As the user adds each new step, previous steps will also be displayed to the user on the same page. 
Once user is done adding all the steps, user can click on "return home" to return to user's homepage. 

#Post a new review: 
Users can choose from a dropdown list to select the recipe they would like to review. However, users cannot review the recipes posted by themselves, so those recipes will not be among the options in the dropdown list. Reivewer can enter a title, a description of the review, choose a rating, and copy over the review picture URL to be displayed along with the review in the recipe detail page. 

This project fulfills the 4 basic requirements, and 2 extra features: 
1) User is able to post reviews
2) More complex searches in terms of mix and match different search inputs such as tags(single tag or multiple), ratings (single rating or multiple), and keywords (single keyword or multiple keywords).
