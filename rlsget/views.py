# coding: utf-8

from django.http import JsonResponse
from django.shortcuts import render

from rlsget import youtube_dl
from rlsget.models import ReleaseDownloadFile


def queue(request):
    return render(request, 'rlsget/queue.html')


def enqueue(request):
    if request.method == 'POST':
        download_file = ReleaseDownloadFile()
        download_file.source = request.POST['url']
        download_file.save()

        youtube_dl.apply_async([download_file.pk])
    return JsonResponse({})


def queue_json(request):
    download_queue = [_.as_dict() for _ in ReleaseDownloadFile.objects.all()]
    return JsonResponse(download_queue, safe=False)
