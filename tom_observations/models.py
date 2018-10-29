from django.db import models
from io import BytesIO
from base64 import b64encode
import json
from django.conf import settings

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import figure
from astropy.io import fits

from tom_targets.models import Target
from tom_observations.facility import get_service_class


class ObservationRecord(models.Model):
    target = models.ForeignKey(Target, on_delete=models.CASCADE)
    facility = models.CharField(max_length=50)
    parameters = models.TextField()
    observation_id = models.CharField(max_length=2000)
    status = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created',)

    @property
    def parameters_as_dict(self):
        return json.loads(self.parameters)

    @property
    def url(self):
        facility = get_service_class(self.facility)
        return facility.get_observation_url(self.observation_id)

    def __str__(self):
        return '{0} @ {1}'.format(self.target, self.facility)


def data_product_path(instance, filename):
    # Uploads go to MEDIA_ROOT
    if instance.observation_record:
        return '{0}/{1}/{2}'.format(instance.target.identifier, instance.observation_record.facility, filename)
    else:
        return '{0}/none/{1}'.format(instance.target.identifier, filename)


class DataProductGroup(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.name


class DataProduct(models.Model):
    product_id = models.CharField(max_length=2000, unique=True, null=True)
    target = models.ForeignKey(Target, on_delete=models.CASCADE)
    observation_record = models.ForeignKey(ObservationRecord, null=True, default=None, on_delete=models.CASCADE)
    data = models.FileField(upload_to=data_product_path, null=True, default=None)
    extra_data = models.TextField(blank=True, default='')
    group = models.ManyToManyField(DataProductGroup)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    tag = models.TextField(blank=True, default='')

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.data.name

    def get_png_data(self):
        path = settings.MEDIA_ROOT + '/' + str(self.data)
        image_data = fits.getdata(path, 0)
        fig = plt.figure()
        plt.imshow(image_data)
        plt.axis('off')
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close(fig)
        return b64encode(buffer.read()).decode('utf-8')