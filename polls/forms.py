from django import forms

from .models import Question, Choice


class QuestionCreateForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'pub_date']


class ChoiceCreateForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text']
