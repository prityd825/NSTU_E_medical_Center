from django.shortcuts import render,redirect, get_object_or_404,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.http import require_POST
from .access import role_required, post_required, RoleRequiredMixin, get_role, get_profile, is_approved, ROLE_HOME
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
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Doctor, Patient, Prescription, Message, PatientFeedback
from .forms import UpdateNameForm, UpdateProfilePictureForm, SelectDoctorForm, SelectMedicineForm, PatientFeedbackForm

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
    # Only an existing administrator may create another one. The very first admin can sign up freely.
    first_admin = not models.User.objects.filter(Q(groups__name='ADMIN') | Q(is_superuser=True)).exists()
    if not first_admin and not is_admin(request.user):
        messages.warning(request, 'New administrator accounts can only be created by an existing administrator.')
        return redirect('/adminlogin')
    form=forms.AdminSigupForm()
    if request.method=='POST':
        form=forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.set_password(user.password)
            user.save()
            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)
            messages.success(request, f'Administrator {user.username} was created.')
            if is_admin(request.user):
                return redirect('admin-dashboard')
            return HttpResponseRedirect('adminlogin')
    template = 'hospital/admin_add_admin.html' if is_admin(request.user) else 'hospital/adminsignup.html'
    return render(request, template, {'form':form})


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
            messages.success(request, 'Account created. You can sign in once an administrator approves it.')
            return HttpResponseRedirect('accountantlogin')
        mydict={'userForm':userForm,'accountantForm':accountantForm}
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
            messages.success(request, 'Account created. You can sign in once an administrator approves it.')
            return HttpResponseRedirect('doctorlogin')
        mydict={'userForm':userForm,'doctorForm':doctorForm}
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
            messages.success(request, 'Account created. You can sign in once an administrator approves it.')
            return HttpResponseRedirect('patientlogin')
        mydict={'userForm':userForm,'patientForm':patientForm}
    return render(request,'hospital/patientsignup.html',context=mydict)






#-----------for checking user is doctor , patient or admin
def is_admin(user):
    return get_role(user) == 'admin'

def is_accountant(user):
    return get_role(user) == 'accountant'

def is_doctor(user):
    return get_role(user) == 'doctor'

def is_patient(user):
    return get_role(user) == 'patient'


#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,ACCOUNTANT,DOCTOR OR PATIENT
#---------AFTER LOGIN: send every user to the dashboard of their own role
def afterlogin_view(request):
    if not request.user.is_authenticated:
        return redirect('/')
    role = get_role(request.user)
    if role is None:
        from django.contrib.auth import logout
        logout(request)
        messages.error(request, 'Your account has no role yet. Please contact the medical center.')
        return redirect('/')
    if is_approved(request.user):
        return redirect(ROLE_HOME[role])
    return render(request, f'hospital/{role}_wait_for_approval.html')


@role_required('admin')
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
    'prescriptioncount':models.Prescription.objects.count(),
    'medicinecount':models.Medicine.objects.count(),
    'lowstockcount':models.Medicine.objects.filter(stock__lt=20).count(),
    'feedbackcount':models.PatientFeedback.objects.count(),
    'postcount':models.Post.objects.count(),
    }
    return render(request,'hospital/admin_dashboard.html',context=mydict)



@role_required('admin')
def admin_doctor_view(request):
    return render(request,'hospital/admin_doctor.html')




# @login_required(login_url='accountantlogin')
# @user_passes_test(is_accountant)
# def accountant_medicine_view(request):
#     return render(request,'hospital/accountant_medicine.html')
@role_required('accountant')
def accountant_medicine_view(request):
    accountant = models.Accountant.objects.get(user_id=request.user.id)
    context = {'accountant': accountant}
    return render(request, 'hospital/accountant_medicine.html', context)


@role_required('admin')
def admin_accountant_view(request):
    return render(request,'hospital/admin_accountant.html')


@role_required('admin')
def admin_view_accountant_view(request):
    accountants=models.Accountant.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_accountant.html',{'accountants':accountants})



@role_required('admin')
@post_required
def delete_accountant_from_hospital_view(request,pk):
    accountant=get_object_or_404(models.Accountant, id=pk)
    accountant.user.delete()  # removes the profile too (on_delete=CASCADE)
    messages.info(request, 'Accountant removed from the medical center.')
    return redirect('admin-view-accountant')



