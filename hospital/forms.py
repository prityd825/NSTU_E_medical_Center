from django import forms
from django.core import validators
from django.contrib.auth.models import User
from . import models
from hospital import models



#for admin signup
class AdminSigupForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }
        
 #for accountant signup   
class AccountantUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','email','password']
        widgets = {
        'password': forms.PasswordInput()
        }    


class AccountantForm(forms.ModelForm):
    class Meta:
        model=models.Accountant
        fields=['address','status','profile_pic']





class DoctorUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','email','password']
        widgets = {
        'password': forms.PasswordInput()
        }
class DoctorForm(forms.ModelForm):
    class Meta:
        model=models.Doctor
        fields=['address','department','status','profile_pic']



class PatientUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','email','password']
        widgets = {
        'password': forms.PasswordInput()
        }
class PatientForm(forms.ModelForm):
    
    # assignedDoctorId=forms.ModelChoiceField(queryset=models.Doctor.objects.all().filter(status=True),empty_label="Name and Department", to_field_name="user_id")
    class Meta:
        model=models.Patient
        fields=['address','status','profile_pic']



class AppointmentForm(forms.ModelForm):
    doctorId=forms.ModelChoiceField(queryset=models.Doctor.objects.all().filter(status=True),empty_label="Doctor Name and Department", to_field_name="user_id")
    patientId=forms.ModelChoiceField(queryset=models.Patient.objects.all().filter(status=True),empty_label="Patient Name and Symptoms", to_field_name="user_id")
    class Meta:
        model=models.Appointment
        fields=['description','status']


class PatientAppointmentForm(forms.ModelForm):
    doctorId=forms.ModelChoiceField(queryset=models.Doctor.objects.all().filter(status=True),empty_label="Doctor Name and Department", to_field_name="user_id")
    class Meta:
        model=models.Appointment
        fields=['description','status']






class MedicineRecordForm(forms.ModelForm):
    class Meta:
        model = models.Medicine
        fields=['date','medicinename', 'companyname','stock']

from .models import PatientFeedback

class PatientFeedbackForm(forms.ModelForm):
    class Meta:
        model = PatientFeedback
        fields = ['patientName', 'email', 'feedback']

# from django import forms
from .models import Patient

# class PatientProfileUpdateForm(forms.ModelForm):
#     class Meta:
#         model = Patient
#         fields = ['profile_pic']

class UpdateNameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name']

class UpdateProfilePictureForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['profile_pic']


from django import forms
from .models import Doctor, Message, Chat, Medicine

class SelectDoctorForm(forms.Form):
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.all(),
        empty_label="Select a Doctor"
    )

class SelectMedicineForm(forms.Form):
    medicine1 = forms.ModelChoiceField(
        queryset=Medicine.objects.all(),
        required=False,
        empty_label="Select a Medicine"
    )

    medicine1Count = forms.IntegerField(
        required=False,
        label="How many medicine for Medicine 1"
        )

    medicine2 = forms.ModelChoiceField(
        queryset=Medicine.objects.all(),
        required=False,
        empty_label="Select a Medicine"
    )

    medicine2Count = forms.IntegerField(required=False,label="How many medicine for Medicine 2")

    medicine3 = forms.ModelChoiceField(
        queryset=Medicine.objects.all(),
        required=False,
        empty_label="Select a Medicine"
    )
    
    medicine3Count = forms.IntegerField(required=False,label="How many medicine for Medicine 3")

    medicine4 = forms.ModelChoiceField(
        queryset=Medicine.objects.all(),
        required=False,
        empty_label="Select a Medicine"
    )

    medicine4Count = forms.IntegerField(
        required=False,
        label="How many medicine for Medicine 4")

    medicine5 = forms.ModelChoiceField(
        queryset=Medicine.objects.all(),
        required=False,
        empty_label="Select a Medicine"
    )

    medicine5Count = forms.IntegerField(
        required=False,
        label="How many medicine for Medicine 5")


class MessageForm(forms.ModelForm):
    class Meta:
        model=Message
        fields=['sender', 'recipient', 'content']