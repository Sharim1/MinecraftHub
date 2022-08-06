from django.db import models
from tinymce.models import HTMLField
from django.urls import reverse


STATUS = ((0, "Draft"), (1, "Publish"))

class Category(models.Model):
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    title = models.CharField(max_length=20)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.title.lower() in ['worlds','world']:
            self.title = 'Worlds'
        if self.title.lower() in ['mods','mod']:
            self.title = 'Mod'
        super(Category, self).save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
    reply = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return "Comment {} by {}".format(self.body, self.name)

class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = HTMLField()
    youtube_link = models.CharField(max_length=100, blank=True)
    upload_file = models.FileField(upload_to="files", blank=True)
    thumbnail = models.ImageField()
    Category = models.ManyToManyField(Category)
    status = models.IntegerField(choices=STATUS, default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_details', kwargs={
            'slug': str(self.slug)
        })

    @property
    def comment_count(self):
        return Comment.objects.filter(post=self).count()

MAX_OBJECTS = 1

class EarlyAccess(models.Model):
    class Meta:
        verbose_name = "Early Access"
        verbose_name_plural = "Early Access"

    heading = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    youtube_link = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.heading

