from django.shortcuts import render
from . import util
from django import forms
# from django.http import HttpResponseRedirect
# from django.urls import reverse
from random import randint

def check_new(value):
    title = value.lower().strip().replace('  ', ' ')
    if any(title == entry.lower() for entry in util.list_entries()):
        raise forms.ValidationError("Title is not unique!")

class SearchForm(forms.Form):
    query = forms.CharField(label='',
                            widget=forms.TextInput(attrs={
                                'class': 'search', 
                                'placeholder': 'Search Encyclopedia'}))

class TitlePageForm(forms.Form):
    title = forms.CharField(label='',
                            validators=[check_new],
                            widget=forms.TextInput(attrs={
                                'placeholder': 'Enter title'}))

class ContentPageForm(forms.Form):
    content = forms.CharField(label='', 
                              widget=forms.Textarea(attrs={
                                  'placeholder': 'Enter content'}))


def index(request):
    return render(request, 'encyclopedia/index.html', {
        'entries': util.list_entries(),
        'search_form': SearchForm()
    })

def entry(request, title):
    return render(request, 'encyclopedia/entry.html', {
        'title': title,
        'entry': util.get_entry(title),
        'search_form': SearchForm()
    })

def search(request):
    form = SearchForm(request.POST)
    if form.is_valid():
        query = form.cleaned_data['query'].lower().strip().replace('  ', ' ')
        if any(query == entry.lower() for entry in util.list_entries()):
            return entry(request, query)
            # return HttpResponseRedirect(reverse('entry', kwargs={'title': query}))
        else:
            return render(request, 'encyclopedia/search.html', {
                'search_results': filter(lambda s: query in s.lower(), util.list_entries()),
                'query': query,
                'search_form': SearchForm()
            })
    else:
        return index(request)

def random_entry(request):
    entries = util.list_entries()
    title = entries[randint(0, len(entries)-1)]
    return entry(request, title)
    # return HttpResponseRedirect(reverse('entry', kwargs={'title': title}))

def new_page(request):
    if request.method == 'POST':
        title_form = TitlePageForm(request.POST)
        content_form = ContentPageForm(request.POST)

        if title_form.is_valid() and content_form.is_valid():
            title = title_form.cleaned_data['title'].strip().replace('  ', ' ')
            content = content_form.cleaned_data['content']
            util.save_entry(title, '#' + title + '\n\n' + content)
            return entry(request, title)
        else:
            return render(request, 'encyclopedia/new_page.html', {
                'new_title': title_form,
                'new_content': content_form,
                'search_form': SearchForm()
            })
    else:
        return render(request, 'encyclopedia/new_page.html', {
            'new_title': TitlePageForm(),
            'new_content': ContentPageForm(),
            'search_form': SearchForm()
        })

def edit_page(request, title):
    if request.method == 'POST':
        content_form = ContentPageForm(request.POST)

        if content_form.is_valid():
            content = content_form.cleaned_data['content']
            util.save_entry(title, content)
            return entry(request, title)
        else:
            return render(request, 'encyclopedia/edit_page.html', {
                'title': title,
                'content': content_form,
                'search_form': SearchForm()
            })
    else:
        content = util.get_entry(title)
        return render(request, 'encyclopedia/edit_page.html', {
            'title': title,
            'content': ContentPageForm(initial={'content': content}),
            'search_form': SearchForm()
        })