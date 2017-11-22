from django import forms

class sign_up_form(forms.Form):
    username = forms.CharField(label='Username', max_length=150, required=True)
    email = forms.EmailField(label='Email', required=True)
    password = forms.CharField(label='Password', required=True)

class sign_in_form(forms.Form):
    username = forms.CharField(label='Username', max_length=150, required=True)
    password = forms.CharField(label='Password', required=True)
