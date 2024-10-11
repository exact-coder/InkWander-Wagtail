from django.db import models
from django.shortcuts import render
from django import forms
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

# Add these:
from modelcluster.fields import ParentalKey,ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.api import APIField
from wagtail.models import Page,Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel,InlinePanel,MultiFieldPanel

from wagtail.snippets.models import register_snippet

from wagtail.search import index
from wagtail.contrib.routable_page.models import RoutablePageMixin,route

class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )

class BlogTagIndexPage(Page):

    def get_context(self, request):
        # Filter by tag
        tag = request.GET.get('tag')
        blogpages = BlogPage.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['blogpages'] = blogpages
        return context
    
class BlogCategory(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(verbose_name="slug", allow_unicode=True,max_length=255, help_text="A slug to identify posts by this category")

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
register_snippet(BlogCategory)

class BlogIndexPage(RoutablePageMixin,Page):

    template="blog/blog_index_page.html"
    subpage_types =['blog.BlogPage','blog.BlogTagIndexPage']
    # max_count=1
    parent_page_types = ['home.HomePage']

    intro = RichTextField(blank=True)

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        blogpages = self.get_children().live().order_by('-first_published_at')

        paginator = Paginator(blogpages,4)

        page = request.GET.get("page")
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)


        context['blogpages'] = posts
        context["categories"] = BlogCategory.objects.all()
        return context

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    api_fields = [
        APIField('intro'),
    ]
    
    @route(r'^latest/?$',name="latest_posts")
    def latest_blog_posts(self,request, *args, **kwargs):
        context = self.get_context(request, *args,**kwargs)
        context["latest_posts"] = BlogPage.objects.live().public()[:2]

        return render(request, "blog/latest_posts.html",context)
    
    def get_sitemap_urls(self, request=None):
        sitemap =  super().get_sitemap_urls(request)
        sitemap.append({
            "location": self.full_url + self.reverse_subpage("latest_posts"),
            "lastmod": (self.last_published_at or self.latest_revision_created_at or self.latest_blog_posts),
            "priority": 0.9,
        })

        return sitemap


class BlogPage(Page):
    template="blog/Blog_Page.html"
    subpage_types = []
    parent_page_types = ['blog.BlogIndexPage']


    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)
    authors = ParentalManyToManyField('blog.Author', blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    categories = ParentalManyToManyField("blog.BlogCategory", blank=True)

    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('authors', widget=forms.CheckboxSelectMultiple),
            FieldPanel('tags'),
        ], heading="Blog information"),
        MultiFieldPanel(
            [
                FieldPanel("categories", widget=forms.CheckboxSelectMultiple)
            ],
            heading="Categories"
        ),
        FieldPanel('intro'),
        FieldPanel('body'),
        InlinePanel('gallery_images', label="Gallery images"),
    ]

    def save(self, *args,**kwargs):
        key = make_template_fragment_key("blog_post_preview",[self.id])
        cache.delete(key)
        return super().save(*args, **kwargs)

    api_fields = [
        APIField('intro'),
        APIField('body'),
        APIField('authors'),
    ]    


class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]

@register_snippet
class Author(models.Model):
    name = models.CharField(max_length=255)
    author_image = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('author_image'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Authors'

    @property
    def author_name(self):
        return self.name

    api_fields = [
        APIField('name'),
        APIField('author_name'),
    ]

class Subscriber(models.Model):
    email = models.CharField(max_length=100,blank=False,null=False,help_text="Email Address")
    name = models.CharField(max_length=100,blank=False,null=False,help_text="Full Name")

    def __str__(self):
        return self.name
    