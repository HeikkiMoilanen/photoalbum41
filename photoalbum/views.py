from django.shortcuts import *
from models import *
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.forms.models import model_to_dict
from forms import MyRegistrationForm, CustomerForm, MyUserChangeForm
from django.conf import settings
from django.core.urlresolvers import reverse
import json
import random
import md5
import string

# Login and authentication:

# This functionality is based on django.contrib.auth. Django's default User model is exteded by
# a custom Customer model to store additional user profile information. 

# URL '/login'. Returns a template with an authentication form asking 
# for username and password.

def login(request):
    c = {}
    c.update(csrf(request))    
    return render_to_response('login.html', c)
    
# Processes the submission of the authentication form. Authenticates the user. 
# If authentication is successful, user is directed to '/main'. Otherwise, user is redirected
# to '/invalid'.
	
def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect('/main') 
    else:
        return HttpResponseRedirect('/invalid')

# URL '/invalid'. Returns a template that tells the user that her authentication attempt
# authentication failed.							  
							  
def invalid_login(request):
    return render_to_response('invalid_login.html')
	
# URL '/logout'. Logs out the user and returns a template that tells the user so.
	
def logout(request):
    auth.logout(request)
    return render_to_response('logout.html')

# URL '/register'. When a GET is made to the URL, a form is returned to allow the user to fill in her
# username, password and other profile information. The POST with the form parameters is sent to the 
# same URL, and in that case the form input is validated and the information is saved to new 
# User and Customer models. Django forms MyRegistrationForm and CustomerForm are used. 
# MyRegistrationForm is an extension to the default django.contrib.auth UserCreationForm.	
	
def register_user(request):
    if request.method == 'POST':
        form_a = MyRegistrationForm(request.POST)
        form_b = CustomerForm(request.POST)
        if form_a.is_valid() and form_b.is_valid():
            user = form_a.save()
            customer = form_b.save(commit=False)
            customer.user = user
            customer.save()

            # Logs newly created user in straight away
            new_user = auth.authenticate(username=request.POST['username'], password=request.POST['password2'])
            auth.login(request, new_user)
            return HttpResponseRedirect("/main")      
    else:
        form_a = MyRegistrationForm()
        form_b = CustomerForm()
    args = {}
    args.update(csrf(request))  
    args['form_a'] = form_a
    args['form_b'] = form_b    
    return render_to_response('register.html', args)

# Serves a response telling to the user that registration succeeded.
# Now with auto-login added not really needed.	

# Starting page.
    
def default(request):
    args = {}
    args['request'] = request
    args['user'] = request.user
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
    args['orders'] = user.customer.orders.all()
    args.update(csrf(request))
    return render_to_response(template, args)

# Allows user to change her user profile information. When a GET is made, returns two forms
# that relate to User and Customer models, respectively. The form fields are pre-populated with
# user's/customer's current information. For a POST, the form parameters are 
# validated and the information is stored to User and Customer objects.
	
@login_required
def update_user_info(request):
    if request.method == 'POST':
        form_a = MyUserChangeForm(request.POST)
        form_b = CustomerForm(request.POST)
        if form_a.is_valid() and form_b.is_valid():
            user = request.user
            user.email = request.POST.get('email', '')
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.save()
            customer = user.customer
            customer.street_address = request.POST.get('street_address', '')
            customer.postal_code = request.POST.get('postal_code', '')
            customer.city = request.POST.get('city', '')
            customer.country = request.POST.get('country', '')
            customer.save()
            return HttpResponseRedirect('/update_success')       
    else:
        user = request.user
        user_as_dict = model_to_dict(user)
        form_a = MyUserChangeForm(initial = user_as_dict)
        customer = user.customer
        customer_as_dict = model_to_dict(customer)
        form_b = CustomerForm(initial = customer_as_dict)
    args = {}
    args.update(csrf(request))  
    args['form_a'] = form_a
    args['form_b'] = form_b
    args['user'] = request.user
    return render_to_response('update_info.html', args)
 
# Tells the user that the user profile update succeeded.
 
@login_required
def update_success(request):
    return render_to_response('update_success.html')

# Album-related views

@login_required
def create_album(request):
    template = "album_edit.html"
    album = Album()
    album.owner_id = request.user.customer.id

    check_prices_exist = PaymentInfo.objects.count()

    if check_prices_exist == 0:

        payment_info = PaymentInfo()
        payment_info.save()

    album.payment_info = PaymentInfo.objects.get(pk=1)

    album.save()

    # Create share id, initially is false.
    hm = ''.join(random.choice(string.ascii_letters) for x in range(30))
    
    while Album.objects.filter(share_id = hm).exists():
        hm = ''.join(random.choice(string.ascii_letters) for x in range(30))

    album.share_id = hm
    album.save()

    first_page = Page(album = album, pagenumber = 1)
    #put to model, album & pagenumber required
    first_page.save()
    another_page= Page(album = album, pagenumber = 2)
    album.insert(another_page)
    return redirect('photoalbum.views.edit_album', albumid=album.id, permanent=True)


