from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import QuestionCreateForm, ChoiceCreateForm
from .models import Question, Choice


def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)


def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def show_polls_with_choices(self):    
        return Poll.objects.exlude(choice_set__isnull=True)
        
    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['choice_form'] = ChoiceCreateForm()
        return context

    def post(self, request, pk):
        form = ChoiceCreateForm(request.POST)
        if form.is_valid:
            choice = form.save(commit=False)
            choice.question = Question.objects.get(pk=pk)
            choice.save()
            return HttpResponseRedirect(reverse('polls:detail', args=[pk]))
        # else if form is not valid
        context = {
            'choice_form': form,
            'question': Question.objects.get(pk=pk)
        }
        return render(request, 'polls/detail.html', context)


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


class QuestionCreateView(LoginRequiredMixin, generic.edit.CreateView):
    login_url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        context = {
            'form': QuestionCreateForm()
        }
        return render(request, 'polls/create.html', context)

    def post(self, request, *args, **kwargs):
        form = QuestionCreateForm(request.POST)
        if form.is_valid:
            question = form.save(commit=False)  # don't save the question yet
            question.author = request.user
            question.save()
            return HttpResponseRedirect(
                reverse('polls:detail', args=[question.id]))
        # else if form is not valid
        return render(request, 'polls/create.html', {'form': form})