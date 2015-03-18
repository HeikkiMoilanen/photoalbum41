from django.conf.urls import patterns, include, url
# from django.contrib.auth.views import login, logout

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'photoalbum.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    
    # Temporary to test AJAX
    #url(r'^ajaxform$', 'photoalbum.views.ajaxform'),
    
    # Starting page
    url(r'^$', 'photoalbum.views.default'),

	# User login and registration related URLs
    url(r'^login$', 'photoalbum.views.login'),
    url(r'^auth$', 'photoalbum.views.auth_view'),    
    url(r'^logout$','photoalbum.views.logout'),
    url(r'^invalid$', 'photoalbum.views.invalid_login'),    
    url(r'^register$', 'photoalbum.views.register_user'),
    #url(r'^register_success$', 'photoalbum.views.register_success'),
	
    # User URLs
    url(r'^main$', 'photoalbum.views.user_main'),
    url(r'^update$', 'photoalbum.views.update_user_info'),
    url(r'^update_success$', 'photoalbum.views.update_success'),
    #url(r'^orders$', 'photoalbum.views.view_orders'),
    url(r'^orders/(?P<orderid>\d+)$', 'photoalbum.views.view_order_details'),
    url(r'^order/pay/(?P<orderid>\d+)$', 'photoalbum.views.pay_order'),
    url(r'^order/cancel/(?P<orderid>\d+)$', 'photoalbum.views.cancel_order'),
    url(r'^order/commit_cancel/(?P<orderid>\d+)$', 'photoalbum.views.commit_cancel'),

    # Order URLs
    url(r'^choose_albums$', 'photoalbum.views.choose_albums'),
    url(r'^create_order$', 'photoalbum.views.create_order'),
    url(r'^order_success$', 'photoalbum.views.process_payment_result', name='success'),
    url(r'^order_cancel$', 'photoalbum.views.process_payment_result', name='cancel'),
    url(r'^order_error$', 'photoalbum.views.process_payment_result', name='error'),

    # Album urls. Link to ViewAlbum is to the public version and uses the share id.
    # EditAlbum uses the default album id and isn't reliant on whether the public link exists or not.
    # Named groups used here for clarity.
    url(r'^album/shared/(?P<shareid>\S+)$', 'photoalbum.views.view_album'),
    url(r'^album/edit/(?P<albumid>\d+)$', 'photoalbum.views.edit_album'),
    url(r'^album/share/(?P<albumid>\d+)$', 'photoalbum.views.share_album'),
    url(r'^album/unshare/(?P<albumid>\d+)$', 'photoalbum.views.unshare_album'),
    url(r'^album/create$', 'photoalbum.views.create_album'),
    url(r'^album/rename$', 'photoalbum.views.rename_album'),
    url(r'^album/delete/(?P<albumid>\d+)$', 'photoalbum.views.delete_album'),
    url(r'^album/commit_delete/(?P<albumid>\d+)$', 'photoalbum.views.commit_delete'),
    
    # Image URLs called by AJAX requests to add or delete images:
    url(r'^add_image$', 'photoalbum.views.add_image'),
    url(r'^delete_image$', 'photoalbum.views.delete_image'),
    url(r'^create_page$', 'photoalbum.views.create_page'),
    url(r'^edit_page$', 'photoalbum.views.view_page'),
    url(r'^delete_page$', 'photoalbum.views.delete_page'),
    url(r'^add_layout$', 'photoalbum.views.add_layout'),
    url(r'^update_image_on_page$', 'photoalbum.views.update_image_on_page'),
    url(r'^delete_image_on_page$', 'photoalbum.views.delete_image_on_page'),
    url(r'^view_page$', 'photoalbum.views.view_page'),
 
)

