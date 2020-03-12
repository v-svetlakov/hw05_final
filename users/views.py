from django.urls import reverse_lazy
from django.views.generic import CreateView
import datetime as dt
from .forms import CreationForm
from django.core.mail import send_mail
from django.shortcuts import redirect


class SignUp(CreateView):
        form_class = CreationForm
        success_url = "/auth/login/"
        template_name = "signup.html"


def year(request):
    """
    Добавляет переменную с текущим годом.
    """
    year = dt.datetime.now().year
    return {
        'year':year
    }

send_mail(
        'Тема письма',
        'Текст письма.',
        'from@example.com',  # Это поле От:
        ['to@example.com'],  # Это поле Кому:
        fail_silently=False,
)

def user_contact(request):

    if request.method == 'POST':

        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            cc_myself = form.cleaned_data['cc_myself']
            return redirect('/thank-you/')
        return render(request, 'contact.html', {'form': form})

    form = ContactForm()
    return render(request, 'contact.html', {'form': form})

