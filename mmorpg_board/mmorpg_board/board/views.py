from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.views.generic import DetailView, DeleteView
from django.views.generic.list import ListView
from django_filters.views import FilterView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.mail import EmailMessage
from .models import Board, Response, Subscriber
from .forms import AdForm, ResponseForm, SubcriberForm, ConfirmManagerForm, MassSendingForm
from .tasks import weekly_mailing
from .filters import ResponseFilter


@login_required
def subscribe_form_view(request):
    try:
        subscriber = Subscriber.objects.get(user=request.user)
        form = SubcriberForm(initial={'category': subscriber.categories})
    except Subscriber.DoesNotExist:
        form = SubcriberForm()

    if request.method == 'POST':
        form = SubcriberForm(request.POST)
        if form.is_valid():
            categories = form.cleaned_data['category']
            Subscriber.objects.update_or_create(
                user=request.user,
                defaults={'categories': categories}
            )
            return redirect('subscribe_form')

    return render(request, 'board/subscribe_form.html', {'form': form})


@login_required
def add_manager_view(request):
    if request.user.groups.filter(name='managers').exists():
        return render(request, 'board/partials/manager.html', {'form': None})

    form = ConfirmManagerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        group = Group.objects.get(name='managers')
        group.user_set.add(request.user)
        return render(request, 'board/partials/manager.html', {'manager_is_added': True})

    return render(request, 'board/partials/manager.html', {'form': form})


@login_required
@permission_required('board.can_send_mass_email', raise_exception=True)
def send_news_view(request):
    if request.method == 'POST':
        form = MassSendingForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            text = form.cleaned_data['text']
            recipients = User.objects.filter(is_active=True).values_list('email', flat=True)

            email = EmailMessage(
                subject=subject,
                body=text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.DEFAULT_FROM_EMAIL],
                bcc=list(recipients),
            )
            email.send()
            return render(request, 'board/partials/mass_send.html')
    else:
        form = MassSendingForm()

    return render(request, 'board/partials/mass_send.html', {'form': form})


class AdListView(ListView):
    model = Board
    template_name = 'board/ads.html'
    context_object_name = 'ad'
    ordering = ['-created_at']
    paginate_by = 5


class AdDetailView(DetailView):
    model = Board
    template_name = 'board/ad_card.html'
    context_object_name = 'ad'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            ad = self.get_object()
            try:
                response = Response.objects.get(ad=ad, author=self.request.user)
                context['response'] = response
            except Response.DoesNotExist:
                pass
        return context


class AdCreateView(LoginRequiredMixin, CreateView):
    model = Board
    form_class = AdForm
    template_name = 'board/ad_create_update.html'
    success_url = reverse_lazy('ad_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class AdUpdateView(LoginRequiredMixin, UpdateView):
    model = Board
    form_class = AdForm
    template_name = 'board/ad_create_update.html'
    success_url = reverse_lazy('ad_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context


class ResponseListView(LoginRequiredMixin, FilterView):
    model = Response
    template_name = 'board/responses.html'
    context_object_name = 'responses'
    paginate_by = 5
    filterset_class = ResponseFilter

    def get_queryset(self):
        queryset = Response.objects.filter(ad__author=self.request.user)
        return queryset.order_by('-created_at')


class ResponseCreateView(LoginRequiredMixin, CreateView):
    model = Response
    form_class = ResponseForm
    template_name = 'board/ad_card.html'
    success_url = reverse_lazy('ad_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ad_id = self.kwargs['ad_id']
        context['ad'] = Board.objects.get(id=ad_id)
        context['response_create'] = True

        if self.request.user.is_authenticated:
            try:
                response = Response.objects.get(ad_id=ad_id, author=self.request.user)
                context['response'] = response
            except Response.DoesNotExist:
                pass

        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.ad = Board.objects.get(id=self.kwargs['ad_id'])
        return super().form_valid(form)


class ResponseUpdateView(LoginRequiredMixin, UpdateView):
    model = Response
    fields = []
    template_name = 'board/partials/confirm_response_accept.html'
    success_url = reverse_lazy('responses')

    def dispatch(self, request, *args, **kwargs):
        response = self.get_object()
        if request.user != response.ad.author:
            raise PermissionDenied('Запрещено работать с откликами на чужие объявления')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.is_accepted = True
        return super().form_valid(form)


class ResponseDeleteView(LoginRequiredMixin, DeleteView):
    model = Response
    success_url = reverse_lazy('responses')
    template_name = 'board/partials/confirm_response_delete.html'

    def dispatch(self, request, *args, **kwargs):
        response = self.get_object()
        if request.user != response.ad.author:
            raise PermissionDenied('Нельзя удалять отклики на чужие объявления')
        return super().dispatch(request, *args, **kwargs)


@login_required
@permission_required('board.can_send_mass_email', raise_exception=True)
def test_view(request):
    return render(request, 'test.html')


def ads_view(request):
    return render(request, 'board/partials/msg.html', {'user': 'mhggh'})
