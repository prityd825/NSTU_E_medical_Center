from django.shortcuts import render,redirect, get_object_or_404,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required,user_passes_test
from datetime import datetime,timedelta,date
from django.conf import settings
from django.db.models import OuterRef, Subquery, Q, Min

#BlogPost
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
ListView,
DetailView,
CreateView,
UpdateView,
DeleteView
)
from .models import Post
from .forms import MedicineRecordForm
from .models import Medicine
from .models import Chat
from datetime import datetime as dt






# Create your views here.
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/index.html')


#for showing signup/login button for admin
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/adminclick.html')


#for showing signup/login button for admin
def accountantclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/accountantclick.html')


#for showing signup/login button for doctor
def doctorclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/doctorclick.html')


#for showing signup/login button for patient
def patientclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/patientclick.html')




def admin_signup_view(request):
    form=forms.AdminSigupForm()
    if request.method=='POST':
        form=forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.set_password(user.password)
            user.save()
            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)
            return HttpResponseRedirect('adminlogin')
    return render(request,'hospital/adminsignup.html',{'form':form})


#accountant--------------------------------------------------------------
def accountant_signup_view(request):
    userForm=forms.AccountantUserForm()
    accountantForm=forms.AccountantForm()
    mydict={'userForm':userForm,'accountantForm':accountantForm}
    if request.method=='POST':
        userForm=forms.AccountantUserForm(request.POST)
        accountantForm=forms.AccountantForm(request.POST,request.FILES)
        if userForm.is_valid() and accountantForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            accountant=accountantForm.save(commit=False)
            accountant.user=user
            accountant.email = user.email
            accountant=accountant.save()
            my_accountant_group = Group.objects.get_or_create(name='ACCOUNTANT')
            my_accountant_group[0].user_set.add(user)
        return HttpResponseRedirect('accountantlogin')
    return render(request,'hospital/accountantsignup.html',context=mydict)

#accountant----------------------------------------------------------------


def doctor_signup_view(request):
    userForm=forms.DoctorUserForm()
    doctorForm=forms.DoctorForm()
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST)
        doctorForm=forms.DoctorForm(request.POST,request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            
            doctor=doctorForm.save(commit=False)
            doctor.user=user
            doctor.email = user.email
            doctor=doctor.save()
            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)
        return HttpResponseRedirect('doctorlogin')
    return render(request,'hospital/doctorsignup.html',context=mydict)


def patient_signup_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            # patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient.email = user.email
            patient=patient.save()
            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)
        return HttpResponseRedirect('patientlogin')
    return render(request,'hospital/patientsignup.html',context=mydict)






#-----------for checking user is doctor , patient or admin
def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()

def is_accountant(user):
    return user.groups.filter(name='ACCOUNTANT').exists()


def is_doctor(user):
    return user.groups.filter(name='DOCTOR').exists()
