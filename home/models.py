from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField
from modelcluster.fields import ParentalKey
from wagtail.models import Orderable

# import MultiFieldPanel:
from wagtail.admin.panels import FieldPanel, MultiFieldPanel,InlinePanel,ObjectList,TabbedInterface

class HomePageCarousels(Orderable):
    page = ParentalKey("home.HomePage", related_name="home_page_carousels")
    carousel_image = models.ForeignKey("wagtailimages.Image",null=True,blank=False,on_delete=models.SET_NULL, related_name="+")
    carousel_title = models.CharField(null=True,blank=False,max_length=200,help_text="Carousel Title *")
    carousel_subtitle = models.CharField(null=True,blank=False,max_length=200,help_text="Carousel Subtitle")
    carousel_cta = models.CharField(blank=True,null=True,verbose_name="Carousel CTA",max_length=255,help_text="Text to display on Call to Action",)
    carousel_cta_link = models.ForeignKey("wagtailcore.Page",null=True,blank=True,on_delete=models.SET_NULL,help_text="Choose a page to link to for the Call to Action")
    carousel_cta_url = models.URLField(verbose_name="Carousel URL", blank=True,help_text="If carousel_cta_link not found. Then this url work")

    panels = [
        FieldPanel("carousel_image"),
        FieldPanel("carousel_title"),
        FieldPanel("carousel_subtitle"),
        FieldPanel("carousel_cta"),
        FieldPanel("carousel_cta_link"),
        FieldPanel("carousel_cta_url"),
    ]


class HomePage(Page):

    template = "home/home_page.html"
    subpage_types = ['home.HomePage','blog.BlogIndexPage','portfolio.PortfolioPage','base.FormPage']
    # max_count=1


    # add the Hero section of HomePage:
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Homepage image",
    )
    hero_text = models.CharField(
        blank=True,
        max_length=255, help_text="Write an introduction for the site"
    )
    hero_cta = models.CharField(
        blank=True,
        verbose_name="Hero CTA",
        max_length=255,
        help_text="Text to display on Call to Action",
    )
    hero_cta_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Hero CTA link",
        help_text="Choose a page to link to for the Call to Action",
    )

    body = RichTextField(blank=True)

    # modify your content_panels:
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                InlinePanel("home_page_carousels",max_num=5,min_num=1,label="Carousel"),
            ],
            heading="Home Page Carousel section",
        ),
        MultiFieldPanel(
            [
                FieldPanel('body'),
            ],
            heading="Body section"
        ),
        
    ]
    # promote_panels = []
    # settings_panel = []

    hero_panels = [
        MultiFieldPanel(
            [
                FieldPanel("image"),
                FieldPanel("hero_text"),
                FieldPanel("hero_cta"),
                FieldPanel("hero_cta_link"),
            ],
            heading="Hero section",
        ),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels,heading="Editable Content"),
        ObjectList(Page.promote_panels,heading="Promotional Staff"),
        ObjectList(Page.settings_panels,heading="Settings Staff"),
        ObjectList(hero_panels,heading="Hero Settings"),
    ])