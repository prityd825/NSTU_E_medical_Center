from django.contrib import admin
from .models import Doctor,Patient,Appointment, Accountant 
from .models import Post
# Register your models here.
class DoctorAdmin(admin.ModelAdmin):
    pass
admin.site.register(Doctor, DoctorAdmin)

#------------------------
class AccountantAdmin(admin.ModelAdmin):
    pass
admin.site.register(Accountant, AccountantAdmin)




class PatientAdmin(admin.ModelAdmin):
    pass
admin.site.register(Patient, PatientAdmin)

class AppointmentAdmin(admin.ModelAdmin):
    pass
admin.site.register(Appointment, AppointmentAdmin)


admin.site.register(Post)
