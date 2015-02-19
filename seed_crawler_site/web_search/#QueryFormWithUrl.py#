from django import forms
import QueryForm

def populate_urls(results):
    index = 1
    CHOICES = []
    for result in results:
        CHOICES.append((str(index),result))
        
    fields = {'choice_field',forms.ChoiceField(widget=forms.RadioSelect, choices=tuple(CHOICES))}
    return type('QueryFormWithUrl', (QueryForm.QueryForm,), { 'base_fields': fields })

        