@role_required('accountant')
@post_required
def delete_medicine_from_hospital_view(request, pk):
    medicine = get_object_or_404(models.Medicine, id=pk)                                                  
    medicine.delete()
    messages.info(request, 'Medicine record deleted.')
    return redirect('accountant-view-medicine') 





@role_required('admin')
def update_accountant_view(request,pk):
    accountant=get_object_or_404(models.Accountant, id=pk)
    user=accountant.user
    userForm=forms.UserEditForm(instance=user)
    accountantForm=forms.AccountantForm(instance=accountant)
    if request.method=='POST':
        userForm=forms.UserEditForm(request.POST,instance=user)
        accountantForm=forms.AccountantForm(request.POST,request.FILES,instance=accountant)
        if userForm.is_valid() and accountantForm.is_valid():
            user=userForm.save()
            accountant=accountantForm.save(commit=False)
            accountant.email=user.email
            accountant.save()
            messages.success(request, 'Accountant details saved.')
            return redirect('admin-view-accountant')
    mydict={'userForm':userForm,'accountantForm':accountantForm, 'accountant':accountant}
    return render(request,'hospital/admin_update_accountant.html',context=mydict)


@role_required('admin')
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
            accountant.email=user.email
            accountant.status=True
            accountant.save()

            my_accountant_group = Group.objects.get_or_create(name='ACCOUNTANT')
            my_accountant_group[0].user_set.add(user)
            messages.success(request, f'Accountant {user.get_full_name() or user.username} was added.')
            return HttpResponseRedirect('admin-view-accountant')
        mydict={'userForm':userForm,'accountantForm':accountantForm}
    return render(request,'hospital/admin_add_accountant.html',context=mydict)




@role_required('accountant')
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
           
            messages.success(request, 'Medicine added to stock.')
           
            return redirect('accountant-view-medicine')  

    else:
        
        form = MedicineRecordForm()

    return render(request, 'hospital/accountant_add_medicine.html', {'form': form, 'accountant': accountant})





@role_required('admin')
def admin_approve_accountant_view(request):
    #those whose approval are needed
    accountants=models.Accountant.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_accountant.html',{'accountants':accountants})





@role_required('admin')
@post_required
def approve_accountant_view(request,pk):
    accountant=get_object_or_404(models.Accountant, id=pk)
    accountant.status=True
    accountant.save()
    messages.success(request, 'Accountant approved. They can now sign in.')
    return redirect(reverse('admin-approve-accountant'))




@role_required('admin')
@post_required
def reject_accountant_view(request,pk):
    accountant=get_object_or_404(models.Accountant, id=pk)
    accountant.user.delete()  # removes the profile too (on_delete=CASCADE)
    messages.info(request, 'Accountant registration rejected and removed.')
    return redirect('admin-approve-accountant')

#--------------------------------------------------------ACCOUNTANT----------------------------



@role_required('admin')
def admin_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_doctor.html',{'doctors':doctors})



@role_required('admin')
@post_required
def delete_doctor_from_hospital_view(request,pk):
    doctor=get_object_or_404(models.Doctor, id=pk)
    doctor.user.delete()  # removes the profile too (on_delete=CASCADE)
    messages.info(request, 'Doctor removed from the medical center.')
    return redirect('admin-view-doctor')



@role_required('admin')
def update_doctor_view(request,pk):
    doctor=get_object_or_404(models.Doctor, id=pk)
    user=doctor.user
    userForm=forms.UserEditForm(instance=user)
    doctorForm=forms.DoctorForm(instance=doctor)
    if request.method=='POST':
        userForm=forms.UserEditForm(request.POST,instance=user)
        doctorForm=forms.DoctorForm(request.POST,request.FILES,instance=doctor)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            doctor=doctorForm.save(commit=False)
            doctor.email=user.email
            doctor.save()
            messages.success(request, 'Doctor details saved.')
            return redirect('admin-view-doctor')
    mydict={'userForm':userForm,'doctorForm':doctorForm, 'doctor':doctor}
    return render(request,'hospital/admin_update_doctor.html',context=mydict)


@role_required('doctor')
def update_doctor_view_doctor(request,pk):
    doctor=get_object_or_404(models.Doctor, id=pk)
    if doctor.user_id != request.user.id:
        messages.warning(request, 'You can only edit your own details.')
        return redirect('doctor-dashboard')
    user=request.user
    userForm=forms.UserEditForm(instance=user)
    doctorForm=forms.DoctorForm(instance=doctor)
    if request.method=='POST':
        userForm=forms.UserEditForm(request.POST,instance=user)
        doctorForm=forms.DoctorForm(request.POST,request.FILES,instance=doctor)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            doctor=doctorForm.save(commit=False)
            doctor.email=user.email
            doctor.save()
            if userForm.cleaned_data.get('password'):
                update_session_auth_hash(request, user)  # stay signed in after a password change
            messages.success(request, 'Your details were saved.')
            return redirect('doctor-dashboard')
    mydict={'userForm':userForm,'doctorForm':doctorForm,'doctor':doctor}
    return render(request,'hospital/admin_update_doctor.html',context=mydict)


