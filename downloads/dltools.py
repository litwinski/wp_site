#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
      project: Welborn Productions - Downloads - Tools
     @summary: Various tools for the downloads app, such as file tracking.
    
      @author: Christopher Welborn <cj@welbornprod.com>
@organization: welborn productions <welbornprod.com>
 
   start date: May 25, 2013
'''

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from downloads.models import file_tracker
from wp_main.utilities.wp_logging import logger
_log = logger("downloads.tools").log


def get_file_tracker(absolute_path, createtracker=True, dosave=False):
    """ gets an existing file_tracker, or creates a new one from a filename """
    try:
        filetracker = file_tracker.objects.get(filename=absolute_path)
    except MultipleObjectsReturned:
        _log.error('File tracker has multiple objects!: '
                   '{}'.format(absolute_path))
        return None
    except ObjectDoesNotExist:
        if createtracker:
            try:
                # create new tracker
                filetracker = file_tracker()
                filetracker.set_filename(absolute_path, dosave=False)
            except Exception as ex:
                _log.error('Unable to create new file tracker for: '
                           '{}\n{}'.format(absolute_path, ex))
                filetracker = None
        else:
            filetracker = None
    except Exception as ex:
        _log.error('Error retrieving file tracker: {}'.format(absolute_path))
        return None

    if (filetracker is not None) and (dosave):
        filetracker.save()
    return filetracker


def update_tracker_views(absolute_path, createtracker=True, dosave=True):
    """ update a file tracker's view_count,
        will create the file_tracker if wanted.
    """
     
    filetracker = get_file_tracker(absolute_path, createtracker)
    if filetracker is None:
        return None
    
    filetracker.view_count += 1
    if dosave:
        filetracker.save()

    return filetracker


def update_tracker_downloads(absolute_path, createtracker=True, dosave=True):
    """ updates a file trackers download_count,
        will create the file_tracker if wanted.
    """
    
    filetracker = get_file_tracker(absolute_path, createtracker)
    if filetracker is None:
        return None
    
    filetracker.download_count += 1
    if dosave:
        filetracker.save()
    
    return filetracker


def update_tracker_projects(tracker_, project_object, dosave=True):
    """ adds a project to this tracker's project field safely. """
    
    if hasattr(tracker_, 'id'):
        trackerid = tracker_.id
    else:
        trackerid = None
    # Tracker must be saved at least once before adding a project relation.
    if trackerid is not None:
        if trackerid < 0:
            tracker_.save()
        tracker_.project.add(project_object)
        if dosave:
            tracker_.save()
