from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

# Create your views here.
class LoginView(LoginView):
    template_name = 'login/login.html'
    
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
class LogoutView(LoginRequiredMixin, LogoutView):
    next_page = reverse_lazy('login')
    
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'login/home.html'