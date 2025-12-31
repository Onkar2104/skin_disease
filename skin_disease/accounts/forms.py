from django import forms 
# from django.contrib.auth.models import User
from .models import User
from django.contrib.auth.forms import ReadOnlyPasswordHashField


class UserAdminCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'age', 'gender', 'skin_type']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_2 = cleaned_data.get("password_2")
        if password is not None and password != password_2:
            self.add_error("password_2", "Your password must match..!")
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
    

class UserAdminChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'password', 'age', 'gender', 'skin_type', 'is_active', 'is_staff']


    def clean_password(self):
        return self.initial["password"]