@login_required
def edit_album(request, albumid):
    customer = request.user.customer
    album = get_object_or_404(Album, pk=albumid)
    if authorize(request, album) is not True:
        return authorize(request, album)
    album_pages = album.pages.all()
    customer_images = customer.images.all()
    if album.name == '':
        album.name ="My Album"
        album.save()
    template = "album_edit.html"
    args = {}
    args['user'] = request.user
    args['customer_images'] = customer_images
    args['album'] = album
    args['pages'] = album_pages
    args.update(csrf(request))
    return render_to_response(template, args)

@login_required
def rename_album(request):
    customer = request.user.customer
    albumid = request.POST.get('album_id', '')
    album_name = request.POST.get('album_name', '')
    album = Album.objects.get(id=albumid)
    if authorize(request, album) is not True:
        return authorize(request, album)
    data_dict = {}
    if len(album_name) < 31:
        album.name = album_name
        album.save()
        data_dict['result'] = 'ok'
    else:
        data_dict['result'] = 'too_long'
    return HttpResponse(json.dumps(data_dict), mimetype='application/json')  


@login_required
def delete_album(request, albumid):
    args = {}
    args['album_id'] = albumid
    args['user'] = request.user
    return render_to_response('delete_ask.html', args)

@login_required
def commit_delete(request, albumid):
    # Check if the user is authorized and not just sending POSTs   
    album = get_object_or_404(Album, pk=albumid)
    if authorize(request, album) is not True:
        return authorize(request, album)
    album.delete()
    return redirect('photoalbum.views.user_main', permanent=True)

@login_required
def share_album(request, albumid):
    
    album = get_object_or_404(Album, pk=albumid)

    if authorize(request, album) is not True:
        return authorize(request, album)

    album.shared = True
    album.save()

    return redirect('photoalbum.views.user_main', permanent=True)

# Removes share link. Can be restored later.
@login_required
def unshare_album(request, albumid):
    
    album = get_object_or_404(Album, pk=albumid)

    if authorize(request, album) is not True:
        return authorize(request, album)

    album.shared = False

    album.save()
    
    return redirect('photoalbum.views.user_main', permanent=True)

def view_album(request, shareid):

    album = get_object_or_404(Album, share_id=shareid)

    if not album.shared:

        template = "unauthorized.html"
        return render_to_response(template)

    args = {}
    args['album'] = album
    args['pages'] = album.pages.all()

    template = "album_view.html"
    return render_to_response(template, args)

 # Page and image-related views

@login_required
def create_page(request):

    customer = request.user.customer
    album_id = request.POST.get('album_id', '')
    # POST always posts strings, so it needs to be made to an int for page creation
    page_number = int(request.POST.get('page_number', ''))
    album = Album.objects.get(id = album_id)
    if authorize(request, album) is not True:
        return authorize(request, album)
    new_page = Page(album = album, pagenumber = page_number)
    album.insert(new_page)
    data_dict = {}
    data_dict['result'] = 'ok'
    data_dict['page_number'] = page_number
    return HttpResponse(json.dumps(data_dict), mimetype='application/json')  
    
@login_required
def delete_page(request):

    customer = request.user.customer
    album_id = request.POST.get('album_id', '')
    page_number = request.POST.get('page_number', '')
    album = Album.objects.get(id = album_id)
    if authorize(request, album) is not True:
        return authorize(request, album)
    removed_page = Page(album = album, pagenumber = page_number)
    ImagesOnPage.objects.filter(page = removed_page).delete()
    album.remove(removed_page)
    data_dict = {}
    data_dict['result'] = 'ok'
    return HttpResponse(json.dumps(data_dict), mimetype='application/json')

@login_required
def add_layout(request):

    customer = request.user.customer
    album_id = request.POST.get('album_id', '')
    page_number = request.POST.get('page_number', '')
    new_layout = request.POST.get('layout', '')
    album = Album.objects.get(id = album_id)
    if authorize(request, album) is not True:
        return authorize(request, album)
    page = Page.objects.get(album = album, pagenumber = page_number)
    page.layout = new_layout
    page.save()
    data_dict = {}
    data_dict['result'] = 'ok'
    return HttpResponse(json.dumps(data_dict), mimetype='application/json')

