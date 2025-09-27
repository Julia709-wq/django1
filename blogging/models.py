from django.db import models


class BlogPost(models.Model):
    header = models.CharField(max_length=255, verbose_name='Заголовок')
    content = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='photos/')
    created_at = models.DateField(auto_now_add=True)
    tag = models.BooleanField(null=True, blank=True, default=True)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.header

    class Meta:
        verbose_name = 'запись'
        verbose_name_plural = 'записи'
        ordering = ['header', ]


