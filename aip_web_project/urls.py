from django.contrib import admin
from django.urls import path,include
from web_application import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name='home'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('login/',views.login_user,name='login'),
    path('logout/',views.logout_user,name='logout'),
    path('register/',views.register_user,name='register'),
    path('upload_invoice/',views.upload_invoice,name='upload_invoice'),
   # path('upload_file/', views.upload_file, name='upload_file'),
    path('show_files/', views.show_files, name='show_files'),
    path('classification_prediction/', views.classification_prediction, name='classification_prediction'),
    path('invoice_classification/', views.invoice_classification,name='invoice_classification'),
    path('verify_predictions/', views.verify_predictions, name='verify_predictions'),
    path('text_extraction_page/', views.text_extraction_page, name='text_extraction_page'),
    path('text_show_files/',views.text_show_files,name='text_show_files'),
    path('invoice_text_extraction/',views.invoice_text_extraction,name='invoice_text_extraction'),
    path('classification_text_extraction/',views.classification_text_extraction,name='classification_text_extraction'),

]

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