def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,ACCOUNTANT,DOCTOR OR PATIENT
def afterlogin_view(request):
    if is_admin(request.user):
        return redirect('admin-dashboard')
    
    
    
    elif is_accountant(request.user):
       accountapproval=models.Accountant.objects.all().filter(user_id=request.user.id,status=True)
       if accountapproval:
            return redirect('accountant-dashboard')
           
       else:
            return render(request,'hospital/accountant_wait_for_approval.html')
    
    
    
    elif is_doctor(request.user):
        accountapproval=models.Doctor.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('doctor-dashboard')
        else:
            return render(request,'hospital/doctor_wait_for_approval.html')
        
        
    elif is_patient(request.user):
        accountapproval=models.Patient.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('patient-dashboard')
        else:
            return render(request,'hospital/patient_wait_for_approval.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    doctors=models.Doctor.objects.all().order_by('-id')
    patients=models.Patient.objects.all().order_by('-id')
    accountants = models.Accountant.objects.all().order_by('-id')
   
    doctorcount=models.Doctor.objects.all().filter(status=True).count()
    pendingdoctorcount=models.Doctor.objects.all().filter(status=False).count()

    patientcount=models.Patient.objects.all().filter(status=True).count()
    pendingpatientcount=models.Patient.objects.all().filter(status=False).count()
    
    accountantcount = models.Accountant.objects.all().filter(status = True).count()
    pendingaccountantcount = models.Accountant.objects.all().filter(status = False).count()
    
    appointmentcount=models.Appointment.objects.all().filter(status=True).count()
    pendingappointmentcount=models.Appointment.objects.all().filter(status=False).count()
    mydict={
    'doctors':doctors,
    'patients':patients,
    'accountants':accountants,
    'doctorcount':doctorcount,
    'pendingdoctorcount':pendingdoctorcount,
    
    'patientcount':patientcount,
    'pendingpatientcount':pendingpatientcount,
    
    'accountantcount':accountantcount,
    'pendingaccountantcount':pendingaccountantcount,
    
    'appointmentcount':appointmentcount,
    'pendingappointmentcount':pendingappointmentcount,
    }
    return render(request,'hospital/admin_dashboard.html',context=mydict)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_doctor_view(request):
    return render(request,'hospital/admin_doctor.html')




# @login_required(login_url='accountantlogin')
# @user_passes_test(is_accountant)
# def accountant_medicine_view(request):
#     return render(request,'hospital/accountant_medicine.html')
@login_required(login_url='accountantlogin')
@user_passes_test(is_accountant)
def accountant_medicine_view(request):
    accountant = models.Accountant.objects.get(user_id=request.user.id)
    context = {'accountant': accountant}
    return render(request, 'hospital/accountant_medicine.html', context)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_accountant_view(request):
    return render(request,'hospital/admin_accountant.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_accountant_view(request):
    accountants=models.Accountant.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_accountant.html',{'accountants':accountants})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_accountant_from_hospital_view(request,pk):
    accountant=models.Accountant.objects.get(id=pk)
    user=models.User.objects.get(id=accountant.user_id)
    user.delete()
    accountant.delete()
    return redirect('admin-view-accountant')



@login_required(login_url='accountantlogin')
@user_passes_test(is_accountant)
def delete_medicine_from_hospital_view(request, pk):
    medicine = models.Medicine.objects.get(id=pk)                                                  
    medicine.delete()
    return redirect('accountant-view-medicine') 





@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_accountant_view(request,pk):
    accountant=models.Accountant.objects.get(id=pk)
    user=models.User.objects.get(id=accountant.user_id)

    userForm=forms.AccountantUserForm(instance=user)
    accountantForm=forms.AccountantForm(request.FILES,instance=accountant)
    mydict={'userForm':userForm,'accountantForm':accountantForm}
    if request.method=='POST':
        userForm=forms.AccountantUserForm(request.POST,instance=user)
        accountantForm=forms.AccountantForm(request.POST,request.FILES,instance=accountant)
        if userForm.is_valid() and accountantForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            accountant=accountantForm.save(commit=False)
            accountant.status=True
            accountant.save()
            return redirect('admin-view-accountant')
    return render(request,'hospital/admin_update_accountant.html',context=mydict)








@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_accountant_view(request):
    userForm=forms.AccountantUserForm()
    accountantForm=forms.AccountantForm()
    mydict={'userForm':userForm,'accountantForm':accountantForm}
    if request.method=='POST':
        userForm=forms.AccountantUserForm(request.POST)
        accountantForm=forms.AccountantForm(request.POST, request.FILES)
        if userForm.is_valid() and accountantForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            accountant=accountantForm.save(commit=False)
            accountant.user=user
            accountant.status=True
            accountant.save()

            my_accountant_group = Group.objects.get_or_create(name='ACCOUNTANT')
            my_accountant_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-accountant')
    return render(request,'hospital/admin_add_accountant.html',context=mydict)




@login_required(login_url='accountantlogin')
@user_passes_test(is_accountant)
def accountant_add_medicine_view(request):
    form = forms.MedicineRecordForm()
    accountant = models.Accountant.objects.get(user_id=request.user.id)
    if request.method == 'POST':
        form = MedicineRecordForm(request.POST)
        if form.is_valid():
           
            medicine = Medicine(
                date=form.cleaned_data['date'],
                medicinename=form.cleaned_data['medicinename'],
                companyname=form.cleaned_data['companyname'],
                stock=form.cleaned_data['stock']
            )
            medicine.save()
           
            return redirect('accountant-view-medicine')  

    else:
        
        form = MedicineRecordForm()

    return render(request, 'hospital/accountant_add_medicine.html', {'form': form, 'accountant': accountant})





@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_accountant_view(request):
    #those whose approval are needed
    accountants=models.Accountant.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_accountant.html',{'accountants':accountants})





@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_accountant_view(request,pk):
    accountant=models.Accountant.objects.get(id=pk)
    accountant.status=True
    accountant.save()
    return redirect(reverse('admin-approve-accountant'))




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_accountant_view(request,pk):
    accountant=models.Accountant.objects.get(id=pk)
    user=models.User.objects.get(id=accountant.user_id)
    user.delete()
    accountant.delete()
    return redirect('admin-approve-accountant')

#--------------------------------------------------------ACCOUNTANT----------------------------



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_doctor.html',{'doctors':doctors})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_doctor_from_hospital_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-view-doctor')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)

    userForm=forms.DoctorUserForm(instance=user)
    doctorForm=forms.DoctorForm(request.FILES,instance=doctor)
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST,instance=user)
        doctorForm=forms.DoctorForm(request.POST,request.FILES,instance=doctor)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            doctor=doctorForm.save(commit=False)
            doctor.status=True
            doctor.save()
            return redirect('admin-view-doctor')
    return render(request,'hospital/admin_update_doctor.html',context=mydict)

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def update_doctor_view_doctor(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)

    userForm=forms.DoctorUserForm(instance=user)
    doctorForm=forms.DoctorForm(request.FILES,instance=doctor)
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST,instance=user)
        doctorForm=forms.DoctorForm(request.POST,request.FILES,instance=doctor)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            doctor=doctorForm.save(commit=False)
            doctor.status=True
            doctor.save()
            return redirect('doctor-dashboard')
    return render(request,'hospital/admin_update_doctor.html',context=mydict)





