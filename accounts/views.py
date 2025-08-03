# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages


def home_view(request):
    """Vue pour la page d'accueil de bienvenue"""
    if request.user.is_authenticated:
        return redirect('chatbot:chat')  # Redirige vers le chatbot si déjà connecté
    return render(request, 'home.html')


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Compte créé avec succès et vous êtes connecté !")
            return redirect("chatbot:chat")  # Redirige vers la page du chatbot
        else:
            messages.error(request, "Erreur lors de la création du compte. Veuillez corriger les erreurs.")
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenue, {user.username} !")
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect("chatbot:chat")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':  # La déconnexion doit être une requête POST pour la sécurité
        logout(request)
        messages.info(request, "Vous avez été déconnecté.")
        return redirect('accounts:home')
    else:
        return redirect('accounts:home')  # Redirige si ce n'est pas une requête POST