@role_required('accountant')
def update_medicine_view(request, pk):
    medicine = get_object_or_404(Medicine, id=pk)
    accountant = get_profile(request.user)
    if request.method == 'POST':
        form = MedicineRecordForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine record updated.')
            return redirect('accountant-view-medicine')
    else:
        form = MedicineRecordForm(instance=medicine)
    return render(request, 'hospital/accountant_update_medicine.html', {'form': form, 'medicine': medicine, 'accountant': accountant})


@role_required('admin')
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
            doctor.email=user.email
            doctor.status=True
            doctor.save()

            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)
            messages.success(request, f'Doctor {user.get_full_name() or user.username} was added.')
            return HttpResponseRedirect('admin-view-doctor')
        mydict={'userForm':userForm,'doctorForm':doctorForm}
    return render(request,'hospital/admin_add_doctor.html',context=mydict)




@role_required('admin')
def admin_approve_doctor_view(request):
    #those whose approval are needed
    doctors=models.Doctor.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_doctor.html',{'doctors':doctors})


@role_required('admin')
@post_required
def approve_doctor_view(request,pk):
    doctor=get_object_or_404(models.Doctor, id=pk)
    doctor.status=True
    doctor.save()
    messages.success(request, 'Doctor approved. They can now sign in.')
    return redirect(reverse('admin-approve-doctor'))


@role_required('admin')
@post_required
def reject_doctor_view(request,pk):
    doctor=get_object_or_404(models.Doctor, id=pk)
    doctor.user.delete()  # removes the profile too (on_delete=CASCADE)
    messages.info(request, 'Doctor registration rejected and removed.')
    return redirect('admin-approve-doctor')



@role_required('admin')
def admin_view_doctor_specialisation_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_doctor_specialisation.html',{'doctors':doctors})




@role_required('doctor')
def doctor_blog_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)  
    context = {
        'posts': Post.objects.all(),
        'doctor': doctor,  
    }
    return render(request, 'hospital/doctor_blog.html', context)



#doctor---------------------------------------------------------------

@role_required('admin')
def admin_patient_view(request):
    return render(request,'hospital/admin_patient.html')



@role_required('admin')
def admin_medicine_view(request):
    medicines=models.Medicine.objects.all()
    return render(request,'hospital/admin_medicine.html',{'medicines':medicines})

@role_required('admin')
def admin_feedback_view(request):
    feedback_items = PatientFeedback.objects.all()
    return render(request, 'hospital/admin_feedback.html', {'feedback_items': feedback_items})


@role_required('admin')
def admin_view_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_patient.html',{'patients':patients})



@role_required('accountant')
def accountant_view_medicine_view(request):
    accountant = models.Accountant.objects.get(user_id=request.user.id)
    medicines = models.Medicine.objects.all()
    context = {'accountant': accountant, 'medicines': medicines}
    return render(request, 'hospital/accountant_view_medicine.html', context)
    
    # medicines=models.Medicine.objects.all()  
    # return render(request,'hospital/accountant_view_medicine.html',{'medicines':medicines})



@role_required('admin')
@post_required
def delete_patient_from_hospital_view(request,pk):
    patient=get_object_or_404(models.Patient, id=pk)
    patient.user.delete()  # removes the profile too (on_delete=CASCADE)
    messages.info(request, 'Patient removed from the medical center.')
    return redirect('admin-view-patient')



@role_required('admin')
def update_patient_view(request,pk):
    patient=get_object_or_404(models.Patient, id=pk)
    user=patient.user
    userForm=forms.UserEditForm(instance=user)
    patientForm=forms.PatientForm(instance=patient)
    if request.method=='POST':
        userForm=forms.UserEditForm(request.POST,instance=user)
        patientForm=forms.PatientForm(request.POST,request.FILES,instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            patient=patientForm.save(commit=False)
            patient.email=user.email
            patient.save()
            messages.success(request, 'Patient details saved.')
            return redirect('admin-view-patient')
    mydict={'userForm':userForm,'patientForm':patientForm, 'patient':patient}
    return render(request,'hospital/admin_update_patient.html',context=mydict)


@role_required('admin')
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
            patient.email=user.email
            patient.status=True
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient.save()

            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)
            messages.success(request, f'Patient {user.get_full_name() or user.username} was added.')
            return HttpResponseRedirect('admin-view-patient')
        mydict={'userForm':userForm,'patientForm':patientForm}
    return render(request,'hospital/admin_add_patient.html',context=mydict)



