import os

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from app_catalog.models import CatalogItem

DEFAULT_IMAGE_FOR_PRODUCTS = 'images/products/0/empty.jpeg'


class Tag(models.Model):
    name = models.CharField(verbose_name='Tag name', max_length=25)

    def __str__(self):
        return f'{self.name}'


class Specification(models.Model):
    name = models.CharField(verbose_name='Specification name', max_length=40)
    value = models.CharField(verbose_name='value', max_length=50)

    def __str__(self):
        return f'{self.name}: {self.value}'


class Product(models.Model):
    title = models.CharField(verbose_name='title', max_length=70)
    description = models.CharField(verbose_name='description', max_length=255)
    price = models.DecimalField(verbose_name='price', max_digits=10, decimal_places=2)
    count = models.PositiveIntegerField(verbose_name='count')
    date = models.DateTimeField(verbose_name='Date of posting on the site', auto_now_add=True)
    rating = models.DecimalField(verbose_name='rating', max_digits=2, decimal_places=1)
    free_delivery = models.BooleanField(verbose_name='Is Free delivery', default=False)
    tags = models.ManyToManyField(Tag, blank=True)
    specifications = models.ManyToManyField(Specification, blank=True)
    category = models.ForeignKey(CatalogItem, on_delete=models.CASCADE, default=1)
    sold = models.PositiveIntegerField(verbose_name='already sold', default=0)

    def __str__(self):
        return f'{self.title}: {self.price}'


def image_dir_path(instance, filename):
    return f'images/products/{instance.product.id}/{filename}'


class Image(models.Model):
    src = models.ImageField('Product image', upload_to=image_dir_path)
    alt = models.CharField(
        verbose_name='alternative text',
        max_length=70,
        default='image'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_image'
    )


@receiver(post_delete, sender=Image)
def delete_image_file(sender, instance, **kwargs):
    if instance.src and instance.src != DEFAULT_IMAGE_FOR_PRODUCTS:
        image_path = instance.src.path
        if os.path.isfile(image_path):
            os.remove(image_path)

    product = instance.product
    is_more_img = Image.objects.filter(product=product).exists()
    if not is_more_img:
        product.product_image.create(
            src=DEFAULT_IMAGE_FOR_PRODUCTS,
            alt='no images have been added'
        )


@receiver(post_save, sender=Image)
def delete_empty_image(sender, instance, created, **kwargs):
    if created:
        if instance.src != DEFAULT_IMAGE_FOR_PRODUCTS:
            qs = (
                Image.objects
                .filter(product=instance.product)
                .filter(src=DEFAULT_IMAGE_FOR_PRODUCTS)
            )
            if qs.exists():
                qs.first().delete()


@receiver(post_save, sender=Product)
def create_empty_image(sender, instance, created, **kwargs):
    if created:
        Image.objects.create(
            src=DEFAULT_IMAGE_FOR_PRODUCTS,
            alt='Empty',
            product=instance
        )


class Review(models.Model):
    text = models.TextField(verbose_name='Text review')
    rate = models.PositiveSmallIntegerField(
        verbose_name='Rate', validators=[MaxValueValidator(5)]
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name='Last modified', auto_now=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        product_reviews = (
            Review.objects
            .filter(product=self.product)
            .values_list('rate', flat=True)
        )
        rate_count = len(product_reviews)
        sum_rate = sum(product_reviews)
        rating = round(sum_rate / rate_count, 1)
        self.product.rating = rating
        self.product.save()

        return result


class SaleItem(models.Model):
    sale_price = models.DecimalField(
        verbose_name='discounted price', max_digits=10, decimal_places=2
    )
    date_from = models.DateField(verbose_name='date from')
    date_to = models.DateField(verbose_name='date to')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_sale'
    )
