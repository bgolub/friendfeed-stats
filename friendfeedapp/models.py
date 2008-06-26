import datetime
from django.db import models

class FFUser(models.Model):
    uuid = models.CharField(unique = True, max_length = 255)
    nickname = models.CharField(unique = True, max_length = 255)
    name = models.CharField(max_length = 255)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '/%s/' % self.nickname

    def update(self, verbose = False):
        import friendfeed
        from friendfeedapp.utils import get_or_create_from_entry
        service = friendfeed.FriendFeed()
        try:
            for entry in service.fetch_user_feed(self.nickname)['entries']:
                results = get_or_create_from_entry(entry)
                if verbose:
                    print results
        except Exception, e:
            pass

    class Admin:
        list_display = ('uuid', 'nickname', 'name')
        search_fields = ['nickname',]

class Service(models.Model):
    uuid = models.CharField(unique = True, max_length = 255)
    name = models.CharField(max_length = 255)

    def __unicode__(self):
        return self.name

    def get_image_url(self):
        return 'http://friendfeed.com/static/images/icons/%s.png' % self.uuid

    class Admin:
        list_display = ('uuid', 'name')

class Entry(models.Model):
    ffuser = models.ForeignKey(FFUser)
    service = models.ForeignKey(Service)

    uuid = models.CharField(unique = True, max_length = 255)

    date = models.DateTimeField(default = datetime.datetime.now)
    hour = models.IntegerField(default = 0)
    day = models.IntegerField(default = 0)
    month = models.IntegerField(default = 0)
    year = models.IntegerField(default = 0)
    weekday = models.IntegerField(default = 0)

    def __unicode__(self):
        return self.uuid

    class Admin:
        list_display = ('ffuser', 'service', 'uuid', 'date')
        list_filter = ('service',)
        search_fields = ['title',] 
