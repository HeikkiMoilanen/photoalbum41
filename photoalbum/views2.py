from django.shortcuts import *
from models import *
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.forms.models import model_to_dict
from forms import MyRegistrationForm, CustomerForm
import json

# Temporary to text AJAX

@login_required
def ajaxform(request):
    args = {}
    args.update(csrf(request));
    return render_to_response('ajaxform.html', args)

# Login and authentication related views:

def login(request):
    c = {}
    c.update(csrf(request))    
    return render_to_response('login.html', c)
    
def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect('/main') 
    else:
        return HttpResponseRedirect('/invalid')
    
def loggedin(request):
    return render_to_response('loggedin.html', 
                              {'full_name': request.user.username})

def invalid_login(request):
    return render_to_response('invalid_login.html')

def logout(request):
    auth.logout(request)
    return render_to_response('logout.html')

def register_user(request):
    if request.method == 'POST':
        form_a = MyRegistrationForm(request.POST)
        form_b = CustomerForm(request.POST)
        if form_a.is_valid() and form_b.is_valid():
            user = form_a.save()
            customer = form_b.save(commit=False)
            customer.user = user
            customer.save()
            return HttpResponseRedirect('/register_success')       
    else:
        form_a = MyRegistrationForm()
        form_b = CustomerForm()
    args = {}
    args.update(csrf(request))  
    args['form_a'] = form_a
    args['form_b'] = form_b    
    return render_to_response('register.html', args)

def register_success(request):
    return render_to_response('register_success.html')

def recover_password(request):
	pass
    
# This view is only for debugging purposes, and will be removed before the end. 
# It is called when no URL explicitly matched the path in urls.py
    
def default(request):
    args = {}
    args['request'] = request
    return render_to_response('default.html', args)

# User specific views. To access these, user has to be logged in. 

@login_required
def user_main(request):
    user = request.user
    albums = user.customer.albums.all()
    template = "user_main.html"
    args = {}
    args['user'] = user
    args['albums'] = albums
    args.update(csrf(request))
    return render_to_response(template, args)

@login_required
def update_user_info(request):
    if request.method == 'POST':
        form_a = MyRegistrationForm(request.POST)
        form_b = CustomerForm(request.POST)
        if form_a.is_valid() and form_b.is_valid():
            user = form_a.save()
            customer = form_b.save(commit=False)
            customer.user = user
            customer.save()
            return HttpResponseRedirect('/update_success')       
    else:
        user = request.user
        user_as_dict = model_to_dict(user)
        form_a = MyRegistrationForm(initial = user_as_dict)
        customer = Customer.objects.get(user = user)
        customer_as_dict = model_to_dict(customer)
        form_b = CustomerForm(initial = customer_as_dict)
    args = {}
    args.update(csrf(request))  
    args['form_a'] = form_a
    args['form_b'] = form_b    
    return render_to_response('update_info.html', args)
        
@login_required
def update_success(request):
    return render_to_response('update_success.html')

# Album-related views

@login_required
def create_album(request):
    template = "album_base.html"
    album = Album()
    album.owner_id = request.user.id
    album.save()
    #for debugging purposes
    print Album.objects.all()
    return edit_album(request)

def view_album(request, shareid):
    template = "album_base.html"
    return render_to_response(template)

@login_required
def edit_album(request):
    customer = request.user.customer
    #testaa customer.images ja tee lista
    #images = Image.objects.get(customer = customer)
    template = "album_base.html"
    args = {}
    args.update(csrf(request));
    return render_to_response(template, args)

@login_required
def delete_album(request):
    args = {}
    args['album_id'] = albumid
    return render_to_response('delete_ask.html', args)

@login_required
def commit_delete(request):
	pass

@login_required
def share_album(request):
	pass

 # Page and image-related views

@login_required
def create_page(request):
	pass

@login_required
def add_layout(request):
	pass

@login_required
def edit_spread(request):
	pass

@login_required
def view_spread(request):
	pass

@login_required
def delete_page(request):
	pass

@login_required
def update_page(request):
	pass

@login_required
def add_image(request):
    customer = request.user.customer
    image_url = request.POST.get('image_url', '')
    image = Image(linkURL = image_url, customer = customer)
    image.save()
    data_dict = {}
    data_dict['image_url'] = image_url;
    data_dict['image_id'] = image.id;
    return HttpResponse(json.dumps(data_dict), mimetype='application/json')

# Order system -related views

@login_required
def create_order(request):
	pass

@login_required
def view_order(request):
	pass

@login_required
def process_payment_result(request):
	pass

