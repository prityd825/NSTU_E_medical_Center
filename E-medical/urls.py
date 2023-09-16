from django.contrib import admin
from django.urls import path
from hospital import views
from django.contrib.auth.views import LoginView,LogoutView
#BlogPost
from hospital.views import (
PostListView,
PostDetailView,
PostCreateView,
PostUpdateView,
PostDeleteView
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home_view,name='HOME'),
    path('blog/', views.blog),

    path('aboutus', views.aboutus_view),
    path('contactus', views.contactus_view),


    path('adminclick', views.adminclick_view),
    path('accountantclick', views.accountantclick_view),
    path('doctorclick', views.doctorclick_view),
    path('patientclick', views.patientclick_view),  

    path('adminsignup', views.admin_signup_view),
    path('accountantsignup', views.accountant_signup_view,name='accountantsignup'),
    path('doctorsignup', views.doctor_signup_view,name='doctorsignup'),
    path('patientsignup', views.patient_signup_view),
    
    path('adminlogin', LoginView.as_view(template_name='hospital/adminlogin.html')),
    path('accountantlogin', LoginView.as_view(template_name='hospital/accountantlogin.html')),
    path('doctorlogin', LoginView.as_view(template_name='hospital/doctorlogin.html')),
    path('patientlogin', LoginView.as_view(template_name='hospital/patientlogin.html')),


    path('afterlogin', views.afterlogin_view,name='afterlogin'),
    path('logout', LogoutView.as_view(template_name='hospital/index.html'),name='logout'),


    path('admin-dashboard', views.admin_dashboard_view,name='admin-dashboard'),

    path('admin-doctor', views.admin_doctor_view,name='admin-doctor'),
    path('admin-view-doctor', views.admin_view_doctor_view,name='admin-view-doctor'),
    path('delete-doctor-from-hospital/<int:pk>', views.delete_doctor_from_hospital_view,name='delete-doctor-from-hospital'),
    path('update-doctor/<int:pk>', views.update_doctor_view,name='update-doctor'),
    path('update-doctor-doctor/<int:pk>', views.update_doctor_view_doctor,name='update-doctor-doctor'),
    path('admin-add-doctor', views.admin_add_doctor_view,name='admin-add-doctor'),
    path('admin-approve-doctor', views.admin_approve_doctor_view,name='admin-approve-doctor'),
    path('approve-doctor/<int:pk>', views.approve_doctor_view,name='approve-doctor'),
    path('reject-doctor/<int:pk>', views.reject_doctor_view,name='reject-doctor'),
    path('admin-view-doctor-specialisation',views.admin_view_doctor_specialisation_view,name='admin-view-doctor-specialisation'),
    
    
     path('admin-accountant', views.admin_accountant_view,name='admin-accountant'),
     path('admin-view-accountant', views.admin_view_accountant_view,name='admin-view-accountant'),
     path('delete-accountant-from-hospital/<int:pk>', views.delete_accountant_from_hospital_view,name='delete-accountant-from-hospital'),
     path('update-accountant/<int:pk>', views.update_accountant_view,name='update-accountant'),
     path('admin-add-accountant', views.admin_add_accountant_view,name='admin-add-accountant'),
     path('admin-approve-accountant', views.admin_approve_accountant_view ,name='admin-approve-accountant'),
     path('approve-accountant/<int:pk>', views.approve_accountant_view,name='approve-accountant'),
     path('reject-accountant/<int:pk>', views.reject_accountant_view,name='reject-accountant'),
     
     
     
    path('admin-medicine', views.admin_medicine_view,name='admin-medicine'),
    path('admin-feedback', views.admin_feedback_view,name='admin-feedback'),
    

    path('admin-patient', views.admin_patient_view,name='admin-patient'),
    path('admin-view-patient', views.admin_view_patient_view,name='admin-view-patient'),
    path('delete-patient-from-hospital/<int:pk>', views.delete_patient_from_hospital_view,name='delete-patient-from-hospital'),
    path('update-patient/<int:pk>', views.update_patient_view,name='update-patient'),
    path('admin-add-patient', views.admin_add_patient_view,name='admin-add-patient'),
    path('admin-approve-patient', views.admin_approve_patient_view,name='admin-approve-patient'),
    path('approve-patient/<int:pk>', views.approve_patient_view,name='approve-patient'),
    path('reject-patient/<int:pk>', views.reject_patient_view,name='reject-patient'),
   


    path('admin-appointment', views.admin_appointment_view,name='admin-appointment'),
    path('admin-view-appointment', views.admin_view_appointment_view,name='admin-view-appointment'),
    path('admin-add-appointment', views.admin_add_appointment_view,name='admin-add-appointment'),
    path('admin-approve-appointment', views.admin_approve_appointment_view,name='admin-approve-appointment'),
    path('approve-appointment/<int:pk>', views.approve_appointment_view,name='approve-appointment'),
    path('reject-appointment/<int:pk>', views.reject_appointment_view,name='reject-appointment'),
]


