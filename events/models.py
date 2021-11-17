from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.
from django.urls import reverse


class Event(models.Model):
    STATUS_CHOICE = (
        ('F', 'Свободен'),
        ('B', 'Занят'),
    )
    title = models.CharField(max_length=300, verbose_name='Title', null=True, blank=True)

    day = models.DateField('Day of the event', help_text='Day of the event')
    start_time = models.TimeField('Starting time', help_text='Starting time')
    end_time = models.TimeField('Final time', help_text='Final time')
    notes = models.TextField('Textual Notes', help_text='Textual Notes', blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(null=True, max_length=300, verbose_name='Status', choices=STATUS_CHOICE,
                              help_text='Choice status')  # свободен/занят

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Scheduling'
        verbose_name_plural = 'Scheduling'

    def check_overlap(self, fixed_start, fixed_end, new_start, new_end):
        overlap = False
        if new_start == fixed_end or new_end == fixed_start:  # edge case
            overlap = False
        elif (fixed_start <= new_start <= fixed_end) or (
                fixed_start <= new_end <= fixed_end):  # innner limits
            overlap = True
        elif new_start <= fixed_start and new_end >= fixed_end:  # outter limits
            overlap = True

        return overlap

    def get_absolute_url(self):
        url = reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args=[self.id])
        return u'<a href="%s">%s</a>' % (url, str(self.start_time))

    def clean(self):
        print(self.end_time, self.start_time)
        if self.end_time <= self.start_time:
            raise ValidationError('Ending times must after starting times')

        events = Event.objects.filter(day=self.day)
        if events.exists():
            for event in events:
                if self.check_overlap(event.start_time, event.end_time, self.start_time, self.end_time):
                    raise ValidationError(
                        'There is an overlap with another event: ' + str(event.day) + ', ' + str(
                            event.start_time) + '-' + str(event.end_time))
