from django.core.cache import cache
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from friendfeedapp.models import FFUser, Service
from friendfeedapp.utils import get_graph_data

CACHE_TIME = 60 * 60

def request_to_graph_data(request, ffuser = None, friends = None):
    key = '%s' % (request.get_full_path())
    results = cache.get(key)
    if not results:
        from datetime import timedelta
        service = None
        if 'service' in request.GET:
            service = get_object_or_404(Service, uuid = request.GET['service'])
        type = request.GET.get('type', 'weekdays')
        if type == 'months':
            duration = timedelta(days = 365)
        elif type == 'days':
            duration = timedelta(days = 14)
        else:
            duration = timedelta(days = 30)
        if 'duration' in request.GET:
            try:
                duration = timedelta(days = int(request.GET['duration']))
            except Exception, e:
                pass
        data, total = get_graph_data(type = type, duration = duration, ffuser = ffuser, service = service, friends = friends)
        results = data, total, duration
        cache.set(key, results, CACHE_TIME)
    return results

def get_services():
    key = 'services'
    services = cache.get(key)
    if not services:
        services = Service.objects.order_by('name')
        cache.set(key, list(services), CACHE_TIME)
    return services

def graph(request, nickname, friends_only = False):
    ffuser = get_object_or_404(FFUser, nickname = nickname)
    friends = None
    if friends_only:
        from friendfeedapp.utils import get_friendfeed_friends
        friends = get_friendfeed_friends(nickname)
    data, total, duration = request_to_graph_data(request, ffuser, friends)
    services = get_services()
    extra_context = {'data': data, 'total': total, 'services': services, 'ffuser': ffuser, 'duration': duration.days}
    if friends:
        template = 'friendfeedapp/friends.html'
    else:
        template = 'friendfeedapp/user.html'
    return render_to_response(template, extra_context, context_instance = RequestContext(request))

def search(request):
    if request.method == 'POST' and 'nickname' in request.POST:
        try:
            ffuser = FFUser.objects.get(nickname = request.POST['nickname'].lower())
        except FFUser.DoesNotExist:
            try:
                ffuser = FFUser.objects.get(name__iexact = request.POST['nickname'])
            except FFUser.DoesNotExist:
                raise Http404
            except FFUser.MultipleObjectsReturned:
                raise Http404
        return HttpResponseRedirect(ffuser.get_absolute_url())
    else:
        raise Http404
