from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    # Note the key boldmessage matches to {{ boldmessage }} in the template!
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    # Note that the first parameter is the template we wish to use.
    return render(request, 'rango/index.html', context=context_dict)
def about(request):
    #return HttpResponse("Rango says this is the about page! <a href='/rango/'>Main page</a>")
    return render(request, 'rango/about.html')

#def index(request):
 #   return HttpResponse("Rango Says hello world <a href='/rango/about/'>About</a>")