#------------------FOR APPROVING PATIENT BY ADMIN----------------------
@role_required('admin')
def admin_approve_patient_view(request):
    #those whose approval are needed
    patients=models.Patient.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_patient.html',{'patients':patients})



@role_required('admin')
@post_required
def approve_patient_view(request,pk):
    patient=get_object_or_404(models.Patient, id=pk)
    patient.status=True
    patient.save()
    messages.success(request, 'Patient approved. They can now sign in.')
    return redirect(reverse('admin-approve-patient'))



@role_required('admin')
@post_required
def reject_patient_view(request,pk):
    patient=get_object_or_404(models.Patient, id=pk)
    patient.user.delete()  # removes the profile too (on_delete=CASCADE)
    messages.info(request, 'Patient registration rejected and removed.')
    return redirect('admin-approve-patient')


@role_required('admin')
def admin_appointment_view(request):
    return render(request,'hospital/admin_appointment.html')



@role_required('admin')
def admin_view_appointment_view(request):
    appointments=models.Appointment.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_appointment.html',{'appointments':appointments})



@role_required('admin')
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
            messages.success(request, 'Appointment created and confirmed.')
            return HttpResponseRedirect('admin-view-appointment')
        mydict={'appointmentForm':appointmentForm,}
    return render(request,'hospital/admin_add_appointment.html',context=mydict)



@role_required('admin')
def admin_approve_appointment_view(request):
    #those whose approval are needed
    appointments=models.Appointment.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_appointment.html',{'appointments':appointments})



@role_required('admin')
@post_required
def approve_appointment_view(request,pk):
    appointment=get_object_or_404(models.Appointment, id=pk)
    appointment.status=True
    appointment.save()
    messages.success(request, 'Appointment approved.')
    return redirect(reverse('admin-approve-appointment'))



@role_required('admin')
@post_required
def reject_appointment_view(request,pk):
    appointment=get_object_or_404(models.Appointment, id=pk)
    appointment.delete()
    messages.info(request, 'Appointment request rejected.')
    return redirect('admin-approve-appointment')


@role_required('doctor')
def doctor_dashboard_view(request):
   
    patientcount=models.Appointment.objects.filter(status=True,doctorId=request.user.id).values('patientId').distinct().count()
    appointmentcount=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id).count()
    # patientdischarged=models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.username).count()

    #for  table in doctor dashboard
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id).order_by('-id')
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid).order_by('-id')
    patient_map={p.user_id: p for p in patients}
    appointments=[(a, patient_map.get(a.patientId)) for a in appointments]
    mydict={
    'patientcount':patientcount,
    'appointmentcount':appointmentcount,
    # 'patientdischarged':patientdischarged,
    'appointments':appointments,
    'doctor':models.Doctor.objects.get(user_id=request.user.id), 
    }
    return render(request,'hospital/doctor_dashboard.html',context=mydict)

#Accountant----------------------------------------------------------------


@role_required('accountant')
def accountant_dashboard_view(request):

    accountant = models.Accountant.objects.get(user_id=request.user.id)

    medicines = Medicine.objects.all()

    context = {
        'accountant': accountant,
        'medicines': medicines,
        'total_stock': medicines.aggregate(t=Sum('stock'))['t'] or 0,
        'low_stock_count': medicines.filter(stock__lt=20).count(),
    }

    return render(request, 'hospital/accountant_dashboard.html', context)


@role_required('accountant')
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


@role_required('doctor')
def search_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    # whatever user write in search box we get in query
    query = request.GET.get('query', '').strip()
    # Patients who have an appointment with this doctor, matched by name or email.
    my_patient_ids = models.Appointment.objects.filter(doctorId=request.user.id).values_list('patientId', flat=True)
    patients = models.Patient.objects.filter(status=True, user_id__in=list(my_patient_ids))
    if query:
        patients = patients.filter(Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query) | Q(email__icontains=query))
    return render(request,'hospital/doctor_view_patient.html',{'patients':patients,'doctor':doctor,'query':query})




