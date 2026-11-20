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
        fields=['address','profile_pic']





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
        fields=['address','department','profile_pic']



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
        fields=['address','profile_pic']



class AppointmentForm(forms.ModelForm):
    doctorId=forms.ModelChoiceField(queryset=models.Doctor.objects.all().filter(status=True),empty_label="Select a doctor", to_field_name="user_id")
    patientId=forms.ModelChoiceField(queryset=models.Patient.objects.all().filter(status=True),empty_label="Select a patient", to_field_name="user_id")
    class Meta:
        model=models.Appointment
        fields=['description','status']


class PatientAppointmentForm(forms.ModelForm):
    doctorId=forms.ModelChoiceField(queryset=models.Doctor.objects.all().filter(status=True),empty_label="Select a doctor", to_field_name="user_id")
    class Meta:
        model=models.Appointment
        fields=['description']






class MedicineRecordForm(forms.ModelForm):
    class Meta:
        model = models.Medicine
        fields=['date','medicinename', 'companyname','stock']
        widgets = {'stock': forms.NumberInput(attrs={'min': 0})}

    def clean_stock(self):
        stock = self.cleaned_data['stock']
        if stock is not None and stock < 0:
            raise forms.ValidationError('Stock cannot be negative.')
        return stock

    def clean_medicinename(self):
        name = self.cleaned_data['medicinename'].strip()
        clash = models.Medicine.objects.filter(medicinename__iexact=name).exclude(pk=self.instance.pk)
        if clash.exists():
            raise forms.ValidationError('This medicine is already on record. Edit its stock instead of adding it again.')
        return name

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
        queryset=Doctor.objects.filter(status=True),
        empty_label="Select a Doctor"
    )

class MedicineChoiceField(forms.ModelChoiceField):
    """Shows the stock next to each medicine so doctors know what is available."""
    def label_from_instance(self, obj):
        return f"{obj.medicinename} ({obj.stock} in stock)"


class SelectMedicineForm(forms.Form):
    medicine1 = MedicineChoiceField(
        queryset=Medicine.objects.filter(stock__gt=0).order_by('medicinename'),
        required=False,
        empty_label="Select a Medicine"
    )

    medicine1Count = forms.IntegerField(
        required=False,
        label="How many medicine for Medicine 1"
        )

    medicine2 = MedicineChoiceField(
        queryset=Medicine.objects.filter(stock__gt=0).order_by('medicinename'),
        required=False,
        empty_label="Select a Medicine"
    )

    medicine2Count = forms.IntegerField(required=False,label="How many medicine for Medicine 2")

    medicine3 = MedicineChoiceField(
        queryset=Medicine.objects.filter(stock__gt=0).order_by('medicinename'),
        required=False,
        empty_label="Select a Medicine"
    )
    
    medicine3Count = forms.IntegerField(required=False,label="How many medicine for Medicine 3")

    medicine4 = MedicineChoiceField(
        queryset=Medicine.objects.filter(stock__gt=0).order_by('medicinename'),
        required=False,
        empty_label="Select a Medicine"
    )

    medicine4Count = forms.IntegerField(
        required=False,
        label="How many medicine for Medicine 4")

    medicine5 = MedicineChoiceField(
        queryset=Medicine.objects.filter(stock__gt=0).order_by('medicinename'),
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

class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=60, label='Your name')
    Email = forms.EmailField(label='Email address')
    Message = forms.CharField(max_length=1000, label='Message', widget=forms.Textarea(attrs={'rows': 5}))


class UserEditForm(forms.ModelForm):
    """Edit a user's name, username and email. Password is optional: leave it blank to keep the current one."""
    password = forms.CharField(required=False, widget=forms.PasswordInput(render_value=False),
                               label='New password', help_text='Leave blank to keep the current password.')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