# @login_required(login_url='accountantlogin')
# @user_passes_test(is_accountant)
# def update_medicine_view(request, pk):
  
   
#     medicine = models.Medicine.objects.get(id=pk)   

#     if request.method == 'POST':
      
#         form = MedicineRecordForm(request.POST, instance=medicine)
#         if form.is_valid():
          
#             form.save()
#             return redirect('accountant-view-medicine')  
#     else:
#         context = {
#          form = MedicineRecordForm(instance=medicine)
#         'accountant': accountant,  # Pass the accountant object to the template
#     }
       

#     return render(request, 'hospital/accountant_update_medicine.html', {'form': form, 'medicine': medicine})



def update_medicine_view(request, pk):
    medicine = Medicine.objects.get(id=pk)

   
    accountant = request.user.accountant

    if request.method == 'POST':
        form = MedicineRecordForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            return redirect('accountant-view-medicine')
    else:
        form = MedicineRecordForm(instance=medicine)

    context = {
        'form': form,
        'medicine': medicine,
        'accountant': accountant,  
    }

    return render(request, 'hospital/accountant_update_medicine.html', context)








@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_doctor_view(request):
    userForm=forms.DoctorUserForm()
    doctorForm=forms.DoctorForm()
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST)
        doctorForm=forms.DoctorForm(request.POST, request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            doctor=doctorForm.save(commit=False)
            doctor.user=user
            doctor.status=True
            doctor.save()

            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-doctor')
    return render(request,'hospital/admin_add_doctor.html',context=mydict)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_doctor_view(request):
    #those whose approval are needed
    doctors=models.Doctor.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_doctor.html',{'doctors':doctors})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    doctor.status=True
    doctor.save()
    return redirect(reverse('admin-approve-doctor'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-approve-doctor')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_specialisation_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_doctor_specialisation.html',{'doctors':doctors})




@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_blog_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)  
    context = {
        'posts': Post.objects.all(),
        'doctor': doctor,  
    }
    return render(request, 'hospital/doctor_blog.html', context)



#doctor---------------------------------------------------------------

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_patient_view(request):
    return render(request,'hospital/admin_patient.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_medicine_view(request):
    medicines=models.Medicine.objects.all()
    return render(request,'hospital/admin_medicine.html',{'medicines':medicines})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_feedback_view(request):
    feedback_items = PatientFeedback.objects.all()
    return render(request, 'hospital/admin_feedback.html', {'feedback_items': feedback_items})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_patient.html',{'patients':patients})



@login_required(login_url='accountantlogin')
@user_passes_test(is_accountant)
def accountant_view_medicine_view(request):
    accountant = models.Accountant.objects.get(user_id=request.user.id)
    medicines = models.Medicine.objects.all()
    context = {'accountant': accountant, 'medicines': medicines}
    return render(request, 'hospital/accountant_view_medicine.html', context)
    
    # medicines=models.Medicine.objects.all()  
    # return render(request,'hospital/accountant_view_medicine.html',{'medicines':medicines})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_patient_from_hospital_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-view-patient')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)

    userForm=forms.PatientUserForm(instance=user)
    patientForm=forms.PatientForm(request.FILES,instance=patient)
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST,instance=user)
        patientForm=forms.PatientForm(request.POST,request.FILES,instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.status=True
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient.save()
            return redirect('admin-view-patient')
    return render(request,'hospital/admin_update_patient.html',context=mydict)





@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_patient_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            patient=patientForm.save(commit=False)
            patient.user=user
            patient.status=True
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient.save()

            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-patient')
    return render(request,'hospital/admin_add_patient.html',context=mydict)



#------------------FOR APPROVING PATIENT BY ADMIN----------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_patient_view(request):
    #those whose approval are needed
    patients=models.Patient.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_patient.html',{'patients':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    patient.status=True
    patient.save()
    return redirect(reverse('admin-approve-patient'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-approve-patient')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_appointment_view(request):
    return render(request,'hospital/admin_appointment.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_appointment_view(request):
    appointments=models.Appointment.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_appointment.html',{'appointments':appointments})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_appointment_view(request):
    appointmentForm=forms.AppointmentForm()
    mydict={'appointmentForm':appointmentForm,}
    if request.method=='POST':
        appointmentForm=forms.AppointmentForm(request.POST)
        if appointmentForm.is_valid():
            appointment=appointmentForm.save(commit=False)
            appointment.doctorId=request.POST.get('doctorId')
            appointment.patientId=request.POST.get('patientId')
            appointment.doctorName=models.User.objects.get(id=request.POST.get('doctorId')).first_name
            appointment.patientName=models.User.objects.get(id=request.POST.get('patientId')).first_name
            appointment.status=True
            appointment.save()
        return HttpResponseRedirect('admin-view-appointment')
    return render(request,'hospital/admin_add_appointment.html',context=mydict)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_appointment_view(request):
    #those whose approval are needed
    appointments=models.Appointment.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_appointment.html',{'appointments':appointments})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.status=True
    appointment.save()
    return redirect(reverse('admin-approve-appointment'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    return redirect('admin-approve-appointment')


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_dashboard_view(request):
   
    patientcount=models.Patient.objects.all().filter(status=True).count()
    appointmentcount=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id).count()
    # patientdischarged=models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.username).count()

    #for  table in doctor dashboard
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id).order_by('-id')
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid).order_by('-id')
    appointments=zip(appointments,patients)
    mydict={
    'patientcount':patientcount,
    'appointmentcount':appointmentcount,
    # 'patientdischarged':patientdischarged,
    'appointments':appointments,
    'doctor':models.Doctor.objects.get(user_id=request.user.id), 
    }
    return render(request,'hospital/doctor_dashboard.html',context=mydict)

#Accountant----------------------------------------------------------------


@login_required(login_url='accountantlogin')
@user_passes_test(is_accountant)
def accountant_dashboard_view(request):

    accountant = models.Accountant.objects.get(user_id=request.user.id)

    medicines = Medicine.objects.all()

    context = {
        'accountant': accountant,
        'medicines': medicines,  
    }

    return render(request, 'hospital/accountant_dashboard.html', context)


@login_required(login_url='accountantlogin')
@user_passes_test(is_accountant)
def search_medicine_records_view(request):
    accountant = models.Accountant.objects.get(user_id=request.user.id)
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date and end_date:
            try:
               
                start_date = dt.strptime(start_date, '%Y-%m-%d')
                end_date = dt.strptime(end_date, '%Y-%m-%d')
                
              
                medicines = Medicine.objects.filter(
                    Q(date__gte=start_date) & Q(date__lte=end_date)
                )
                

                context = {
                    'medicines': medicines,
                    'start_date': start_date,
                    'end_date': end_date,
                    'accountant': accountant,
                }

                return render(request, 'hospital/medicine_search_results.html', context)

            except ValueError:
                pass
    return redirect('accountant-dashboard')


#accountant___________________________________________-

# @login_required(login_url='doctorlogin')
# @user_passes_test(is_doctor)
# def doctor_patient_view(request):
#     mydict={
#     'doctor':models.Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
#     }
#     return render(request,'hospital/doctor_patient.html',context=mydict)





# @login_required(login_url='doctorlogin')
# @user_passes_test(is_doctor)
# def doctor_view_patient_view(request):
#     patients=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id)
#     doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
#     return render(request,'hospital/doctor_view_patient.html',{'patients':patients,'doctor':doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def search_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    # whatever user write in search box we get in query
    query = request.GET['query']
    patients=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id).filter(Q(symptoms__icontains=query)|Q(user__first_name__icontains=query))
    return render(request,'hospital/doctor_view_patient.html',{'patients':patients,'doctor':doctor})




@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/doctor_appointment.html',{'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_view_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_delete_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def delete_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_dashboard_view(request):
    patient = Patient.objects.get(user=request.user)  

    prescriptions = Prescription.objects.filter(patient=patient)

    return render(request, 'hospital/patient_dashboard.html', {'prescriptions': prescriptions, 'patient': patient})



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'hospital/patient_appointment.html',{'patient':patient})



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_book_appointment_view(request):
    appointmentForm=forms.PatientAppointmentForm()
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    message=None
    mydict={'appointmentForm':appointmentForm,'patient':patient,'message':message}
    if request.method=='POST':
        appointmentForm=forms.PatientAppointmentForm(request.POST)
        if appointmentForm.is_valid():
            print(request.POST.get('doctorId'))
            desc=request.POST.get('description')

            doctor=models.Doctor.objects.get(user_id=request.POST.get('doctorId'))
            
            appointment=appointmentForm.save(commit=False)
            appointment.doctorId=request.POST.get('doctorId')
            appointment.patientId=request.user.id #----user can choose any patient but only their info will be stored
            appointment.doctorName=models.User.objects.get(id=request.POST.get('doctorId')).first_name
            appointment.patientName=request.user.first_name #----user can choose any patient but only their info will be stored
            appointment.status=False
            appointment.save()
        return HttpResponseRedirect('patient-view-appointment')
    return render(request,'hospital/patient_book_appointment.html',context=mydict)



def patient_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'hospital/patient_view_doctor.html',{'patient':patient,'doctors':doctors})


from .models import PatientFeedback
from .forms import PatientFeedbackForm

@login_required(login_url='patientlogin')
def patient_view_feedback_view(request):
    try:
        patient = Patient.objects.get(user=request.user)  # Get the patient associated with the logged-in user
    except Patient.DoesNotExist:
        patient = None

    if request.method == 'POST':
        model_form = PatientFeedbackForm(request.POST)
        if model_form.is_valid():
            model_form.save()
            return redirect('patient-feedback')
    
        regular_form = PatientFeedbackForm(request.POST)
        if regular_form.is_valid():
            patient_name = regular_form.cleaned_data['patientName']
            email = regular_form.cleaned_data['email']
            feedback_text = regular_form.cleaned_data['feedback']
            return redirect('patient-feedback')
    else:
        model_form = PatientFeedbackForm()
        regular_form = PatientFeedbackForm()

    return render(request, 'hospital/patient_view_feedback.html', {'model_form': model_form, 'regular_form': regular_form, 'patient': patient})




def search_doctor_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    
    # whatever user write in search box we get in query
    query = request.GET['query']
    doctors=models.Doctor.objects.all().filter(status=True).filter(Q(department__icontains=query)| Q(user__first_name__icontains=query))
    return render(request,'hospital/patient_view_doctor.html',{'patient':patient,'doctors':doctors})




@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_view_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    appointments=models.Appointment.objects.all().filter(patientId=request.user.id)
    return render(request,'hospital/patient_view_appointment.html',{'appointments':appointments,'patient':patient})



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_discharge_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    dischargeDetails=models.PatientDischargeDetails.objects.all().filter(patientId=patient.id).order_by('-id')[:1]
    patientDict=None
    if dischargeDetails:
        patientDict ={
        'is_discharged':True,
        'patient':patient,
        'patientId':patient.id,
        'patientName':patient.get_name,
        'assignedDoctorName':dischargeDetails[0].assignedDoctorName,
        'address':patient.address,
        'email':patient.email,
        'symptoms':patient.symptoms,
        'admitDate':patient.admitDate,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'medicineCost':dischargeDetails[0].medicineCost,
        'roomCharge':dischargeDetails[0].roomCharge,
        'doctorFee':dischargeDetails[0].doctorFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
        }
        print(patientDict)
    else:
        patientDict={
            'is_discharged':False,
            'patient':patient,
            'patientId':request.user.id,
        }
    return render(request,'hospital/patient_discharge.html',context=patientDict)


def aboutus_view(request):
    return render(request,'hospital/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message,settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'hospital/contactussuccess.html')
    return render(request, 'hospital/contactus.html', {'form':sub})





#Blogggggggg

def blog(request):
    context = {
    'posts': Post.objects.all()
    }
    return render(request, 'hospital/blog.html', context)




class PostListView(ListView):
    model = Post
    template_name = 'hospital/doctor_blog.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']

   


class PostDetailView(DetailView):
    model = Post




class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']


    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)




