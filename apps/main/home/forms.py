from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, UsernameField, PasswordResetForm, SetPasswordForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.widgets import CKEditor5Widget
from django import forms
from .models import *


class UserProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'bio', 'cpf', 'gender')
        labels = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'email': _('Email'),
            'bio': _('Biography'),
            'cpf': _('CPF'),
            'gender': _('Gender'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['first_name', 'last_name', 'email', 'bio', 'gender']:
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})
        self.fields['cpf'].widget.attrs.update({'class': 'form-control', 'id': 'cpf'})


class AvatarForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar']
        labels = {
            'avatar': _('Profile Picture'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].widget.attrs.update({'class': 'form-control-file'})


class AddressUserForm(forms.ModelForm):
    class Meta:
        model = AddressUser
        fields = ['street', 'number', 'complement', 'neighborhood', 'city', 'state', 'postal_code']
        labels = {
            'street': _('Street'),
            'number': _('Number'),
            'complement': _('Complement'),
            'neighborhood': _('Neighborhood'),
            'city': _('City'),
            'state': _('State'),
            'postal_code': _('Postal Code'),
        }
        widgets = {
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'complement': forms.TextInput(attrs={'class': 'form-control'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
        }


class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Username')})
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('example@company.com')})
    )
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Password')})
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Confirm Password')})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    username = UsernameField(
        label=_("Your Username"),
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": _("Username")})
    )
    password = forms.CharField(
        label=_("Your Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("Password")}),
    )


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your email')
        })
    )


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        max_length=50,
        label=_("New Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('New Password')
        })
    )
    new_password2 = forms.CharField(
        max_length=50,
        label=_("Confirm New Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Confirm New Password')
        })
    )


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        max_length=50,
        label=_("Old Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Old Password')
        })
    )
    new_password1 = forms.CharField(
        max_length=50,
        label=_("New Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('New Password')
        })
    )
    new_password2 = forms.CharField(
        max_length=50,
        label=_("Confirm New Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Confirm New Password')
        })
    )


class DashboardContentForm(forms.ModelForm):
    class Meta:
        model = DashboardContent
        fields = ['slug', 'is_active']
        labels = {
            'slug': _('Slug'),
            'is_active': _('Active'),
        }
        widgets = {
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DashboardContentTranslationForm(forms.ModelForm):
    class Meta:
        model = DashboardContentTranslation
        fields = ['language', 'title', 'content']
        labels = {
            'language': _('Language'),
            'title': _('Title'),
            'content': _('Content'),
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name="extends"),
        }

    def __init__(self, *args, **kwargs):
        language = kwargs.pop('language', None)
        super().__init__(*args, **kwargs)
        if language:
            self.fields['language'].initial = language


class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        labels = {
            'username': _('Username'),
            'email': _('Email'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'is_active': _('Active'),
            'is_staff': _('Staff Status'),
            'is_superuser': _('Superuser Status'),
            'groups': _('Groups'),
            'user_permissions': _('User Permissions'),
            'password': _('Password'),
        }


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'password1', 'password2',
            'avatar', 'bio', 'cpf', 'gender',
            'is_email_verified', 'is_2fa_enabled', 'fichas',
        )
        labels = {
            'username': _('Username'),
            'email': _('Email'),
            'password1': _('Password'),
            'password2': _('Confirm Password'),
            'avatar': _('Profile Picture'),
            'bio': _('Biography'),
            'cpf': _('CPF'),
            'gender': _('Gender'),
            'is_email_verified': _('Email Verified'),
            'is_2fa_enabled': _('2FA Enabled'),
            'fichas': _('Credits'),
        }
