from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from utils import helpers

class Itinerary(models.Model):
    """ Itinerary for visiting cases """
    title = models.CharField(max_length=300, blank=False)
    week = models.IntegerField(default=1, validators=[MaxValueValidator(52), MinValueValidator(1)])
    plain_text_itinerary = models.TextField(max_length=4000, blank=True)

    def __str__(self):
        return self.title

   # this is not needed if small_image is created at set_image
    def save(self, *args, **kwargs):
        super(Itinerary, self).save(*args, **kwargs)

        self.items.all().delete()

        if self.plain_text_itinerary.strip():
            for line in self.plain_text_itinerary.split('\n'):
                itinerary_item_data = helpers.get_postal_code(line)
                itinerary_item = ItineraryItem(itinerary=self, case_id='foo', **itinerary_item_data)
                itinerary_item.save()


class ItineraryItem(models.Model):
    """ Single Itinerary """
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, null=False, related_name='items')
    case_id = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=False)
    postal_code_area = models.CharField(max_length=255, null=False)
    postal_code_street = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.address