class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']


# def form_valid(self, form):
#     form.instance.author = self.request.user
#     return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False




class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/doctor-blog/'
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False



from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Doctor, Patient, Prescription
from django.template.loader import get_template
from xhtml2pdf import pisa


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def prescribe(request):
   
    doctor = Doctor.objects.get(user=request.user)

    if request.method == "POST":
        patient_email = request.POST['patient_email']
        patient = Patient.objects.get(email=patient_email)
        prescription = Prescription.objects.create(doctor=doctor, patient=patient)
        print(prescription)
        return redirect('prescription_form', prescription_id=prescription.id)

    context = {
        'doctor': doctor 
    }
    return render(request, 'hospital/prescribe.html', context)


from .forms import SelectMedicineForm
@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def prescription_form(request, prescription_id):
    prescription = Prescription.objects.get(id=prescription_id)
    print(prescription.doctor)
    if request.method == "POST":
        form = SelectMedicineForm(request.POST)
        print(form)
        # Handle prescription form submission
        # Save symptoms, medicines, and tests to the prescription object

        prescription.symptoms = request.POST['symptoms']
        prescription.extraMedicine = request.POST['extraMedicine']
        prescription.advice = request.POST['advice']
        prescription.tests = request.POST['tests']
        
        if (hasattr(form.cleaned_data['medicine1'], 'medicinename')):
            prescription.medicine1 = form.cleaned_data['medicine1'].medicinename
            prescription.medicine1Count = form.cleaned_data['medicine1Count']
            medicine1 = Medicine.objects.get(medicinename=form.cleaned_data['medicine1'].medicinename)
            medicine1.stock = medicine1.stock - int(request.POST['medicine1Count']);
            medicine1.save()
        
        if (hasattr(form.cleaned_data['medicine2'], 'medicinename')):
            prescription.medicine2 = form.cleaned_data['medicine2'].medicinename
            prescription.medicine2Count = form.cleaned_data['medicine2Count']
            medicine2 = Medicine.objects.get(medicinename=form.cleaned_data['medicine2'].medicinename)
            medicine2.stock = medicine2.stock - int(request.POST['medicine2Count']);
            medicine2.save()
        
        if (hasattr(form.cleaned_data['medicine3'], 'medicinename')):
            prescription.medicine3 = form.cleaned_data['medicine3'].medicinename
            prescription.medicine3Count = form.cleaned_data['medicine3Count']
            medicine3 = Medicine.objects.get(medicinename=form.cleaned_data['medicine3'].medicinename)
            medicine3.stock = medicine3.stock - int(request.POST['medicine3Count']);
            medicine3.save()
        
        if (hasattr(form.cleaned_data['medicine4'], 'medicinename')):
            prescription.medicine4 = form.cleaned_data['medicine4'].medicinename
            prescription.medicine4Count = form.cleaned_data['medicine4Count']
            medicine4 = Medicine.objects.get(medicinename=form.cleaned_data['medicine4'].medicinename)
            medicine4.stock = medicine4.stock - int(request.POST['medicine4Count']);
            medicine4.save()
        
        if (hasattr(form.cleaned_data['medicine5'], 'medicinename')):
            prescription.medicine5 = form.cleaned_data['medicine5'].medicinename
            prescription.medicine5Count = form.cleaned_data['medicine5Count']
            medicine5 = Medicine.objects.get(medicinename=form.cleaned_data['medicine5'].medicinename)
            medicine5.stock = medicine5.stock - int(request.POST['medicine5Count']);
            medicine5.save()

        prescription.save()

        return redirect('prescription_history')
    else:
        form = SelectMedicineForm()

    return render(request, 'hospital/prescription_form.html', {'prescription': prescription, 'form': form})


