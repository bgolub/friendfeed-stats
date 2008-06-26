import datetime
from friendfeedapp.models import FFUser, Service, Entry

def get_friendfeed_friends(nickname):
    from django.http import Http404
    from django.core.cache import cache
    key = 'friendfeed_friends_%s' % nickname
    friends = cache.get(key)
    if not friends:
        friends = []
        import friendfeed
        ff = friendfeed.FriendFeed()
        try:
            friends = ff.fetch_user_profile(nickname)['subscriptions']
        except:
            raise Http404
        friends = [friend['nickname'] for friend in friends]
        cache.set(key, friends, 60*60*24)
    return friends

def get_or_create_from_entry(entry):
    defaults = {
        'nickname': entry['user']['nickname'], 
        'name': entry['user']['name']
    }
    ffuser, ffuser_created = FFUser.objects.get_or_create(uuid = entry['user']['id'], defaults = defaults)

    defaults = {
        'name': entry['service']['name']
    }
    service, service_created = Service.objects.get_or_create(uuid = entry['service']['id'], defaults = defaults)

    defaults = {
        'ffuser': ffuser,
        'service': service,
        'date': entry['published'],
        'hour': entry['published'].hour,
        'day': entry['published'].day,
        'month': entry['published'].month,
        'year': entry['published'].year,
        'weekday': entry['published'].weekday(),
    }

    entry, entry_created = Entry.objects.get_or_create(uuid = entry['id'], defaults = defaults)

    return ffuser, ffuser_created, service, service_created, entry, entry_created

def get_graph_data(type = 'weekdays', duration = datetime.timedelta(days = 30), ffuser = None, service = None, friends = None):
    data = []
    total = 0
    now = datetime.datetime.utcnow()
    end = now
    start = end - duration
    types = ('hours', 'weekdays', 'months', 'services', 'days')
    if not type in types:
        type = 'weekdays'
    queryset = Entry.objects
    if not type == 'days':
        queryset = queryset.filter(date__lte = end, date__gte = start)
    if ffuser and not friends:
        queryset = queryset.filter(ffuser = ffuser)
    if service:
        queryset = queryset.filter(service = service)
    if friends:
        queryset = queryset.filter(ffuser__nickname__in = friends)
    if type == 'hours':
        labels = '12am 1am 2am 3am 4am 5am 6am 7am 8am 9am 10am 11am 12pm 1pm 2pm 3pm 4pm 5pm 6pm 7pm 8pm 9pm 10pm 11pm'
        for hour, label in enumerate(labels.split()):
            count = queryset.filter(hour = hour).count()
            total += count
            data.append({
                'label': label,
                'count': count,
            })
    elif type == 'weekdays':
        labels = 'Monday Tuesday Wednesday Thursday Friday Saturday Sunday'
        for weekday, label in enumerate(labels.split()):
            count = queryset.filter(weekday = weekday).count()
            total += count
            data.append({
                'label': label,
                'count': count,
            })
    elif type == 'months':
        labels = 'January February March April May June July August September October November December'
        for month, label in enumerate(labels.split()):
            count = queryset.filter(month = month + 1).count()
            total += count
            data.append({
                'label': label,
                'count': count,
            })
    elif type == 'services':
        for service in Service.objects.order_by('name'):
            count = queryset.filter(service = service).count()
            total += count
            data.append({
                'label': service.name,
                'count': count,
            })
    elif type == 'days':
        from django.template.defaultfilters import timesince
        for day in range(1, duration.days):
            start = end - datetime.timedelta(days = 1)
            count = queryset.filter(date__lte = end, date__gte = start).count()
            total += count
            data.append({
                'label': '%s ago' % timesince(now, start),
                'count': count,
            })
            end = start
    return data, total
