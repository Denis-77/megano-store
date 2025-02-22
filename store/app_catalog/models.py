from django.db import models


class CatalogItem(models.Model):
    title = models.CharField(verbose_name='title', max_length=70)
    parent_category = models.ForeignKey(
        'self', on_delete=models.SET(''), blank=True, null=True,
        related_name='catalog_item'
    )

    def __str__(self):
        return self.title[:30]


def image_dir_path(instance, filename):
    return f'images/catalog_items/{filename}'


class Image(models.Model):
    src = models.ImageField('Catalog item image', upload_to=image_dir_path)
    alt = models.CharField(
        verbose_name='alternative text',
        max_length=70,
        default='image'
    )
    catalog_item = models.OneToOneField(
        CatalogItem, on_delete=models.CASCADE,
        blank=True, null=True, related_name='item_image'
    )