@login_required
def view_page(request):
    customer = request.user.customer
    album_id = request.POST.get('album_id', '')
    page_number = request.POST.get('page_number', '')
    album = Album.objects.get(id = album_id)
    try:
        page = Page.objects.get(album = album, pagenumber = page_number)
    except Page.DoesNotExist:
        page = None
    data_dict = {}
    if page is not None:
        data_dict['result'] = 'ok'
        data_dict['layout'] = page.layout
        data_dict['pagenumber'] = page.pagenumber
        images_on_page = page.imagesonpage.all()
        for image in images_on_page:
            index = image.index
            caption = image.caption
            image_url = image.image.linkURL
            image_info_list = [image_url, caption]
            data_dict[index] = image_info_list
    else:
        data_dict['result'] = 'no_page'    
    return HttpResponse(json.dumps(data_dict), mimetype='application/json')

@login_required
def delete_image_on_page(request):
    customer = request.user.customer
    album_id = request.POST.get('album_id', '')
    page_number = request.POST.get('page_number', '')
    index = request.POST.get('index', '')
    album = Album.objects.get(id = album_id)
    if authorize(request, album) is not True:
        return authorize(request, album)
    page = Page.objects.get(album = album, pagenumber = page_number)
    data_dict = {}
    try:
        image_on_page = ImagesOnPage.objects.get(page = page, index = index)
    except ImagesOnPage.DoesNotExist:
        image_on_page = None
    if image_on_page is None:
        data_dict['result'] = 'none'
    else:
        image_on_page.delete()
        data_dict['result'] = 'ok'
    return HttpResponse(json.dumps(data_dict), mimetype='application/json')

@login_required
def update_image_on_page(request):
    customer = request.user.customer
    album_id = request.POST.get('album_id', '')
    page_number = request.POST.get('page_number', '')
    index = request.POST.get('index', '')
    image_url = request.POST.get('image_url', '')
    caption = request.POST.get('caption', '')
    album = Album.objects.get(id = album_id)
    if authorize(request, album) is not True:
        return authorize(request, album)
    page = Page.objects.get(album = album, pagenumber = page_number)
    image = Image.objects.get(customer = customer, linkURL = image_url)
    try:
        image_on_page = ImagesOnPage.objects.get(page = page, index = index)
    except ImagesOnPage.DoesNotExist:
        image_on_page = None
    if image_on_page is None:
        image_on_page = ImagesOnPage(page = page, index = index, image = image, caption = caption)
        created = True
    else:
        image_on_page.image = image
        image_on_page.caption = caption
        created = False
    image_on_page.save()
    data_dict = {}
    if created == True:
        data_dict['result'] = 'new'
    else:
        data_dict['result'] = 'update'
    return HttpResponse(json.dumps(data_dict), mimetype='application/json')

# Adds an image for a particular customer based on its URL. Returns also the newly added image's
# id (not necessarily used by the client for anything). If the customer already has an
# image with the same URL, no changes are made and 'result: duplicate' is returned to the 
# client.
    
@login_required    
def add_image(request):
    customer = request.user.customer
    image_url = request.POST.get('image_url', '')
    image, created = Image.objects.get_or_create(linkURL = image_url, customer = customer)
    data_dict = {}
    if created == True:
        data_dict['result'] = 'ok'
        data_dict['image_url'] = image_url
        data_dict['image_id'] = image.id
    else:
        data_dict['result'] = 'duplicate'
    return HttpResponse(json.dumps(data_dict), mimetype='application/json')    

# Deletes an image based on its URL for a particular customer.
	
@login_required
def delete_image(request):
    customer = request.user.customer
    image_url = request.POST.get('image_url', '')
    Image.objects.get(linkURL = image_url, customer = customer).delete()
    return HttpRespose

# Order system -related views

@login_required
def choose_albums(request):
    albums = request.user.customer.albums.all()
    template = "order/choose_albums.html"
    args = {}
    args['albums'] = albums
    user = request.user
    args['user'] = user
    args['new_try'] = False
    args.update(csrf(request))

    return render_to_response(template, args)