# @login_required(login_url='doctorlogin')
# @user_passes_test(is_doctor)
# def prescription_history(request):
#     doctor = Doctor.objects.get(user=request.user)
#     prescriptions = Prescription.objects.filter(doctor=doctor)
#     return render(request, 'hospital/prescription_history.html', {'prescriptions': prescriptions})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def prescription_history(request):
   
    doctor = Doctor.objects.get(user=request.user)
    
    prescriptions = Prescription.objects.filter(doctor=doctor)
    
    context = {
        'doctor': doctor,  
        'prescriptions': prescriptions,
    }
    
    return render(request, 'hospital/prescription_history.html', context)



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def generate_pdf(request, prescription_id):
    prescription = Prescription.objects.get(id=prescription_id)
    template_path = 'hospital/pdf_template.html'
    context = {'prescription': prescription}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="prescription_{prescription.id}.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


@user_passes_test(is_patient)
@login_required(login_url='patientlogin')
def generate_pdf_patient(request, prescription_id):
    prescription = Prescription.objects.get(id=prescription_id)
    template_path = 'hospital/pdf_template.html'
    context = {'prescription': prescription}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="prescription_{prescription.id}.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


# from django.shortcuts import render, redirect
# from .forms import PatientProfileUpdateForm
# @user_passes_test(is_patient)
# @login_required(login_url='patientlogin')
# def edit_profile(request):
#     patient = request.user.patient

