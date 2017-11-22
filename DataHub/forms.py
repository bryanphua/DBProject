from django import forms

class sign_up_form(forms.Form):
    username = forms.CharField(label='Username', max_length=150, required=True)
    first_name = forms.CharField(label='First name', max_length=30, required=True)
    last_name = forms.CharField(label='Last name', max_length=30, required=False)
    email = forms.EmailField(label='Email', required=True)
    password = forms.CharField(label='Password', required=True)
