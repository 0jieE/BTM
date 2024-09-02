from django import forms
from crispy_forms.helper import FormHelper
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, UsernameField, PasswordResetForm, SetPasswordForm
from crispy_forms.layout import Submit
from .models import Business, User, Staff_user, BusinessYear, Admin_user
from django.utils.translation import gettext_lazy as _

class LoginForm(forms.Form):
  username = UsernameField(label=_("Your Username"), widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}))
  password = forms.CharField(
      label=_("Your Password"),
      strip=False,
      widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}),
  )

class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))

class StaffRegistrationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"}))

    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "First name",
                "class": "form-control"}))

    middle_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Middle name",
                "class": "form-control"}))

    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Last name",
                "class": "form-control"}))

    extension_name = forms.CharField(
        required=False,  # Make the field optional
        widget=forms.TextInput(
            attrs={
                "placeholder": "Extension name",
                "class": "form-control"}))

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"}))

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control"}))

    class Meta:
        model = Staff_user
        fields = ('username','first_name','middle_name','last_name','extension_name','password1', 'password2')


class AdminRegistrationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"}))

    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "First name",
                "class": "form-control"}))

    middle_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Middle name",
                "class": "form-control"}))

    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Last name",
                "class": "form-control"}))

    extension_name = forms.CharField(
        required=False,  # Make the field optional
        widget=forms.TextInput(
            attrs={
                "placeholder": "Extension name",
                "class": "form-control"}))

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"}))

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control"}))

    class Meta:
        model = Admin_user
        fields = ('username','first_name','middle_name','last_name','extension_name','password1', 'password2')

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if not data and initial:
            return initial
        elif data and not isinstance(data, list):
            return [data]
        return data

class MultiplePictureForm(forms.Form):
    business_no = forms.ModelChoiceField(queryset=Business.objects.all(), widget=forms.HiddenInput())
    pictures = MultipleFileField()

    def __init__(self, *args, **kwargs):
        super(MultiplePictureForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Upload'))


class UploadBusinessFileForm(forms.Form):
    file = forms.FileField(label='Select a file')

    def __init__(self, *args, **kwargs):
        super(UploadBusinessFileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Upload'))

class UploadCollectionFileForm(forms.Form):
    file = forms.FileField(label='Select a Collection file')

    def __init__(self, *args, **kwargs):
        super(UploadCollectionFileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Upload'))

class YearSelectionForm(forms.Form):
    year = forms.ChoiceField(
        choices=[(year, year) for year in BusinessYear.objects.values_list('year', flat=True).distinct().order_by('year')],
        label='Select Year',
        required=True,
    )


class EditLocationForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ['latitude', 'longitude']
        widgets = {
            'latitude': forms.NumberInput(attrs={'class': 'form-control','id':'lat'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control','id':'long'}),
        }

    def clean_latitude(self):
        latitude = self.cleaned_data.get('latitude')
        if latitude:
            latitude = round(latitude, 6)
        return latitude

    def clean_longitude(self):
        longitude = self.cleaned_data.get('longitude')
        if longitude:
            longitude = round(longitude, 6)
        return longitude



