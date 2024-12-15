from django.db.models import F
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Question


class FutureQuestionsFilterMixin:
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class IndexView(FutureQuestionsFilterMixin, generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return super().get_queryset().order_by("-pub_date")[:5]


class DetailView(FutureQuestionsFilterMixin, generic.DetailView):
    model = Question
    template_name = "polls/detail.html"


class ResultsView(FutureQuestionsFilterMixin, generic.DetailView):
    model = Question
    template_name = "polls/results.html"


def vote(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if question.pub_date > timezone.now():
        raise Http404
    if not request.POST.get("choice", None):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    selected_choice = question.choice_set.get(pk=request.POST["choice"])
    selected_choice.votes = F("votes") + 1
    selected_choice.save()
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
