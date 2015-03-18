from django.db import models
from django.contrib.auth.models import User

# Customer model is used to extend Django's default User model with further user profile related
# attributes. It is linked to contrib.auth.User through OneToOne relationship. Another approach
# would have been to inherit Customer from User, but making Customer as the new authentication
# model seemed to create too much complexity for our purposes of simply adding a few fields.

class Customer(models.Model):
    user = models.OneToOneField(User)
    street_address = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=5)
    city = models.CharField(max_length=30)
    COUNTRY_CHOICES = (
        ('FI', 'Finland'),
        ('OT', 'Other'),
        )
    country = models.CharField(max_length=2, choices = COUNTRY_CHOICES)
    
# This was included in one of the examples but not clear if we need it    
# User.profile = property(lambda u: Customer.objects.get_or_create(user=u)[0])
    

class PaymentInfo(models.Model):
    baserate = models.DecimalField(default = 5.0, max_digits=5, decimal_places=2)
    pagerate = models.DecimalField(default = 1.0, max_digits=5, decimal_places=2)


class Album(models.Model):
    share_id = models.CharField(default = None, max_length=30, null=True, blank=True, unique=True)
    shared = models.BooleanField(default = False)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length = 50)
    date_created = models.DateField(auto_now_add = True) 
    owner = models.ForeignKey(Customer, related_name="albums")
    locked = models.BooleanField(default = False)
    payment_info = models.ForeignKey(PaymentInfo)
 
    # Inserts a new page to the album in a specific position. The page numbers of all subsequent pages are incremented by one. 
    def insert(self, new_page):
        #works, pagenumbers get updated, though they stay in the wrong order in the list.
        for page in self.pages.all():
            if page.pagenumber >= new_page.pagenumber:
                page.pagenumber = page.pagenumber + 1
                page.save()
        new_page.save()
 
    # Removes a specific page from the album. The page numbers of all subsequent pages are decremented by one.
    def remove(self, removed_page):
        number = removed_page.pagenumber
        removed_page.delete()
        for page in self.pages.all():
            if page.pagenumber > number:
                page.pagenumber = page.pagenumber - 1
                page.save()
    
	# Counts how many pages are included in this album
    def _get_pageCount(self):
        return Page.objects.filter(album=self).count()
	
    pageCount = property(_get_pageCount)

    # Calculates the price of this album based on how many pages there are and the rates in use
    def _get_price(self):
        return self.payment_info.baserate + self.pageCount * self.payment_info.pagerate

    price = property(_get_price)

    # Charfield did not allow null, and was "" if not specified otherwise.
    # Thus it got stuck on not being unique. We don't want to define share_id for
    # unshared albums, so save-function had to be overwritten to change "" to None.
    #def save(self, *args, **kwargs):
    #    if not self.share_id:
    #        self.share_id = None
    #    super(Album, self).save(*args, **kwargs)

    # For debugging purposes, print now prints id and share_id
    def __unicode__(self):
        return str(self.id) + ", shareid =" + str(self.share_id)

class Image(models.Model):
    linkURL = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, related_name="images")
   
class Meta:
    unique_together = ('linkURL', 'customer')
	
class Page(models.Model):
    heading = models.CharField(max_length=50)
    album = models.ForeignKey('Album', related_name="pages")
    layout = models.IntegerField(default = 1)
    pagenumber = models.IntegerField(default = 0)
    images = models.ManyToManyField(Image, through='ImagesOnPage')

class ImagesOnPage(models.Model):
    page = models.ForeignKey(Page, related_name="imagesonpage")
    image = models.ForeignKey(Image, related_name="imagesonpage")
    index = models.IntegerField()
    caption = models.CharField(max_length=300) 
	
class Order(models.Model):
    STATUS_CHOICES = (
        ('OR', 'Ordered'),
        ('PA', 'Paid'),
        ('DE', 'Delivered'),
        )
    status = models.CharField(max_length=2, choices = STATUS_CHOICES)
    date_created = models.DateField(auto_now_add = True)
    customer = models.ForeignKey(Customer, related_name="orders")
    albums = models.ManyToManyField(Album, through='AlbumsInOrder')
    pid = models.CharField(max_length=50)
    # Calculates the price for this order summing the prices of each album included in the order
    def _get_price(self):
        order_price = 0
        for one_album in self.albums.all(): # Goes through the albums belonging to this order
            album_in_order = AlbumsInOrder.objects.get(order=self, album = one_album)
            order_price = order_price + album_in_order.quantity * one_album.price
            # Sums their prices

        if order_price >= 1000000:

            return 0

        return order_price

    price = property(_get_price)
	
class AlbumsInOrder(models.Model):
    album = models.ForeignKey(Album)
    order = models.ForeignKey(Order)
    quantity = models.IntegerField(default=0)