from cProfile import Profile
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from cart.models import Cart, CartItem
from cart.views import _get_cart_id

from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile

# Create your views here.


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            password = form.cleaned_data["password"]
            phone_number = form.cleaned_data["phone_number"]
            confirm_password = form.cleaned_data["confirm_password"]
            email = form.cleaned_data["email"]
            username = email.split('@')[0]

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, username=username,
                                               email=email, password=password)
            user.phone_number = phone_number
            user.save()

            # send Verification
            current_site = get_current_site(request)
            mail_subject = " Please Activate your Account"
            message = render_to_string("accounts/account_verification_email.html", {
                "user": user,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),

            })

            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])

            send_email.send()

            # messages.success(request, "Thank You for registering with us. We have a sent you a mail []!")
            return redirect('/accounts/login/?command=verification&email=' + email)
    else:
        form = RegistrationForm()
        context = {
            "form": form,
        }
        return render(request, "accounts/register.html", context)


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                # cart = Cart.objects.get(cart=_get_cart_id(request))
                # cart_item = CartItem.filter(cart=cart).exists()
                is_in_cart = CartItem.objects.filter(
                    cart__cart_id=_get_cart_id(request)).exists()
                if is_in_cart:
                    cart_item = CartItem.objects.get(
                        cart__cart_id=_get_cart_id(request))
                    cart_item.user = user
                    cart_item.save()

            except:
                pass

            auth.login(request, user)
            messages.success(request, "You're Logged In!")
            return redirect('dashboard')

        # user = Account.objects.get(email=email)
        # if user.password == password:

        else:
            messages.error(request, "Invalid Login Credentials")
            return redirect('login')
    else:

        return render(request, "accounts/login.html")


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, "You are logged out")
    return redirect('login')


def activate(request, uidb64, token):
    try:
        user_pk = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=user_pk)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request, "Congratulations! Your account is activated.")
        return redirect('login')

    else:
        messages.error(request, "Invalid Activation Link")
        return redirect('register')


@login_required(login_url='login')
def dashboard(request):
    return render(request, "accounts/dashboard.html")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST["email"]

        # user = auth.authenticate(email=email)
        if Account.objects.filter(email__iexact=email).exists():
            user = Account.objects.get(email__iexact=email)
            if user is not None:
                current_site = get_current_site(request)
                email_subject = "Create a new  Password"
                message = render_to_string("accounts/reset_password_email.html", {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user)
                })

                email_to = email
                send_email = EmailMessage(
                    email_subject, message, to=[email_to])
                send_email.send()
                messages.success(
                    request, "Password reset email has  been sent to email address")
                return redirect('login')
            else:
                messages.error(request, "Invalid User Credential")
                return redirect('forgot-password')

    return render(request, "accounts/forgot_password.html")

# checks the token and uid from the email sent  and saves the user_pk in the session
# Runs only when the email link is clicked


def reset_password_validate(request, uidb64, token):

    try:
        user_pk = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=user_pk)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = user_pk  # the uid used to get user_pk
        messages.success(request, "Please reset your password")
        return redirect("reset-password")
    else:
        messages.error(request, "This Link has been expired")
        return redirect('forgot-password')


def reset_password(request):

    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            user_pk = request.session.get("uid")
            user = Account.objects.get(pk=user_pk)
            if user:
                user.set_password(password)  # hashes the password
                user.save()
                messages.success(
                    request,  "Password Reset Successful,Please login with your new password")
                return redirect('login')
        else:
            messages.error(
                request, "Passwords doesn't match. Please Input again")
            return redirect('reset-password')
    else:
        return render(request, "accounts/reset_password.html")


def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=user_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your Update was saved successfully")
            return redirect('edit-profile')

    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    context = {
        "user_form": user_form,
        "profile_form": profile_form
    }

    return render(request, "accounts/edit_profile.html", context)
