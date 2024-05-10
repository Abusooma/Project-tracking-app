from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import NewUser
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from admin_material.forms import RegistrationForm, CustomLoginForm, UserPasswordResetForm, UserSetPasswordForm, \
    UserPasswordChangeForm


# Create your views here.

# Pages
def index(request):
    return render(request, 'pages/index.html', {'segment': 'index'})


def create_project(request):
    return render(request, 'pages/create_project.html', {'segment': 'create_project'})


def billing(request):
    return render(request, 'pages/billing.html', {'segment': 'billing'})


def tables(request):
    return render(request, 'pages/tables.html', {'segment': 'tables'})


def vr(request):
    return render(request, 'pages/virtual-reality.html', {'segment': 'vr'})


def rtl(request):
    return render(request, 'pages/rtl.html', {'segment': 'rtl'})


def notification(request):
    return render(request, 'pages/notifications.html', {'segment': 'notification'})


def profile(request):
    return render(request, 'pages/profile.html', {'segment': 'profile'})


def loginView(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                if not user.has_change_password and hasattr(user, 'chef_de_projet'):
                    login(request, user)
                    return redirect('password_change')
                login(request, user)
                return redirect('display')
            else:
                return redirect('login')
    else:
        form = CustomLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.has_change_password = True
            user.save()
            return redirect('/accounts/login/')
        else:
            print("Register failed!")
    else:
        form = RegistrationForm()

    context = {'form': form}
    return render(request, 'accounts/register.html', context)


def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')


class UserPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    form_class = UserPasswordResetForm


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = UserSetPasswordForm


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = UserPasswordChangeForm

    def form_valid(self, form):
        super().form_valid(form)
        self.request.user.has_change_password = True
        self.request.user.save()

        messages.success(self.request, 'Mot de passe changé avec success')
        return redirect('display')

