# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from supercaptcha import CaptchaField

class LoginForm(forms.Form):
    username = forms.CharField(label=_(u"Username"), max_length=64, required=True)
    password = forms.CharField(label=_(u"Password"), max_length=64, required=True, widget=forms.PasswordInput())
    remember = forms.BooleanField(label=_(u"Remember me"), required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    return cleaned_data
                else:
                    raise forms.ValidationError(_(u"User is blocked."))

            raise forms.ValidationError(_(u"Wrong username or password."))

class RegistrationForm(forms.Form):
    username = forms.RegexField(label=_(u"Username"), required=True, regex=r'^[\w.@+-]+$',
        widget=forms.TextInput(attrs={'class': 'span3'}))

    password = forms.CharField(label=_(u"Password"), required=True, min_length=6, max_length=64,
        widget=forms.PasswordInput(attrs={'class': 'span3'}),
        help_text=_(u"Min 6 simbols, max 64."))
    password2 = forms.CharField(label=_(u"Password again"), required=True, max_length=64,
        min_length=6, widget=forms.PasswordInput(attrs={'class': 'span3'}))

    email = forms.EmailField(label=_(u"E-mail"), required=False, max_length=64,
        widget=forms.TextInput(attrs={'class': 'span3'}))

    captcha = CaptchaField(label=_(u"Secret code"), required=True,
        help_text=_(u"Input text from captcha."))

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password == password2:
            return password2

        raise forms.ValidationError(u"Passwords not same.")

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError(_(u"Input username"))

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise forms.ValidationError(_(u'Username not free.'))


class ResetPasswordForm(forms.Form):
    password = forms.CharField(label=_(u"New password"), required=True, min_length=6, max_length=64,
        widget=forms.PasswordInput(attrs={'class': 'span4'}),
        help_text=_(u"Минимум 6 символов, максимум 64."))
    password2 = forms.CharField(label=_(u"New password again"), required=True, max_length=64,
        min_length=6, widget=forms.PasswordInput(attrs={'class': 'span4'}))

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password == password2:
            return password2

        raise forms.ValidationError(_(u"Passwords not same."))


class PasswordRestoreForm(forms.Form):
    email = forms.EmailField(label=_(u"E-mail"), required=True)
    captcha = CaptchaField(label=_(u"Secret code"), required=True)


    def clean(self):
        cleaned_data = self.cleaned_data
        username = cleaned_data.get('username','')
        email = cleaned_data.get('email','')
        if not email:
            raise forms.ValidationError(_(u"Wrong email"))

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError(_(u"User with email not found"))

        return cleaned_data


class ProfileForm(forms.Form):
    email = forms.EmailField(label=_(u"E-mail"), required=False)


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label=u"Old pasword", required=True, min_length=6, max_length=64,
        widget=forms.PasswordInput(attrs={'class': 'span4'}))
    password = forms.CharField(label=u"New password", required=True, min_length=6, max_length=64,
        widget=forms.PasswordInput(attrs={'class': 'span4'}),
        help_text=u"Min 6, max 64 simbols.")
    password2 = forms.CharField(label=u"New password again", required=True, max_length=64,
        min_length=6, widget=forms.PasswordInput(attrs={'class': 'span4'}))

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password == password2:
            return password2

        raise forms.ValidationError(u"Passwords not same.")


    def check_old_password(self, user):
        old_password = self.cleaned_data['old_password']
        user = authenticate(username=user.username, password=old_password)
        if not user is None:
            return True
        else:
            return False
