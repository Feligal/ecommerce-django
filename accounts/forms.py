
from django import forms
from django.forms import CharField, ModelForm, PasswordInput
from .models import Account


class RegistrationForm(ModelForm):
    password =  CharField(widget=PasswordInput(attrs={
        'placeholder':'Enter Password'
    }))

    confirm_password =  CharField(widget=PasswordInput(attrs={
        'placeholder':'Confirm password'
    }))

    class Meta:
        model = Account
        fields = ['first_name','last_name','phone_number','email', 'password']
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm,self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
    
        """
        Can  also be done like this below
        for name,field in self.fields.items():
            field.widget.attrs.update({
                'class':'form-control',
            })
        """
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super(RegistrationForm,self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match."
            )