#     if request.method == 'POST':
#         form = PatientProfileUpdateForm(request.POST, request.FILES, instance=patient)
#         if form.is_valid():
#             form.save()
#             return redirect('patient_dashboard')
#     else:
#         form = PatientProfileUpdateForm(instance=patient)

#     return render(request, 'hospital/edit_profile.html', {'form': form})

from django.shortcuts import render, redirect
from .forms import UpdateNameForm, UpdateProfilePictureForm
from . import views
@user_passes_test(is_patient)
@login_required(login_url='patientlogin')
def edit_profile_patient(request):
    patient = Patient.objects.get(user=request.user)   # Get the patient associated with the logged-in user

    if request.method == 'POST':
        name_form = UpdateNameForm(request.POST, instance=request.user)
        picture_form = UpdateProfilePictureForm(request.POST, request.FILES, instance=patient)

        if name_form.is_valid() and picture_form.is_valid():
            name_form.save()
            picture_form.save()
            return redirect('patient-dashboard')
    else:
        name_form = UpdateNameForm(instance=request.user)
        picture_form = UpdateProfilePictureForm(instance=patient)

    return render(request, 'hospital/edit-profile-patient.html', {'name_form': name_form, 'picture_form': picture_form,'patient':patient})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def edit_profile_doctor(request):
    doctor = Doctor.objects.get(user=request.user)  # Get the doctor associated with the logged-in user
    
    if request.method == 'POST':
        name_form = UpdateNameForm(request.POST, instance=request.user)
        picture_form = UpdateProfilePictureForm(request.POST, request.FILES, instance=doctor)

        if name_form.is_valid() and picture_form.is_valid():
            name_form.save()
            picture_form.save()
            return redirect('doctor-dashboard')
    else:
        name_form = UpdateNameForm(instance=request.user)
        picture_form = UpdateProfilePictureForm(instance=doctor)

    return render(request, 'hospital/edit-profile-doctor.html', {'name_form': name_form, 'picture_form': picture_form, 'doctor': doctor})



