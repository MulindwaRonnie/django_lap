from django.conf import settings # import the projects settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
#from django.db.models.functions import Now # In case we want to use database default values instead of timezone

class PublishedManager(models.Manager):
    def get_queryset(self):
        return (
            super().get_queryset().filter(status=Post.Status.PUBLISHED)
        )

class Post(models.Model):
    class Status(models.TextChoices): # this class tells whether the post is published or a draft, this is an enumeration class.
        DRAFT = 'DF', 'Draft' # this follows the format 'choice e.g DF', "human-readable format e.g Draft"
        PUBLISHED = 'PB', 'Published'
    
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish') # this ensures that the same slug and publish date are not stored for many posts
    author = models.ForeignKey(     #foreign key is used to relate our post model with the default user model, thus creating a user account
        settings.AUTH_USER_MODEL, # a user can write any number of posts
        on_delete=models.CASCADE, # if a user is deleted, all related posts are also deleted
        related_name='blog_posts' # this is the reverse relationship from user to posts i.e user.blog_posts accesses the user's posts
    )
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now) # same as: publish = models.DateTimeField(db_default=Now())
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(  #an instance of the status class defined above
        max_length=2,
        choices=Status,
        default=Status.DRAFT
    )
    objects = models.Manager() # the default manager
    published = PublishedManager() # Our custom manager

    class Meta: # define our own ordering for the posts
        ordering = ['-publish'] # order depends on the publish field and its in reverse chronological order
        indexes = [
            models.Index(fields=['-publish']),
        ] # please take note that this index ordering is not supported for MySQL

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'blog:post_detail',
            args=[
                self.publish.year,
                self.publish.month,
                self.publish.day,
                self.slug
        ]
    )
        
class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'

          
    
