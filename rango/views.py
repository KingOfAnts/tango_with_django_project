from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from datetime import datetime


from rango.forms import UserForm, UserProfileForm
from rango.forms import CategoryForm
from rango.forms import PageForm
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# A helper method
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    # Get the number of visits to the site.
    # We use the COOKIES.get() function to obtain the visits cookie.
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exist, then the default value of 1 is used.
    visits = int(get_server_side_cookie(request ,'visits', '1'))
    
    last_visit_cookie = get_server_side_cookie(request, 
                                               'last_visit',
                                               str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')
    # If its been more than a day since the last visit...
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # Update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        # Set the last visit cookie
        request.session['last_visit'] = last_visit_cookie
    
    # Update/set the visits cookie
    request.session['visits'] = visits


def index(request):
    
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by the number of likes in descending order.
    # Retrieve the top 5 only -- or all if less than 5.
    # Place the list in our context_dict dictionary (with our boldmessage!)
    # that will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5]

    page_list = Page.objects.order_by('-views')[:5]
    # Note the key boldmessage matches to {{ boldmessage }} in the template!
    
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    
    # Call the helper function to handle the cookies 
    visitor_cookie_handler(request)
    #context_dict['visits'] = request.session['visits']
    
    
    # Obtain our Response object early so we can add cookie information
    response = render(request, 'rango/index.html', context= context_dict)
    
    
    
    # Return response back to user, updationg any cookies that need changing
    return response
    
    
    #request.session.set_test_cookie()
    # Note that the first parameter is the template we wish to use.
    #return render(request, 'rango/index.html', context=context_dict)
def about(request):
    #return HttpResponse("Rango says this is the about page! <a href='/rango/'>Main page</a>")
    print (request.method)
    
    print(request.user)
    
    #if request.session.test_cookie_worked():
     #   print("TEST COOKIE WORKED!")
      #  request.session.delete_test_cookie()
    context_dict = {}
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    
    
    return render(request, 'rango/about.html', context_dict)

def show_category(request, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        
        pages = Page.objects.filter(category=category)
        
        context_dict['pages'] = pages
        
        
        context_dict['category'] = category
    except Category.DoesNotExist:
        
        context_dict['category'] = None
        context_dict['pages'] = None
    return render(request, 'rango/category.html', context=context_dict)
@login_required
def add_category(request):
    form = CategoryForm()
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        
        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)
            # Now that the category is saved, we could confirm this.
            # For now, just redirect the user back to the index view.
            return redirect('/rango/')
    else:
        # The supplied form contained errors -
        #print to terminal
        print(form.errors)
    #will handle the bad form, new form or no form supplied cases
    #render the form with error messages (if any)
    return render(request, 'rango/add_category.html', {'form':form})
@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
        
    if category is None:
        return redirect('/rango/')
    
    form = PageForm()
    
    if request.method == "POST":
        form = PageForm(request.POST)
        
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                
                return redirect(reverse('rango:show_category',
                                        kwargs={'category_name_slug':
                                            category_name_slug}))
    else:
        print(form.errors)
    context_dict = {'form':form, 'category':category}
    return render(request, 'rango/add_page.html', context_dict)


def register(request):
    # A boolean value for telling the template
    # whether the registration was successful.
    # Set to False initially. Code changes value to
    # True when registration succeeds.
    registered = False
    
    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == "POST":
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        #if the two forms are valid ...
        if user_form.is_valid() and profile_form.is_valid():
            #save the user's form data to the database
            user = user_form.save()
            
            #now we hash the password with the set_password method.
            #once hashed we can update the user object
            user.set_password(user.password)
            user.save()
            
            #now sort out the UserProfile instance
            #Since we need to set the user attribute ourselves.
            #we set commit=False. This delays saving the model
            #until we're ready to avoid integrity problems
            profile = profile_form.save(commit=False)
            profile.user = user
            
            #did the user provide a profile picture?
            #if so we need to get it from the input form and
            #put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
                
            #now we save the UserProfile model instance
            profile.save()
            
            #update our variable to indicate that the template
            #registration was successful
            registered = True
        else:
            #invalid form or forms - mistakes or something else?
            # Print problems to the terminal
            print(user_form.errors, profile_form.errors)
    else:
        #not a HTTP POST, so we render our form using two ModelForm instances.
        # These forms will be blank, ready for user input.
        user_form = UserForm()
        profile_form = UserProfileForm()
        
    #render the template depending on the context
    return render(request,
                  'rango/register.html',
                  context = {'user_form': user_form,
                             'profile_form': profile_form,
                             'registered': registered})
    
def user_login(request):
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        # We use request.POST.get('<variable>') as opposed
        # to request.POST['<variable>'], because the
        # request.POST.get('<variable>') returns None if the
        # value does not exist, while request.POST['<variable>']
        # will raise a KeyError exception.
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)
        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
        
    # The request is not a HTTP POST, so display the login form.
    # this scenario would most likely be a HTTP GET
    else:
        #No context variables to pass to the template syste, hence the
        #blank dictionary object
        return render(request,'rango/login.html')
    
@login_required
def restricted (request):
    
    return render(request,'rango/restricted.html')

# Use the login_required() decorator to ensure only those logged in can
# access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return redirect(reverse('rango:index'))



#def index(request):
 #   return HttpResponse("Rango Says hello world <a href='/rango/about/'>About</a>")
