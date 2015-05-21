from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
from django.utils.safestring import mark_safe
import QueryForm
from django import forms
from django.core import serializers

import seed_crawler_model 

from subprocess import call
from subprocess import Popen
from subprocess import PIPE
import download
import rank
import extract_terms
import sys
import shutil
from collections import OrderedDict
import operator
from os import listdir, chdir, environ, getcwd
from os.path import isfile, join, exists

from concat_nltk import get_bag_of_words
from search_documents import get_image

from django.core.files.uploadedfile import SimpleUploadedFile

def encode( url):
  return url.replace("/", "_")

def get_downloaded_urls(inputfile):
  urls = []
  with open(inputfile, 'r') as f:
    urls = f.readlines()
  urls = [url.strip() for url in urls]
  return urls

def populate_urls(request, urls=[]):
    fields = [] 
    file_data = []
    CHOICES = ((1,'Yes'),(2,'No'))
    if len(urls) > 0:
        # Display search results
        index = 0
        for url in urls:
            [image_name, img] = get_image(url)
            if not (image_name == None):
              with open(environ['DDT_HOME']+"/seed_crawler/seed_crawler_site/web_search/static/web_search/"+image_name,'wb') as f:
                f.write(img)
              fields.append(['thumbnail_'+str(index),forms.CharField(label=image_name.encode('utf-8'))])
              request.session['thumbnail_'+str(index)] = image_name                
            fields.append(['choice_urls_field_'+str(index), forms.TypedChoiceField(label=mark_safe('<a href="'+url+'"target="_blank">'+url+'</a>'),required=False,widget=forms.RadioSelect(), choices=CHOICES,coerce=int)])
            request.session['choice_urls_field_'+str(index)] = url
            index = index + 1
    else:
        index = 0
        while True:
          key_url = 'choice_urls_field_'+str(index)
          url = request.session.get(key_url,None)
          key_img = 'thumbnail_'+str(index)
          image_name = request.session.get(key_img,None)

          if url is not None:
            if not (image_name == None):
              fields.append([key_img,forms.CharField(label=image_name.encode('utf-8'))])
            fields.append([key_url, forms.TypedChoiceField(label=mark_safe('<a href="'+ url +'"target="_blank">'+url+'</a>'),required=False,widget=forms.RadioSelect(), choices=CHOICES,coerce=int)])
            index = index + 1
          else:
            break
                
    ordered_fields = OrderedDict(fields)

    return type('QueryFormWithUrl', (forms.BaseForm,), { 'base_fields': ordered_fields })

def populate_freq_terms(request, terms):
    CHOICES = ((1,'Yes'),(2,'No'))
    fields = {}
    if len(terms) > 0:
        index = 0
        for term in terms:
          if term:
            fields['choice_freq_terms_field'+str(index)] = forms.TypedChoiceField(label=mark_safe(term.title()),required=False,widget=forms.RadioSelect(), choices=CHOICES,coerce=int)
            request.session['choice_freq_terms_field'+str(index)] = term.title()
            index = index + 1
    else:
        for key in request.session.keys():
            if 'choice_freq_terms_field' in key:
                fields[key] = forms.TypedChoiceField(label=mark_safe(request.session[key]),required=False,widget=forms.RadioSelect(), choices=CHOICES,coerce=int)
    fields = OrderedDict(sorted(fields.items(), key=operator.itemgetter(0)))

    return type('QueryFormWithTerms', (forms.BaseForm,), { 'base_fields': fields })

def populate_ranked_terms(request,terms):
    CHOICES = ((1,'Yes'),(2,'No'))
    fields = {}
    if len(terms) > 0:
        index = 0
        for term in terms:
            fields['choice_ranked_terms_field'+str(index)] = forms.TypedChoiceField(label=mark_safe(term.title()),required=False,widget=forms.RadioSelect(), choices=CHOICES,coerce=int)
            request.session['choice_ranked_terms_field'+str(index)] = term.title()
            index = index + 1
    else:
        for key in request.session.keys():
            if 'choice_ranked_terms_field' in key:
                fields[key] = forms.TypedChoiceField(label=mark_safe(request.session[key]),required=False,widget=forms.RadioSelect(), choices=CHOICES,coerce=int)

    fields = OrderedDict(sorted(fields.items(), key=operator.itemgetter(0)))
    return type('QueryFormWithRankedTerms', (forms.BaseForm,), { 'base_fields': fields })

def add_to_search_freq(request):
    form_class = populate_freq_terms(request, [])
    form4 = form_class(request.POST)   
    int_yes_choices = []
    if form4.is_valid():
        for field in form4.cleaned_data:
            if "choice_freq_terms_field" in field:
                if form4.cleaned_data[field] == 1:
                    int_yes_choices.append(form4[field].label.lower().strip())
        
    return int_yes_choices

