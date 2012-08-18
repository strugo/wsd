# -*- coding: utf-8 -*-

from django.shortcuts import redirect, render_to_response, Http404, HttpResponse
from django.template import RequestContext
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from .models import  PasswordRestoreQueue
from .forms import LoginForm, PasswordRestoreForm, ResetPasswordForm, RegistrationForm, ProfileForm, ChangePasswordForm
from .utils import send_email

SITE_URL = getattr(settings, 'SITE_URL','http://localhost:8000')

def login_page(request):
    form = LoginForm()
    next = request.GET.get('next','')

    if request.user.is_authenticated():
        return redirect("logout_page")

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, user)
            remember = form.cleaned_data.get('remember')
            if not remember:
                request.session.set_expiry(0)
            if next:
                return redirect(next)
            else:
                return redirect("main_page")

    data = {
        'form': form,
        }

    return render_to_response("account/login.html", data, context_instance=RequestContext(request))


@login_required
def logout_page(request):
    logout(request)
    return redirect("main_page")


def registration_page(request):
    if request.user.is_authenticated():
        return redirect("main_page")
    form = RegistrationForm()

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data['username'], email=form.cleaned_data['email'],
                password=form.cleaned_data['password2'])
            user.is_active=True
            user.save()
            profile = user.get_profile()
            profile.save()
            messages.success(request, _(u"You have been registered."))
            return redirect("main_page")

    data = {
        'form': form,
        }

    return render_to_response("account/registration.html", data, context_instance=RequestContext(request))


def restore_password(request):
    if request.user.is_authenticated():
        return redirect("main_page")

    success = False
    form = PasswordRestoreForm()

    if request.method == 'POST':
        form = PasswordRestoreForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(email=email, username=username)
                aq = PasswordRestoreQueue.objects.create_queue(user=user)
                url = aq.get_absolute_url()
                send_email(request, user, _(u"Password restore"), 'account/email/password_restore.html', {'url': url, })
                messages.success(request, _(u"Watch your email for next step."))
                success = True
            except User.DoesNotExist:
                messages.error(request, _(u"E-mail not found"))

    data = {
        'form': form,
        'success': success,
        }

    return render_to_response("account/password_restore.html", data, context_instance=RequestContext(request))


def reset_password_page(request, uuid):
    if request.user.is_authenticated():
        return redirect("main_page")

    try:
        aq = PasswordRestoreQueue.objects.get(uuid=uuid)
        if not aq.is_active():
            raise Http404()
    except PasswordRestoreQueue.DoesNotExist:
        raise Http404()

    form = ResetPasswordForm()

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            aq.user.set_password(form.cleaned_data['password2'])
            aq.user.save()
            aq.delete()
            messages.success(request, _(u"Password was changed."))
            return redirect("login_page")

    data = {
        'form': form,
        }

    return render_to_response("account/password_reset.html", data, context_instance=RequestContext(request))


@login_required
def profile_settings(request):
    profile = request.user.get_profile()
    user = request.user
    form1 = ProfileForm(initial={'email': user.email,  })
    form2 = ChangePasswordForm()

    if request.method == 'POST':
        action = request.POST.get('action','')
        if action == 'profile':
            form1 = ProfileForm(request.POST)
            if form1.is_valid():
                profile.city = form1.cleaned_data.get('city',)
                profile.save()
                if form1.cleaned_data.get('email',''):
                    user.email = form1.cleaned_data.get('email','')
                    user.save()
                messages.success(request, u"Saved.")
                return redirect("settings_page")
            else:
                messages.error(request, u"Check errors")
        elif action == 'password':
            form2 = ChangePasswordForm(request.POST)
            if form2.is_valid():
                user = request.user
                user.set_password(form2.cleaned_data['password2'])
                user.save()
                logout(request)
                messages.success(request, u"Saved. Re-login please.")
                return redirect("home_page")
            else:
                messages.error(request, u"Check errors")

    data = {
        'form1': form1,
        'form2': form2,
        }

    return render_to_response("account/profile/settings.html", data, context_instance=RequestContext(request))