#---------FOR DOCTOR RELATED URLS-------------------------------------
urlpatterns +=[
    path('doctor-dashboard', views.doctor_dashboard_view,name='doctor-dashboard'),
    path('search', views.search_view,name='search'),
    
    path('doctor-blog', views.doctor_blog_view,name='doctor-blog'),

    path('doctor-appointment', views.doctor_appointment_view,name='doctor-appointment'),
    path('doctor-view-appointment', views.doctor_view_appointment_view,name='doctor-view-appointment'),
    path('doctor-delete-appointment',views.doctor_delete_appointment_view,name='doctor-delete-appointment'),
    path('delete-appointment/<int:pk>', views.delete_appointment_view,name='delete-appointment'),
]


urlpatterns +=[
    path('accountant-dashboard', views.accountant_dashboard_view,name = 'accountant-dashboard'),
    path('accountant-medicine', views.accountant_medicine_view,name='accountant-medicine'),
    path('accountant-view-medicine', views.accountant_view_medicine_view,name='accountant-view-medicine'),
    path('accountant-add-medicine', views.accountant_add_medicine_view,name='accountant-add-medicine'),
    path('delete-medicine-from-hospital/<int:pk>', views.delete_medicine_from_hospital_view,name='delete-medicine-from-hospital'),
    path('update-medicine/<int:pk>', views.update_medicine_view,name='update-medicine'),
    path('search-medicine-records', views.search_medicine_records_view, name='search-medicine-records'),
]

  


#---------FOR PATIENT RELATED URLS-------------------------------------
urlpatterns +=[
    path('patient-dashboard', views.patient_dashboard_view,name='patient-dashboard'),
    path('patient-appointment', views.patient_appointment_view,name='patient-appointment'),
    path('patient-book-appointment', views.patient_book_appointment_view,name='patient-book-appointment'),
    path('patient-view-appointment', views.patient_view_appointment_view,name='patient-view-appointment'),
    path('patient-view-doctor', views.patient_view_doctor_view,name='patient-view-doctor'),
    path('patient-feedback', views.patient_view_feedback_view,name='patient-feedback'),
    path('searchdoctor', views.search_doctor_view,name='searchdoctor'),

]
#Blog_post code
urlpatterns += [
    path('doctor-blog/', PostListView.as_view(), name='doctor-blog'),
    path('blog/', PostListView.as_view(), name='blog-home'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('new-blog/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
]

#prescription

urlpatterns += [
    path('prescribe/', views.prescribe, name='prescribe'),
    path('prescription_form/<int:prescription_id>/', views.prescription_form, name='prescription_form'),
    path('prescription_history/', views.prescription_history, name='prescription_history'),
    path('generate_pdf/<int:prescription_id>/', views.generate_pdf, name='generate_pdf'),
    path('generate_pdf_patient/<int:prescription_id>/', views.generate_pdf_patient, name='generate_pdf_patient'),
]

# profile update
urlpatterns += [
    path('edit-profile-patient/', views.edit_profile_patient, name='edit_profile_patient'),
    path('edit-profile-doctor/', views.edit_profile_doctor, name='edit_profile_doctor'),
]

#message for patient
urlpatterns += [
    path('select_doctor/', views.select_doctor, name='select_doctor'),
    path('send_message/<int:recipient_id>/', views.send_message, name='send_message'),
    path('message_list/', views.message_list, name='message_list'),
    path('message_list/<int:chat_id>/<int:recipient_id>/', views.message_list, name='message_list'),
]

#message for doctor
urlpatterns += [
    path('doctor_messages/', views.doctor_messages, name='doctor_messages'),
]

#passowrd change
from django.contrib.auth import views as auth_views
urlpatterns += [
        # path('password-reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
        # path('password-reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
        # path('password-reset-confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
        # path('password-reset-complete/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),

        path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
        path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
        path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
        path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