#message
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message


from django.contrib.auth.models import User
@login_required
def send_message(request, recipient_id):
    print('inside send_message ', recipient_id)
    recipient = get_object_or_404(User, id=recipient_id)
    most_recent_message_ids = Message.objects.filter(chat=OuterRef('chat')).order_by('-timestamp').values('id')[:1]
    messages = Message.objects.filter(id__in=Subquery(most_recent_message_ids))
    
    try:
        userType = request.user.doctor
        sidebar = "hospital/doctor_base.html"
    except:
        sidebar = "hospital/patient_base.html"
    
    if request.method == 'POST':
        content = request.POST['content']
        chat = Chat()
        chat.save()
        message = Message(sender=request.user, recipient=recipient, chat=chat, content=content)
        message.save()
        unique_chat_ids = Message.objects.values('chat').distinct()
        messages = Message.objects.filter(Q(id__in=Subquery(unique_chat_ids)) & (Q(sender=request.user) | Q(recipient=request.user))).order_by('-timestamp')
        return render(request, 'hospital/message_list.html', {'messages': messages, 'recipient': recipient, 'sidebar': sidebar})
    
    # return redirect('message_list')

    return render(request, 'hospital/message_list.html', {'messages': messages, 'recipient': recipient, 'sidebar': sidebar})