@login_required
def create_order(request):

    customer = request.user.customer

    # Check to see if there are actually orders in the album
    is_order = False

    order = Order()
    order.customer_id = customer.id

    order.save()
    order.pid = str(order.id) + str(customer.id) + str(random.randrange(0, 32767))

    # Check that the pid isn't already on use
    while Order.objects.filter(pid = order.pid).count() > 0:
        order.pid = str(order.id) + str(customer.id) + random.randrange(0, 32767)

    order.status = 'OR'
    order.save()

    # Link all ordered albums to order
    for album in customer.albums.all():
        quantity = request.POST.get('quantity' + str(album.id), '')

        if int(quantity) > 0:
            albums_in_order = AlbumsInOrder(order=order, album=album, quantity=quantity)
            albums_in_order.save()
            if not album.locked:
                album.locked = True
                album.save()
    
    amount = order.price

    # If order price would come up as 0, or exceeds limit (which also gives 0), delete order and go back
    if amount == 0:
        order.delete()
        albums = request.user.customer.albums.all()
        template = "order/choose_albums.html"
        args = {}
        args['albums'] = albums
        user = request.user
        args['user'] = user
        args['new_try'] = True
        args.update(csrf(request))

        return render_to_response(template, args)

    template = 'order/checkout.html'
    args = {}
    checksumstr = "pid=%s&sid=%s&amount=%s&token=%s"%(order.pid, settings.SID, amount, settings.SECRET_ORDER_KEY)
    m = md5.new(checksumstr)
    checksum = m.hexdigest()
    args['checksum'] = checksum
    args['order'] = order
    args['sid'] = settings.SID
    args['pid'] = order.pid
    args['amount'] = amount

    args['user'] = request.user
    return render_to_response(template, args)

# Paying for an order made earlier
@login_required
def pay_order(request, orderid):

    order = get_object_or_404(Order, pk=orderid)

    template = 'order/pay.html'
    amount = order.price
    args = {}
    checksumstr = "pid=%s&sid=%s&amount=%s&token=%s"%(order.pid, settings.SID, amount, settings.SECRET_ORDER_KEY)
    m = md5.new(checksumstr)
    checksum = m.hexdigest()
    args['checksum'] = checksum
    args['order'] = order
    args['sid'] = settings.SID
    args['pid'] = order.pid
    args['amount'] = amount
    args['user'] = request.user
    return render_to_response(template, args)

@login_required
def cancel_order(request, orderid):

    order = get_object_or_404(Order, pk=orderid)
    args = {}
    args['order_id'] = orderid
    args['user'] = request.user
    return render_to_response('order/cancel_ask.html', args)

# Cancels an order that hasn't been paid or delivered.
@login_required
def commit_cancel(request, orderid):
    
    order = get_object_or_404(Order, pk=orderid)
    albums = order.albums.all()

    # Checks that the order is either indeterminate or just ordered status.
    # Deletes the order completely.
    # If the order has already been paid or delivered, does nothing.
    # In any case directs back to order list.
    if order.status == '' or order.status == 'OR':

        for album in albums:

            # Frees albums that are only in this order
            if album.order_set.count() <= 1:

                album.locked = False
                album.save()

        order.delete()

    return redirect('photoalbum.views.user_main', permanent=True)

@login_required
def view_order_details(request, orderid):

    customer = request.user.customer
    order = get_object_or_404(Order, pk=orderid)
    albums_in_order = []

    for one_album in order.albums.all(): # Goes through the albums belonging to this order
        album_in_order = AlbumsInOrder.objects.get(order=order, album = one_album)
        albums_in_order.append(album_in_order)

    template = 'order/order_details.html'
    args = {}
    args['customer'] = customer
    args['order'] = order
    args['albums'] = albums_in_order
    args['user'] = request.user
    return render_to_response(template, args)

@login_required
def process_payment_result(request):

    p_id = request.GET.get('pid', '')
    order = Order.objects.get(pid = p_id)
    ref = int(request.GET.get('ref', ''))

    # Calculates returning checksum
    checksumstr = "pid=%s&ref=%s&token=%s"%(p_id, ref, settings.SECRET_ORDER_KEY)
    m = md5.new(checksumstr)
    checksum = m.hexdigest()

    args = {}
    args['user'] = request.user
    # If checksum isn't a match, notify of the error.
    if checksum != request.GET.get('checksum', ''):

        template = 'order/rejected.html'
        return render_to_response(template, args)

    if request.path == reverse('success'):

        template = 'order/success.html'

        for one_album in order.albums.all(): # Goes through the albums belonging to this order
            
            # Locks those that have been ordered (as in, more than 0 copies)
            if AlbumsInOrder.objects.get(order=order, album = one_album).quantity > 0:
                one_album.locked = True
                one_album.save()

        order.status = 'PA'
        order.save()

        return render_to_response(template, args)

    if request.path == reverse('cancel'):

        template = 'order/cancelled.html'
        return render_to_response(template, args)

    if request.path == reverse('error'):

        template = 'order/error.html'
        return render_to_response(template, args)

# Used to check that the user who is trying to view or update any album related 
# information (including images on pages) is really the owner of that album.		
		
def authorize(request, album):
    #call this whenever changing images etc
    if album.owner.id is not request.user.customer.id:
        template = "unauthorized.html"
        return render_to_response(template)
    return True