def add_to_search_rank(request):
    form_class = populate_ranked_terms(request, [])
    form5 = form_class(request.POST)   
    int_yes_choices = []
    if form5.is_valid():
        for field in form5.cleaned_data:
            if "choice_ranked_terms_field" in field:
                if form5.cleaned_data[field] == 1:
                    int_yes_choices.append(form5[field].label.lower().strip())
        
    return int_yes_choices
                
def populate_score(ranked_urls, scores):
    fields = {}
    urls = ""
    for i in range(0,len(ranked_urls)):
        urls = urls + "<br />"+ranked_urls[i]+" "+str(scores[i])
    fields["ranked_urls"] = forms.CharField(label=mark_safe(urls),required=False) 

    return type('RankedUrls', (forms.BaseForm,), { 'base_fields': fields })

def copy_files(int_yes_choices,int_no_choices):
    urlspath = '/Users/krishnam/Memex/memex/seed_crawler/seeds_generator/html/'
    classifier_data_positive_path = '/Users/krishnam/Memex/memex/pageclassifier/conf/sample_training_data/positive'
    classifier_data_negative_path = '/Users/krishnam/Memex/memex/pageclassifier/conf/sample_training_data/negative'
    files = [ f for f in listdir(urlspath) if isfile(join(urlspath,f))]
    [ shutil.copy(urlspath+files[index], classifier_data_positive_path) for index in int_yes_choices ]
    [ shutil.copy(urlspath+files[index], classifier_data_negative_path) for index in int_no_choices ]
        
    