@login_required
def message_list(request, recipient_id=1, chat_id=1):
    currentChat = Chat.objects.filter(id=chat_id)
    recipient = get_object_or_404(User, id=recipient_id)
    
    most_recent_message_ids = Message.objects.filter(chat=OuterRef('chat')).order_by('-timestamp').values('id')[:1]
    messages = Message.objects.filter(id__in=Subquery(most_recent_message_ids)).order_by('-timestamp')
    
    try:
        userType = request.user.doctor
        sidebar = "hospital/doctor_base.html"
    except:
        sidebar = "hospital/patient_base.html"

    if (len(currentChat) != 0):
        currentChat = currentChat[0]
        chatMessage = Message.objects.filter(Q(chat=currentChat)).order_by('timestamp')
    else:
        chatMessage = []

    if request.method == 'POST':
        content = request.POST['content']
        message = Message(chat=currentChat, sender=request.user, recipient=recipient, content=content)
        message.save()
        # chats = Chat.objects.filter(Q(sender=request.user) | Q(recipient=request.user)).order_by('-timestamp')
        chatMessage = Message.objects.filter(Q(chat=currentChat)).order_by('timestamp')
    is_doctor = Doctor.objects.filter(user=request.user).exists()
    return render(request, 'hospital/message_list.html', {'is_doctor': is_doctor,'messages': messages, 'chatMessage':chatMessage, 'recipient': request.user, 'chat_id':chat_id, 'sidebar': sidebar})

@login_required
def message_detail(request, chat_id):
    message = get_object_or_404(Message, id=chat_id)
    return render(request, 'hospital/message_detail.html', {'message': message})

from django.shortcuts import render, redirect
from .forms import SelectDoctorForm
# @login_required
# def select_doctor(request):
#     if request.method == 'POST':
#         form = SelectDoctorForm(request.POST)
#         if form.is_valid():
#             selected_doctor = form.cleaned_data['doctor']
#             doctorUser = Doctor.objects.filter(Q(id=selected_doctor.id))
#             if (len(doctorUser) != 0):
#                 singleMSG = Message.objects.filter(Q(recipient=selected_doctor.user))
#                 if (len(singleMSG) == 0):
#                     return redirect('send_message', recipient_id=selected_doctor.user.id)
#                 else:
#                     return redirect('message_list', chat_id=singleMSG[0].chat.id, recipient_id=selected_doctor.user.id)
#     else:
#         form = SelectDoctorForm()
    
#     return render(request, 'hospital/select_doctor.html', {'form': form})

@login_required
def select_doctor(request):
    try:
        patient = Patient.objects.get(user=request.user)  # Get the patient associated with the logged-in user
    except Patient.DoesNotExist:
        patient = None

    if request.method == 'POST':
        form = SelectDoctorForm(request.POST)
        if form.is_valid():
            selected_doctor = form.cleaned_data['doctor']
            doctorUser = Doctor.objects.filter(Q(id=selected_doctor.id))
            if len(doctorUser) != 0:
                singleMSG = Message.objects.filter(Q(recipient=selected_doctor.user))
                if len(singleMSG) == 0:
                    return redirect('send_message', recipient_id=selected_doctor.user.id)
                else:
                    return redirect('message_list', chat_id=singleMSG[0].chat.id, recipient_id=selected_doctor.user.id)
    else:
        form = SelectDoctorForm()
    
    return render(request, 'hospital/select_doctor.html', {'form': form, 'patient': patient})

from django.shortcuts import render
from .models import Message

def doctor_messages(request):
    current_doctor = request.user

    # Filter messages where recipient_id matches the current doctor's ID
    messages = Message.objects.filter(recipient_id=current_doctor.id).order_by('-timestamp')

    return render(request, 'hospital/doctor_messages.html', {'messages': messages})
