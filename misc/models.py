from django.db import models
from misc.types import MiscTypes, Lang
from datetime import date

# Module level functions...


def get_date_today():
    """ returns today's date for setting default publish_date value """
        
    return date.today()


class wp_misc(models.Model):

    """ Model for a misc object, 
        small snippets of code, small scripts, text, etc. """
    # Proper Name for this object (must be unique because .get(name=) is used
    name = models.CharField(blank=False, max_length=250,
                            help_text=('Name for this misc object '
                                       '(must be unique)'))
    
    # Alias for this object (usually name.lower().replace(' ', ''), used for building urls)
    # Prepopulated using Django admin in the fashion described above.
    alias = models.CharField(blank=False, max_length=250,
                             help_text=('Alias for this misc object '
                                        '(used for building urls)'))
    
    # short description of misc object
    # (longer description should be in it's htmlcontent/content)
    description = models.CharField(blank=True, default='', max_length=1024,
                                   help_text=('Short description for the '
                                              'misc object.'))
    
    # version in the form of X.X.X or XX.XX.XX
    version = models.CharField(blank=True, default='1.0.0', max_length=8,
                               help_text='Version string in the form of X.X.X')

    # filename for this misc object.
    # used for viewing/downloading
    filename = models.CharField(blank=True, default='', max_length=512,
                                help_text=('Main source file for the misc '
                                           'object for viewing/downloading.'))
    
    # Html content (for long description of this misc object)
    # If no Html file is present, then contents is used.
    contentfile = models.CharField(blank=True, default='', max_length=512,
                                   help_text=('Html file for this misc '
                                              'object, used for long '
                                              'description.'))
    
    # Content (for long description of this misc object)
    content = models.TextField(blank=True, default='',
                               help_text=('Content for this misc object '
                                          '(long description) if contentfile '
                                          'is not used.'))
    
    # misc type (code file, snippet, text, script, archive, executable, etc.)
    filetype = models.CharField(blank=False,
                                default='None',
                                max_length=100,
                                choices=MiscTypes.fieldchoices,
                                help_text=('Type of misc object (snippet, '
                                           'code, archive, text, etc.)'))
    
    # language type for this misc object (can be None, Python, Python2, Python3, Bash, C, etc.)
    language = models.CharField(blank=False,
                                default='None',
                                max_length=100,
                                choices=Lang.fieldchoices,
                                help_text=('Code language for this misc '
                                           'object (None, Python, C, Bash, '
                                           'etc.)'))
    
    # disables project (instead of deleting it, it simply won't be viewed)
    disabled = models.BooleanField(default=False)
    
    # count of views/downloads
    view_count = models.IntegerField(default=0,
                                     help_text=('How many times this misc '
                                                'object has been viewed. '
                                                '(Integer)'))
    download_count = models.IntegerField(default=0,
                                         help_text=('How many times this '
                                                    'misc object has been '
                                                    'downloaded. (Integer)'))

    # publish date (for sort-order mainly)
    publish_date = models.DateField(blank=False, default=get_date_today(),
                                    help_text=('Date the misc object was '
                                               'published. (Automatically set '
                                               'to today.)'))

    # admin stuff
    date_hierarchy = 'publish_date'
    get_latest_by = 'publish_date'
    
    def __unicode__(self):
        """ returns string/unicode representation of project """
        s = self.name
        if self.version:
            s = s + " v. " + self.version
        return s

    def __str__(self):
        """ same as unicode() except str() """
        return str(self.__unicode__())
    
    def __repr__(self):
        """ same as unicode() """
        return self.__unicode__()
    
    # Meta info for the admin site
    class Meta:
        ordering = ['name']
        verbose_name = "Misc. Object"
        verbose_name_plural = "Misc. Objects"
