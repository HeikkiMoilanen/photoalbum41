from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from models import Customer

# This is the form used for creating the user account. It is based on django.contrib.auth's 
# UserCreationForm, but extends the default form by e-mail, first_name and last_name fields.

class MyRegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email', 'first_name', 'last_name')
        
    def save(self, commit=True):
        user = super(MyRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save() 
        return user

# This form is based on the Customer model and extends the user profile with
# street address, postal code, city and country. Used for creating the user account.
        
class CustomerForm(forms.ModelForm):
    
    class Meta:
        model = Customer 
        fields = ('street_address', 'postal_code', 'city', 'country')

# A form used for updating the some fields in the user account. Based on the User model. 
        
class MyUserChangeForm(forms.ModelForm):
        
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

