from django import forms
import pickle, os, datetime
from django.conf import settings

datafile = open(os.path.join(settings.PROJECT_ROOT, '..', 'data', 'iso-639.pkl'), 'rb')
isolist = pickle.load(datafile)

LANGS = ((d['bibliographic'], d['name']) for d in isolist)
LANGS = sorted(LANGS, key=lambda lang: lang[1])
TYPES = (
#         ('audio', 'audio'),
         ('image', 'image'),
         ('video','video')
)
    
class DublinCoreForm(forms.Form):
    """
    A form for Dublin Core data.
    """
    
    error_css_class = 'error'
    required_css_class = 'required'
    
    date = forms.DateField(required=False, initial=datetime.date.today)
    title = forms.CharField()
    creator = forms.CharField(required=False, initial='uncredited')
    contributor = forms.CharField(required=False, widget=forms.Textarea(),
                                 help_text='A list of those who contributed to the creation of this piece.')
    description = forms.CharField(required=False, widget=forms.Textarea())
    subject = forms.CharField(required=False, help_text='Subject and keywords.')
    format = forms.CharField(required=False, help_text='The file format, physical medium, or dimensions of the resource.')
    identifier = forms.CharField(required=False)
    language = forms.ChoiceField(choices=LANGS)
    source = forms.CharField(required=False, help_text='ID of source, if derived from another asset.')
    relation = forms.CharField(required=False, help_text='Relation of this asset to the source.')
    publisher = forms.CharField(required=False, help_text='Individual, group, or organization that made this asset available.')
    rights = forms.CharField(required=False, widget=forms.Textarea(),
                             help_text='Rights held in and over the resource, often containing copyright information.')
    type = forms.ChoiceField(choices=TYPES)
    coverage = forms.CharField(required=False, help_text='Geographical reference of location depicted in the asset.')

