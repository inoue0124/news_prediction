from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.http.response import HttpResponse
from naive_bayes.forms import UrlForm
from naive_bayes.modules.PredictCategory import PredictCategory

def index_page(request):
    form = UrlForm()
    return render(request, 'index.html', {
        'form': form,
    })


def result_page(request):
    url = request.POST['url']
    predictor = PredictCategory(url)
    estimation = predictor.classify(predictor.keywords)
    return render(request, 'result.html', {
        'url':url,
        'estimation': predictor.categories[estimation],
    })

