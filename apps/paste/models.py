from django.db import models
from datetime import datetime
from random import SystemRandom

IDCHOICES = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
SYSRANDOM = SystemRandom()
IDSTARTCHAR = 'a'
IDPADCHARS = ('x', 'y', 'z')


def generate_random_id(length=4):
    """ Generate a random/unique id for a paste. """
    finalid = [SYSRANDOM.choice(IDCHOICES) for i in range(length)]
    return ''.join(finalid)


def encode_id(realid):
    """ A form of encoding, that is reversible. """
    startchar = ord(IDSTARTCHAR)
    
    finalid = []
    for c in str(realid):
        newchar = chr(startchar + int(c))
        finalid.append(newchar)
    while len(finalid) < 4:
        finalid.append(SYSRANDOM.choice(IDPADCHARS))
    return ''.join(finalid)


def decode_id(idstr):
    """ Decode an id that has been encoded. """
    startchar = ord(IDSTARTCHAR)
    finalid = []
    for c in idstr:
        if c in IDPADCHARS:
            continue
        intstr = str(ord(c) - startchar)
        finalid.append(intstr)
    return int(''.join(finalid))


class wp_paste(models.Model):

    """ A Paste object for the paste app. """

    # author of the paste (possible future development.)
    author = models.CharField('paste author',
                              blank=True,
                              default='',
                              max_length=255,
                              help_text='Author for the paste.')

    # paste content (can't be blank.)
    content = models.TextField('paste content',
                               blank=False,
                               help_text='Content for the paste.')

    # paste title..
    title = models.CharField('paste title',
                             blank=True,
                             default='',
                             max_length=255,
                             help_text='Title for the paste.')

    # language for the paste.
    language = models.CharField('paste language',
                                blank=True,
                                default='',
                                max_length=255,
                                help_text='Language for highlighting.')

    # Human-readable paste id.
    paste_id = models.CharField('paste id',
                                max_length=255,
                                blank=True,
                                help_text='Paste ID for building urls.')

    # publish date (for sort-order mainly)
    publish_date = models.DateTimeField('publish date',
                                        blank=False,
                                        default=datetime.now,
                                        help_text=('Date the paste was '
                                                   'published. '
                                                   '(Set automatically)'))
    
    # disables paste (instead of deleting it, it simply won't be viewed)
    disabled = models.BooleanField(default=False)
    
    # hold on to the paste forever?
    onhold = models.BooleanField(default=False)

    # count of views/downloads
    view_count = models.PositiveIntegerField('view count',
                                             default=0,
                                             help_text=('How many times this '
                                                        'paste has been '
                                                        'viewed.'))
    
    # parent/replyto paste object.
    parent = models.ForeignKey('self',
                               verbose_name='parent of this paste',
                               blank=True,
                               null=True,
                               related_name='children')

    # admin stuff
    date_hierarchy = 'publish_date'
    get_latest_by = 'publish_date'
    
    def __str__(self):
        """ String format for a paste object. """
        if hasattr(self, 'id'):
            _id = self.id
            basestr = '{}: ({})'.format(_id, self.paste_id)
        else:
            basestr = '({})'.format(self.paste_id)
        finalstr = '{} {}'.format(basestr, self.title)
        if len(finalstr) > 80:
            return finalstr[:80]
        return finalstr
    
    def __repr__(self):
        """ same as str() """
        return self.__str__()
    
    # Meta info for the admin site
    class Meta:
        ordering = ['-publish_date']
        verbose_name = 'Paste'
        verbose_name_plural = 'Pastes'
        db_table = 'wp_pastes'

    def save(self, *args, **kwargs):
        """ Generate paste_id before saving. """

        super(wp_paste, self).save(*args, **kwargs)
        # Generate a paste_id for this paste if it doesnt have one already.
        if not self.paste_id:
            self.generate_id()

    def generate_id(self):
        """ Get current paste_id, or generate a new one and saves it. """
        if self.paste_id:
            return self.paste_id

        realid = self.id
        if realid is None:
            # This will call generate_id() again, but make an id to use.
            self.save()

        newid = encode_id(realid)
        self.paste_id = newid
        # Save the newly generated id.
        self.save()

    def get_url(self):
        """ Return absolute url.
            reverse url lookup really needs to be used here.
        """
        return '/paste/?id={}'.format(self.paste_id)

    def reverse_id(self, pasteid=None):
        """ Decode a paste_id, return the actual id.
            If no paste_id is given, it decodes the current pastes id.
        """
        if pasteid is None:
            if not self.paste_id:
                return None
            return decode_id(self.paste_id)
        # Decode pasteid given..
        return decode_id(pasteid)