@role_required('doctor')
def doctor_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/doctor_appointment.html',{'doctor':doctor})



@role_required('doctor')
def doctor_view_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    patient_map={p.user_id: p for p in patients}
    appointments=[(a, patient_map.get(a.patientId)) for a in appointments]
    return render(request,'hospital/doctor_view_appointment.html',{'appointments':appointments,'doctor':doctor})



@role_required('doctor')
def doctor_delete_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    patient_map={p.user_id: p for p in patients}
    appointments=[(a, patient_map.get(a.patientId)) for a in appointments]
    return render(request,'hospital/doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})



@role_required('doctor')
@post_required
def delete_appointment_view(request,pk):
    appointment=get_object_or_404(models.Appointment, id=pk)
    if appointment.doctorId != request.user.id:
        messages.warning(request, 'You can only remove your own appointments.')
    else:
        appointment.delete()
        messages.info(request, 'Appointment removed.')
    return redirect('doctor-delete-appointment')


@role_required('patient')
def patient_dashboard_view(request):
    patient = Patient.objects.get(user=request.user)  

    prescriptions = Prescription.objects.filter(patient=patient)

    return render(request, 'hospital/patient_dashboard.html', {'prescriptions': prescriptions, 'patient': patient})



@role_required('patient')
def patient_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'hospital/patient_appointment.html',{'patient':patient})



@role_required('patient')
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
            messages.success(request, 'Appointment requested. It will show as confirmed once the medical center approves it.')
            return HttpResponseRedirect('patient-view-appointment')
        mydict['appointmentForm']=appointmentForm
    return render(request,'hospital/patient_book_appointment.html',context=mydict)



@role_required('patient')
def patient_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'hospital/patient_view_doctor.html',{'patient':patient,'doctors':doctors})


from .models import PatientFeedback
from .forms import PatientFeedbackForm

@role_required('patient')
def patient_view_feedback_view(request):
    patient = get_profile(request.user)
    if request.method == 'POST':
        model_form = PatientFeedbackForm(request.POST)
        if model_form.is_valid():
            feedback = model_form.save(commit=False)
            feedback.patient = patient
            feedback.save()
            messages.success(request, 'Thank you! Your feedback was sent to the medical center.')
            return redirect('patient-feedback')
    else:
        model_form = PatientFeedbackForm(initial={'patientName': request.user.get_full_name(), 'email': request.user.email})
    return render(request, 'hospital/patient_view_feedback.html', {'model_form': model_form, 'regular_form': model_form, 'patient': patient})


@role_required('patient')
def search_doctor_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    
    # whatever user write in search box we get in query
    query = request.GET['query']
    doctors=models.Doctor.objects.all().filter(status=True).filter(Q(department__icontains=query)| Q(user__first_name__icontains=query))
    return render(request,'hospital/patient_view_doctor.html',{'patient':patient,'doctors':doctors})




@role_required('patient')
def patient_view_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    appointments=models.Appointment.objects.all().filter(patientId=request.user.id)
    return render(request,'hospital/patient_view_appointment.html',{'appointments':appointments,'patient':patient})




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
            receivers = getattr(settings, 'EMAIL_RECEIVING_USER', [settings.EMAIL_HOST_USER])
            if isinstance(receivers, str):
                receivers = [receivers]
            try:
                send_mail(str(name)+' || '+str(email), message, settings.EMAIL_HOST_USER, receivers, fail_silently=False)
            except Exception:
                messages.error(request, 'Sorry, we could not send your message right now. Please try again later or visit the medical center.')
                return render(request, 'hospital/contactus.html', {'form': sub})
            return render(request, 'hospital/contactussuccess.html')
    return render(request, 'hospital/contactus.html', {'form':sub})





#Blogggggggg

def blog(request):
    context = {
    'posts': Post.objects.select_related('author').order_by('-date_posted')
    }
    return render(request, 'hospital/blog.html', context)




class PostListView(ListView):
    model = Post
    template_name = 'hospital/doctor_blog.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']

    def get_template_names(self):
        # Doctors see the blog inside their dashboard; everyone else gets the public blog page.
        if is_doctor(self.request.user):
            return ['hospital/doctor_blog.html']
        return ['hospital/blog.html']

   


class PostDetailView(DetailView):
    model = Post

    def get_template_names(self):
        if is_doctor(self.request.user):
            return ['hospital/post_detail.html']
        return ['hospital/post_public.html']




class PostCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ('doctor',)
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.doctor = get_profile(self.request.user)
        messages.success(self.request, 'Your post is published.')
        return super().form_valid(form)


class PostUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ('doctor',)
    model = Post
    fields = ['title', 'content']

    def dispatch(self, request, *args, **kwargs):
        if is_doctor(request.user) and self.get_object().author_id != request.user.id:
            messages.warning(request, 'You can only edit your own posts.')
            return redirect('/doctor-blog/')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Post updated.')
        return super().form_valid(form)


class PostDeleteView(RoleRequiredMixin, DeleteView):
    """Doctors may delete their own posts; administrators may delete any post."""
    allowed_roles = ('doctor', 'admin')
    model = Post

    def dispatch(self, request, *args, **kwargs):
        if is_doctor(request.user) and self.get_object().author_id != request.user.id:
            messages.warning(request, 'You can only delete your own posts.')
            return redirect('/doctor-blog/')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.info(self.request, 'Post deleted.')
        return '/admin-blog' if is_admin(self.request.user) else '/doctor-blog/'


@role_required('doctor')
def prescribe(request):
   
    doctor = Doctor.objects.get(user=request.user)

    if request.method == "POST":
        patient_email = request.POST.get('patient_email', '').strip()
        patient = Patient.objects.filter(email__iexact=patient_email).first()
        if patient is None:
            messages.error(request, f'No patient is registered with the email "{patient_email}". Check the spelling and try again.')
            return render(request, 'hospital/prescribe.html', {'doctor': doctor, 'patient_email': patient_email})
        prescription = Prescription.objects.create(doctor=doctor, patient=patient)
        print(prescription)
        return redirect('prescription_form', prescription_id=prescription.id)

    context = {
        'doctor': doctor 
    }
    return render(request, 'hospital/prescribe.html', context)