def get_query(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form1 = QueryForm.QueryForm(request.POST)
        if 'search' in request.POST:
            # create a form instance and populate it with data from the request:
            # check whether it's valid:
            if form1.is_valid():
                # Search Bing for the urls related to the query terms
                query_terms = [form1.cleaned_data['query_terms']]
                
                scm = seed_crawler_model.SeedCrawlerModel()

                results = list(scm.submit_query_terms(query_terms, max_url_count = 20, cached=False))
                
                form_class = populate_urls(request, results[0:15])
                form2 = form_class()

                return render(request, 'query_with_results.html', {'form1': form1,'form2':form2})

        form_class = populate_urls(request)
        form2 = form_class(request.POST)
        url_yes_choices = []
        url_no_choices = []
        if form2.is_valid():
            # If relevant pages are selected do the ranking
            for field in form2.cleaned_data:
              if "choice_urls_field_" in field:
                if form2.cleaned_data[field] == 1:
                  url_yes_choices.append(request.session[field].encode('ascii','ignore'))
                elif form2.cleaned_data[field] == 2:
                  url_no_choices.append(request.session[field].encode('ascii','ignore'))
        else:
          for field in form2.cleaned_data:
            if "choice_urls_field_" in field:
              if form2.cleaned_data[field] == 1:
                url_yes_choices.append(request.session[field].encode('ascii','ignore'))
              elif form2.cleaned_data[field] == 2:
                url_no_choices.append(request.session[field].encode('ascii','ignore'))
            
        if 'rank' in request.POST:
                        
            #copy_files(int_url_yes_choices,int_url_no_choices)
            
            results = get_downloaded_urls(environ['DDT_HOME']+'/seed_crawler/seeds_generator/results.txt')
            scm = seed_crawler_model.SeedCrawlerModel(results)
            [ranked_urls, scores] = scm.submit_selected_urls(url_yes_choices, url_no_choices)
            for i in range(0,len(ranked_urls)):
              print ranked_urls[i], " ", scores[i]
            #form_class = populate_score(ranked_urls[0:15], scores[0:15])
            #form3 = form_class()
            #return render(request, 'query_with_ranks.html', {'form1': form1,'form2':form2, 'form3':form3})
            form_class = populate_urls(request, ranked_urls[0:15])
            form2 = form_class()
            return render(request, 'query_with_results.html', {'form1': form1,'form2':form2})

        elif 'extract' in request.POST:
            chdir(environ['DDT_HOME']+'/seed_crawler/ranking')
            if exists("selected_terms.txt"):
                call(["rm", "selected_terms.txt"])
            if exists("exclude.txt"):
                call(["rm", "exclude.txt"])
                
            results = get_downloaded_urls(environ['DDT_HOME']+'/seed_crawler/seeds_generator/results.txt')
            scm = seed_crawler_model.SeedCrawlerModel(results)
            [ranked_urls, scores] = scm.submit_selected_urls(url_yes_choices, url_no_choices)
            terms = scm.extract_terms(20)
            form_class = populate_freq_terms(request,terms)
            form4 = form_class()
            return render(request, 'query_with_terms.html', {'form1': form1,'form2':form2, 'form4':form4})
                
        elif ('rank_terms' in request.POST):
            form_class = populate_freq_terms(request,[])
            form4 = form_class(request.POST)
            if form4.is_valid():
                int_yes_choices = []
                int_no_choices = []
                for field in form4.cleaned_data:
                    if "choice_freq_terms_field" in field:
                        if form4.cleaned_data[field] == 1:
                            #int_yes_choices.append(int(field.replace("choice_freq_terms_field","")))
                            int_yes_choices.append(form4[field].label.lower().strip())
                        elif form4.cleaned_data[field] == 2:
                            #int_no_choices.append(int(field.replace("choice_freq_terms_field","")))
                            int_no_choices.append(form4[field].label.lower().strip())
                            
                chdir(environ['DDT_HOME']+'/seed_crawler/ranking')
                with open('exclude.txt','w+') as f:
                    for choice in int_no_choices :
                        f.write(choice+'\n')

                results = get_downloaded_urls(environ['DDT_HOME']+'/seed_crawler/seeds_generator/results.txt')
                scm = seed_crawler_model.SeedCrawlerModel(results)
                scm.submit_selected_urls(url_yes_choices, url_no_choices)
                ranked_terms = scm.submit_selected_terms(int_yes_choices, int_no_choices)
                form_class = populate_ranked_terms(request, ranked_terms[0:20])
                form5 = form_class()

                with open('selected_terms.txt','w+') as f:
                    for choice in int_yes_choices :
                        f.write(choice+'\n')

                return render(request, 'query_with_term_rank.html', {'form1': form1,'form2':form2, 'form4':form4, 'form5':form5})
                
        elif 'rank_terms_1' in request.POST:
            form_class = populate_freq_terms(request,[])
            form4 = form_class(request.POST)

            form_class = populate_ranked_terms(request,[])
            form5 = form_class(request.POST)
            if form5.is_valid():
                int_yes_choices = []
                int_no_choices = []
                
                for field in form5.cleaned_data:
                    if "choice_ranked_terms_field" in field:
                        if form5.cleaned_data[field] == 1:
                            #int_yes_choices.append(int(field.replace("choice_ranked_terms_field","")))
                            int_yes_choices.append(form5[field].label.lower().strip())
                        elif form5.cleaned_data[field] == 2:
                            #int_no_choices.append(int(field.replace("choice_ranked_terms_field","")))
                            int_no_choices.append(form5[field].label.lower().strip())

                chdir(environ['DDT_HOME']+'/seed_crawler/ranking')
                results = get_downloaded_urls(environ['DDT_HOME']+'/seed_crawler/seeds_generator/results.txt')
                scm = seed_crawler_model.SeedCrawlerModel(results)
                scm.submit_selected_urls(url_yes_choices, url_no_choices)
                ranked_terms = scm.submit_selected_terms(int_yes_choices, int_no_choices)
                form_class = populate_ranked_terms(request, ranked_terms[0:20])
                form5 = form_class(request.POST)                

                return render(request, 'query_with_term_rank.html', {'form1': form1,'form2':form2, 'form4':form4, 'form5':form5})

        elif 'add_to_search_freq' in request.POST:
            form_class = populate_freq_terms(request,[])
            form4 = form_class(request.POST)

            results = add_to_search_freq(request)
            form1 = QueryForm.QueryForm(request.POST)
            if form1.is_valid():
                query_terms = form1.cleaned_data['query_terms']
                for word in results:
                    query_terms = query_terms + " " + word;
                form1 = QueryForm.QueryForm(initial={'query_terms':query_terms})
                return render(request, 'query_with_terms.html', {'form1': form1,'form2':form2, 'form4':form4})

        elif 'add_to_search_rank' in request.POST:
            form_class = populate_freq_terms(request,[])
            form4 = form_class(request.POST)
            form_class = populate_ranked_terms(request, [])
            form5 = form_class(request.POST)                

            results = add_to_search_rank(request)
            form1 = QueryForm.QueryForm(request.POST)
            if form1.is_valid():
                query_terms = form1.cleaned_data['query_terms']
                for word in results:
                    query_terms = query_terms + " " + word;
                form1 = QueryForm.QueryForm(initial={'query_terms':query_terms})
                return render(request, 'query_with_term_rank.html', {'form1': form1,'form2':form2, 'form4':form4, 'form5':form5})

    # if a GET (or any other method) we'll create a blank form
    else:
        form1 = QueryForm.QueryForm()
        
    return render(request, 'query.html', {'form1': form1})


    
