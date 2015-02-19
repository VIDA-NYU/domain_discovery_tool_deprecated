from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
from django.utils.safestring import mark_safe
import QueryForm

from subprocess import call
from subprocess import Popen
from subprocess import PIPE
import download
import rank
import os
import sys
from os import listdir
from os.path import isfile, join


# Create your views here.
def populate_urls(results):
    index = 1
    CHOICES = []
    for result in results:
        CHOICES.append((str(index),mark_safe('<a href="'+result+'"target="_blank">'+result+'</a>')))
        index = index + 1

    fields = {'choice_field':forms.MultipleChoiceField(label=mark_safe("<br /><br /><br />Search Results"),required=False,widget=forms.CheckboxSelectMultiple, choices=tuple(CHOICES))}
    return type('QueryFormWithUrl', (forms.BaseForm,), { 'base_fields': fields })

def populate_score(ranked_urls, scores):
    fields = {}
    urls = ""
    for i in range(0,len(ranked_urls)):
        urls = urls + "<br />"+ranked_urls[i]+" "+str(scores[i])
    fields["ranked_urls"] = forms.CharField(label=mark_safe(urls),required=False) 

    return type('RankedUrls', (forms.BaseForm,), { 'base_fields': fields })
    
def get_query(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        form1 = QueryForm.QueryForm(request.POST)
        # check whether it's valid:
        if form1.is_valid():
            if 'search' in request.POST:
                # Search Bing for the urls related to the query terms
                query_terms = form1.cleaned_data['query_terms']

                os.chdir('/Users/krishnam/Memex/memex/seed_crawler/seeds_generator')
                
                with open('conf/queries.txt','w') as f:
                    f.write(query_terms)
                    
                p=Popen("java -cp .:class:libs/commons-codec-1.9.jar BingSearch -t 10",shell=True,stdout=PIPE)
                output, errors = p.communicate()
                print output
                print errors
                call(["rm", "-rf", "html"])
                call(["mkdir", "-p", "html"])
                dl = download.download("results.txt","html")
                
            # Display search results
            urlspath = '/Users/krishnam/Memex/memex/seed_crawler/seeds_generator/html'
            urls = [ download.decode(f) for f in listdir(urlspath) if isfile(join(urlspath,f)) ]
                
            form_class = populate_urls(urls)

            form2 = form_class(request.POST)
            if form2.is_valid():
                # If relevant pages are selected do the ranking
                if 'select' in request.POST:
                    choices = form2.cleaned_data['choice_field']
                    int_choices = [int(x)-1 for x in choices]
                    print "Positive Examples = ", int_choices

                    os.chdir('/Users/krishnam/Memex/memex/seed_crawler/lda_pipeline')

                    p=Popen("java -cp .:class/:lib/boilerpipe-1.2.0.jar:lib/nekohtml-1.9.13.jar:lib/xerces-2.9.1.jar Extract ../seeds_generator/html/  | python concat_nltk.py data/lda_input.csv",shell=True,stdout=PIPE)
                    output, errors = p.communicate()
                    print output
                    print errors
                    
                    ranker = rank.rank()
                    [ranked_urls,scores] = ranker.results('/Users/krishnam/Memex/memex/seed_crawler/lda_pipeline/data/lda_input.csv',int_choices)
                    form_class = populate_score(ranked_urls, scores)

                    form3 = form_class(request.POST)
                    return render(request, 'query_with_ranks.html', {'form1': form1,'form2':form2, 'form3':form3})

            # redirect to a new URL:
            return render(request, 'query_with_results.html', {'form1': form1,'form2':form2})

    # if a GET (or any other method) we'll create a blank form
    else:
        form1 = QueryForm.QueryForm()
        
    return render(request, 'query.html', {'form1': form1})


    