from .forms import SelectMedicineForm
@role_required('doctor')
def prescription_form(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    if prescription.doctor.user_id != request.user.id:
        messages.warning(request, 'You can only edit prescriptions you wrote.')
        return redirect('prescription_history')
    if (prescription.symptoms or '').strip():
        # A saved prescription is final: editing it again would take the medicines out of stock twice.
        messages.info(request, 'This prescription is already saved. Open its PDF from the history, or write a new one.')
        return redirect('prescription_history')
    if request.method == "POST":
        form = SelectMedicineForm(request.POST)
        for field in ['symptoms', 'extraMedicine', 'advice', 'tests']:
            setattr(prescription, field, request.POST.get(field, ''))
        if not form.is_valid():
            messages.error(request, 'Please check the medicine quantities and try again.')
            return render(request, 'hospital/prescription_form.html', {'prescription': prescription, 'form': form})
        # Keep what the doctor typed so it is still there if we have to show an error.
        for field in ['symptoms', 'extraMedicine', 'advice', 'tests']:
            setattr(prescription, field, request.POST.get(field, ''))
        # Check every medicine has enough stock before changing anything.
        problems = []
        totals = {}  # the same medicine may be picked in more than one row
        for i in range(1, 6):
            med = form.cleaned_data.get(f'medicine{i}')
            qty = form.cleaned_data.get(f'medicine{i}Count') or 0
            if med and qty <= 0:
                problems.append(f'Enter how many {med.medicinename} to give.')
            elif med:
                totals[med] = totals.get(med, 0) + qty
        for med, qty in totals.items():
            if qty > med.stock:
                problems.append(f'Only {med.stock} {med.medicinename} left in stock.')
        if not request.POST.get('symptoms', '').strip():
            problems.append('Please describe the symptoms.')
        if problems:
            for msg in problems:
                messages.error(request, msg)
            return render(request, 'hospital/prescription_form.html', {'prescription': prescription, 'form': form})
        # Handle prescription form submission
        # Save symptoms, medicines, and tests to the prescription object

        prescription.symptoms = request.POST.get('symptoms', '')
        prescription.extraMedicine = request.POST.get('extraMedicine', '')
        prescription.advice = request.POST.get('advice', '')
        prescription.tests = request.POST.get('tests', '')
        
        if (hasattr(form.cleaned_data['medicine1'], 'medicinename')):
            prescription.medicine1 = form.cleaned_data['medicine1'].medicinename
            prescription.medicine1Count = form.cleaned_data['medicine1Count']
            medicine1 = Medicine.objects.get(pk=form.cleaned_data['medicine1'].pk)
            medicine1.stock = medicine1.stock - (form.cleaned_data['medicine1Count'] or 0);
            medicine1.save()
        
        if (hasattr(form.cleaned_data['medicine2'], 'medicinename')):
            prescription.medicine2 = form.cleaned_data['medicine2'].medicinename
            prescription.medicine2Count = form.cleaned_data['medicine2Count']
            medicine2 = Medicine.objects.get(pk=form.cleaned_data['medicine2'].pk)
            medicine2.stock = medicine2.stock - (form.cleaned_data['medicine2Count'] or 0);
            medicine2.save()
        
        if (hasattr(form.cleaned_data['medicine3'], 'medicinename')):
            prescription.medicine3 = form.cleaned_data['medicine3'].medicinename
            prescription.medicine3Count = form.cleaned_data['medicine3Count']
            medicine3 = Medicine.objects.get(pk=form.cleaned_data['medicine3'].pk)
            medicine3.stock = medicine3.stock - (form.cleaned_data['medicine3Count'] or 0);
            medicine3.save()
        
        if (hasattr(form.cleaned_data['medicine4'], 'medicinename')):
            prescription.medicine4 = form.cleaned_data['medicine4'].medicinename
            prescription.medicine4Count = form.cleaned_data['medicine4Count']
            medicine4 = Medicine.objects.get(pk=form.cleaned_data['medicine4'].pk)
            medicine4.stock = medicine4.stock - (form.cleaned_data['medicine4Count'] or 0);
            medicine4.save()
        
        if (hasattr(form.cleaned_data['medicine5'], 'medicinename')):
            prescription.medicine5 = form.cleaned_data['medicine5'].medicinename
            prescription.medicine5Count = form.cleaned_data['medicine5Count']
            medicine5 = Medicine.objects.get(pk=form.cleaned_data['medicine5'].pk)
            medicine5.stock = medicine5.stock - (form.cleaned_data['medicine5Count'] or 0);
            medicine5.save()

        prescription.save()

        messages.success(request, 'Prescription saved. You can download it as a PDF from the history page.')

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



@role_required('doctor')
def prescription_history(request):
   
    doctor = Doctor.objects.get(user=request.user)
    
    prescriptions = Prescription.objects.filter(doctor=doctor)
    
    context = {
        'doctor': doctor,  
        'prescriptions': prescriptions,
    }
    
    return render(request, 'hospital/prescription_history.html', context)



def _prescription_pdf(prescription):
    html = get_template('hospital/pdf_template.html').render({'prescription': prescription})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="prescription_{prescription.id}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Sorry, the PDF could not be created.', status=500)
    return response


@role_required('doctor', 'admin')
def generate_pdf(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    if is_doctor(request.user) and prescription.doctor.user_id != request.user.id:
        messages.warning(request, 'You can only open prescriptions you wrote.')
        return redirect('prescription_history')
    return _prescription_pdf(prescription)


@role_required('patient', 'admin')
def generate_pdf_patient(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    if is_patient(request.user) and prescription.patient.user_id != request.user.id:
        messages.warning(request, 'You can only open your own prescriptions.')
        return redirect('patient-dashboard')
    return _prescription_pdf(prescription)


@role_required('patient')
def edit_profile_patient(request):
    patient = Patient.objects.get(user=request.user)   # Get the patient associated with the logged-in user

    if request.method == 'POST':
        name_form = UpdateNameForm(request.POST, instance=request.user)
        picture_form = UpdateProfilePictureForm(request.POST, request.FILES, instance=patient)

        if name_form.is_valid() and picture_form.is_valid():
            name_form.save()
            picture_form.save()
            messages.success(request, 'Your profile was updated.')
            return redirect('patient-dashboard')
    else:
        name_form = UpdateNameForm(instance=request.user)
        picture_form = UpdateProfilePictureForm(instance=patient)

    return render(request, 'hospital/edit-profile-patient.html', {'name_form': name_form, 'picture_form': picture_form,'patient':patient})


@role_required('doctor')
def edit_profile_doctor(request):
    doctor = Doctor.objects.get(user=request.user)  # Get the doctor associated with the logged-in user
    
    if request.method == 'POST':
        name_form = UpdateNameForm(request.POST, instance=request.user)
        picture_form = UpdateProfilePictureForm(request.POST, request.FILES, instance=doctor)

        if name_form.is_valid() and picture_form.is_valid():
            name_form.save()
            picture_form.save()
            messages.success(request, 'Your profile was updated.')
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
def _chat_between(user_a, user_b):
    """The existing chat between two users, or None."""
    ids = Message.objects.filter(Q(sender=user_a, recipient=user_b) | Q(sender=user_b, recipient=user_a)).values_list('chat_id', flat=True)
    return Chat.objects.filter(id__in=list(ids)).order_by('-timestamp').first()


def _can_chat(user, other):
    """Patients talk to approved doctors; doctors talk to approved patients."""
    if user == other or not is_approved(other):
        return False
    return {get_role(user), get_role(other)} == {'doctor', 'patient'}


def _chat_base(user):
    return 'hospital/doctor_base.html' if is_doctor(user) else 'hospital/patient_base.html'


def _conversation_list(user):
    latest = Message.objects.filter(chat=OuterRef('chat')).order_by('-timestamp').values('id')[:1]
    return Message.objects.filter(id__in=Subquery(latest)).filter(Q(sender=user) | Q(recipient=user)).order_by('-timestamp')


@role_required('doctor', 'patient')
def send_message(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)
    if not _can_chat(request.user, recipient):
        messages.warning(request, 'Patients can message doctors, and doctors can message patients.')
        return redirect('message_list')
    existing = _chat_between(request.user, recipient)
    if existing:
        return redirect('message_list', chat_id=existing.id, recipient_id=recipient.id)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            new_chat = Chat.objects.create()
            Message.objects.create(sender=request.user, recipient=recipient, chat=new_chat, content=content)
            return redirect('message_list', chat_id=new_chat.id, recipient_id=recipient.id)
        messages.error(request, 'Please type a message first.')
    return render(request, 'hospital/message_list.html', {'messages': _conversation_list(request.user), 'recipient': recipient, 'sidebar': _chat_base(request.user)})


@role_required('doctor', 'patient')
def message_list(request, recipient_id=None, chat_id=None):
    current_chat = Chat.objects.filter(id=chat_id).first() if chat_id else None
    chat_messages = []
    other = None
    if current_chat is not None:
        chat_messages = Message.objects.filter(chat=current_chat).order_by('timestamp')
        first = chat_messages.filter(Q(sender=request.user) | Q(recipient=request.user)).first()
        if first is None:
            # Not a participant: never show another person's conversation.
            current_chat, chat_messages = None, []
        else:
            other = first.recipient if first.sender_id == request.user.id else first.sender

    if request.method == 'POST' and current_chat is not None:
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(chat=current_chat, sender=request.user, recipient=other, content=content)
        return redirect('message_list', chat_id=current_chat.id, recipient_id=other.id)

    return render(request, 'hospital/message_list.html', {
        'is_doctor': is_doctor(request.user),
        'messages': _conversation_list(request.user),
        'chatMessage': chat_messages,
        'recipient': request.user,
        'chat_id': current_chat.id if current_chat else None,
        'sidebar': _chat_base(request.user),
    })


@role_required('doctor', 'patient')
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

@role_required('patient')
def select_doctor(request):
    patient = get_profile(request.user)
    if request.method == 'POST':
        form = SelectDoctorForm(request.POST)
        if form.is_valid():
            doctor_user = form.cleaned_data['doctor'].user
            existing = _chat_between(request.user, doctor_user)
            if existing:
                return redirect('message_list', chat_id=existing.id, recipient_id=doctor_user.id)
            return redirect('send_message', recipient_id=doctor_user.id)
    else:
        form = SelectDoctorForm()
    return render(request, 'hospital/select_doctor.html', {'form': form, 'patient': patient})


@role_required('doctor')
def doctor_messages(request):
    current_doctor = request.user

    # Filter messages where recipient_id matches the current doctor's ID
    messages = Message.objects.filter(recipient_id=current_doctor.id).order_by('-timestamp')

    return render(request, 'hospital/doctor_messages.html', {'messages': messages})


#---------ADMIN: read access to every record in the medical center
@role_required('admin')
def admin_prescriptions_view(request):
    prescriptions = Prescription.objects.select_related('doctor__user', 'patient__user').order_by('-date', '-id')
    return render(request, 'hospital/admin_prescriptions.html', {'prescriptions': prescriptions})


@role_required('admin')
def admin_blog_view(request):
    posts = Post.objects.select_related('author').order_by('-date_posted')
    return render(request, 'hospital/admin_blog.html', {'posts': posts})


#---------SIGN OUT: works from any button or link, always lands on the home page
def logout_view(request):
    from django.contrib.auth import logout
    was_signed_in = request.user.is_authenticated
    logout(request)
    if was_signed_in:
        messages.success(request, 'You have been signed out.')
    return redirect('HOME')
