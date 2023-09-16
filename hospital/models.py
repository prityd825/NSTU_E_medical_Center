from django.db import models
from django.contrib.auth.models import User


#BlogPost



from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
#from .models import Post 





departments=[('Cardiologist','Cardiologist'),
('Dermatologists','Dermatologists'),
('Emergency Medicine Specialists','Emergency Medicine Specialists'),
('Allergists/Immunologists','Allergists/Immunologists'),
('Anesthesiologists','Anesthesiologists'),
('Colon and Rectal Surgeons','Colon and Rectal Surgeons')
]
class Doctor(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/DoctorProfilePic/',null=True,blank=True)
    address = models.CharField(max_length=40)
    email = models.EmailField(default='')
    department= models.CharField(max_length=50,choices=departments,default='Cardiologist')
    status=models.BooleanField(default=False)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return "{} ({})".format(self.user.first_name,self.department)
    def iden():
        return "doctor"


class Accountant(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/AccountantProfilePic/',null=True,blank=True)
    address = models.CharField(max_length=40)
    email = models.EmailField(default='')
    status=models.BooleanField(default=False)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
   





class Patient(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/PatientProfilePic/',null=True,blank=True)
    address = models.CharField(max_length=40)
    email = models.EmailField(default='')
    # symptoms = models.CharField(max_length=100,null=False)
    # assignedDoctorId = models.PositiveIntegerField(null=True)
    admitDate=models.DateField(auto_now=True)
    status=models.BooleanField(default=False)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return self.user.first_name
    def iden(self):
        return "patient"


class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE,null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE,null=True)
    patientId=models.PositiveIntegerField(null=True)
    doctorId=models.PositiveIntegerField(null=True)
    patientName=models.CharField(max_length=40,null=True)
    doctorName=models.CharField(max_length=40,null=True)
    appointmentDate=models.DateField(auto_now=True)
    description=models.TextField(max_length=500)
    status=models.BooleanField(default=False)



#BlogPost

class Post(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE,null=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
            return self.title


    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})
    
from django.db import models

class Medicine(models.Model):
    date = models.DateField()
    medicinename = models.CharField(max_length=100)
    companyname = models.CharField(max_length=100)
    stock = models.IntegerField()

    def __str__(self):
        return self.medicinename




class PatientFeedback(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True)
    patientName = models.CharField(max_length=100)
    email = models.EmailField()
    feedback = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Feedback from {self.patient_name} ({self.email})"    
    


from django.db import models

class Prescription(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    symptoms = models.TextField()
    
    medicine1 = models.TextField(null=True)
    medicine1Count = models.IntegerField(null=True)
    medicine2 = models.TextField(null=True)
    medicine2Count = models.IntegerField(null=True)
    medicine3 = models.TextField(null=True)
    medicine3Count = models.IntegerField(null=True)
    medicine4 = models.TextField(null=True)
    medicine4Count = models.IntegerField(null=True)
    medicine5 = models.TextField(null=True)
    medicine5Count = models.IntegerField(null=True)

    extraMedicine = models.TextField(null=True)
    advice = models.TextField(null=True)

    tests = models.TextField()

class Chat(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='chat', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages_box', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages_box', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)