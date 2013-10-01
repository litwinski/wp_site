#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
      project: Welborn Productions - Statistics
     @summary: Gathers info about blog/project views/downloads and any other
               info I can grab.
    
      @author: Christopher Welborn <cj@welbornprod.com>
@organization: welborn productions <welbornprod.com>
 
   start date: May 25, 2013
'''

import sys, os, os.path #@UnusedImport: os is used, grow up pydev.

# Append project's settings.py dir.
scriptpath = sys.path[0]
project_dir = os.path.split(scriptpath)[0]
settings_dir = os.path.join(project_dir, "wp_main/")
if not settings_dir in sys.path: sys.path.insert(0, settings_dir)
if not project_dir in sys.path: sys.path.insert(0, project_dir)


# Set django environment variable (if not set yet)
if not os.environ.has_key("DJANGO_SETTINGS_MODULE"):
    os.environ["DJANGO_SETTINGS_MODULE"] = "wp_main.settings"
    
# Import welbornprod stuff
try:
    from blogger.models import wp_blog
    from projects.models import wp_project
    from downloads.models import file_tracker
    
except ImportError as eximp:
    print "unable to import welbornprod modules!\n" + \
          "are you in the right directory?\n\n" + str(eximp)
    sys.exit(1)

# everything from welborn prod was imported correctly.
#print "django environment ready..."

# import local tools
try:
    from wpdict import print_block
except ImportError as eximp:
    print "unable to import wpdict.py!\n" + \
          "is it in the same directory as this script?\n\n" + str(eximp)
          
# local tools were imported correctly.
#print "local tools imported...\n"

# possible argument flags/options
possible_args = (('-a', '--all'),
                 ('-b', '--blog'),
                 ('-p', '--projects'),
                 ('-v', '--views'),
                 ('-d', '--downloads'),
                 ('-f', '--files'),
                 ('-o=', '--orderby'),
                 )
# print formatting for print_block()
printblock_args = {'prepend_text': '    ',
                   'append_key': ': ',
                   'prepend_val': None}

# default orders
orderby_projects = 'name'
orderby_posts = '-posted'
orderby_files = 'shortname'

def main(args):

    if len(args) == 0:
        return print_all()
    ret = None
    argd = make_arg_dict(args, possible_args)
    
    orderby = argd['--orderby']
    if orderby is not None: orderby = orderby.lower() # all my attr's are lowercase.
    
    if argd['--all']:
        return print_all(order=orderby)
    
    if argd['--blog']:
        ret = print_blogs_info(order=orderby)
    if argd['--projects']:
        ret = print_projects_info(order=orderby)
    if argd['--files']:
        ret = print_files_info(order=orderby)
    if argd['--views']:
        ret = print_most_views()
    if argd['--downloads']:
        ret = print_most_downloads()
        
    if ret is None:
        # try getting object from argument...
        obj = get_object_byname(args[0])
        if obj is None:
            print "unable to locate info for: " + args[0]
            print "needs more info, like a project name or blog slug."
            return 1
        return print_object_info(obj)


def make_arg_dict(args, arg_tuples):
    argdict = {}
    def find_val(opt):
        short_=opt[0].strip('=')
        long_=opt[1]
        for arg in args:
            if arg.startswith(short_) or arg.startswith(long_):
                if '=' in arg:
                    try:
                        opt,val = arg.split('=')
                        return val
                    except:
                        # invalid option syntax (users fault)
                        return None
                else:
                    # no '=' in option (users fault)
                    return None
        # option wasn't found in args
        return None
    
    # parse args        
    for argoption in arg_tuples:
        if '=' in argoption[0]:
            #this is a setting, we need to find its value (if any)
            possibleval = find_val(argoption)
            argdict[argoption[1]] = possibleval
        else:
            # regular flag, its either there or it isn't.
            argdict[argoption[1]] = ((argoption[0] in args) or (argoption[1] in args))
    return argdict

def get_object_id(obj):
    obj_type = get_object_type(obj).lower().replace(' ', '')
    if obj_type == 'project':
        return obj.name
    elif obj_type == 'blogpost':
        return obj.slug
    elif obj_type == 'file':
        return obj.shortname
    else:
        return 'Unknown Object!'
    
def get_object_type(obj):
    if hasattr(obj, 'version'):
        return 'Project'
    elif hasattr(obj, 'posted'):
        return 'Blog Post'
    elif hasattr(obj, 'shortname'):
        return 'File'
    else:
        return 'Unknown'
    
def get_object_byname(partialname):
    try:
        obj = wp_project.objects.get(name=partialname)
    except:
        obj =None
    if obj is not None: return obj
    
    try:
        obj = wp_blog.objects.get(name=partialname)
    except:
        obj = None
    if obj is not None: return obj
    
    try:
        obj = file_tracker.objects.get(shortname=partialname)
    except:
        obj = None
    if obj is not None: return obj
    
    
    # search projects
    for proj in wp_project.objects.order_by('name'):
        if proj.name.lower().startswith(partialname.lower()):
            return proj
    
    # search blog posts
    for post in wp_blog.objects.order_by('-posted'):
        if post.slug.startswith(partialname.lower()):
            return post
    
    # search file trackers
    for filetracker in file_tracker.objects.order_by('shortname'):
        if filetracker.shortname.startswith(partialname.lower()):
            return filetracker
    
    return None

def print_all(order=None):
    print_blogs_info(order)
    print ' '
    print_projects_info(order)
    print ' '
    ret = print_files_info(order)
    return ret

def print_blogs_info(order=None):
    """ Print all info gathered with get_blogs_info(), formatted with a print_block() """
    if wp_blog.objects.count() == 0:
        print('\nNo blog posts to gather info for!')
        return 1
    
    if order is None:
        order = orderby_posts
    else:    
        if not hasattr(wp_blog.objects.all()[0], order.strip('-')):
            print "Posts don't have a '" + order + "' attribute, using the default: " + orderby_posts
            order = orderby_posts
    blog_info = get_blogs_info(order)
    print "Blog Stats order by " + order + ":"
    blog_info.printblock(**printblock_args)
    print ' '
    return 0


def print_projects_info(order=None):
    """ Print all info gathered with get_projects_info(), formatted with a print_block() """
    if wp_project.objects.count() == 0:
        print('\nNo projects to gather info for!')
        return 1
    
    if order is None:
        order = orderby_projects
    else:
        if not hasattr(wp_project.objects.all()[0], order.strip('-')):
            print "Projects don't have a '" + order + "' attribute, using the default: " + orderby_projects
            order = orderby_projects
    proj_info = get_projects_info(order)
    print 'Project Stats ordered by ' + order + ':'
    proj_info.printblock(**printblock_args)
    print ' '
    
    return 0


def print_files_info(order=None):
    """ Print all info gathered with get_files_info(), formatted with a print block. """
    
    if file_tracker.objects.count() == 0:
        print('\nNo file-trackers to gather info for.')
        return 1
    
    if order is None:
        order = orderby_files
    else:
        if not hasattr(file_tracker.objects.all()[0], order.strip('-')):
            print "File Trackers don't have a '" + order + "' attribute, using the default: " + orderby_files
            order = orderby_files
            
    file_info = get_files_info(order)
    print "File Stats ordered by " + order + ":"
    file_info.printblock(**printblock_args)
    print ' '
    
    return 0

def print_object_info(obj):
    obj_info = get_object_info(obj)
    if obj_info is None: return 1
    
    obj_type = get_object_type(obj)
    
    print 'Stats for: ' + get_object_id(obj) + ' [' + obj_type +']'
    obj_info.printblock(**printblock_args)
    print ' '
    
    return 0


def print_most_views():
    pblock = get_most_views()
    if pblock is None:
        print "couldn't retrieve print block for most views!\n"
        return 1
    else:
        print "Most views:"
        pblock.printblock(**printblock_args)
        print ' '
        return 0


def print_most_downloads():
    pblock = get_most_downloads()
    if pblock is None:
        print "couldn't retrieve print block for most downloads!\n"
        return 1
    else:
        print "Most downloads:"
        pblock.printblock(**printblock_args)
        print ' '
        return 0
    
    
def get_projects_info(orderby=None):
    pblock = print_block()
    if wp_project.objects.count() == 0:
        return pblock
    
    if orderby is None:
        orderby = orderby_projects
    if not hasattr(wp_project.objects.all()[0], orderby.strip('-')):
        orderby = orderby_projects
    for proj in wp_project.objects.order_by(orderby):
        # intialize empty info for this project
        #pblock[proj.name] = [" "] # blank item on top...
        newpblock = get_project_info(proj, pblock)
        if newpblock is not None: pblock = newpblock
        # get download count
        #pblock[proj.name] = ["downloads: " + str(proj.download_count)]
        # get view count
        #pblock[proj.name].append("    views: " + str(proj.view_count))
    
    return pblock


def get_blogs_info(orderby=None):
    pblock = print_block()
    if wp_blog.objects.count() == 0:
        return pblock
    
    if orderby is None:
        orderby = orderby_posts
    if not hasattr(wp_blog.objects.all()[0], orderby.strip('-')):
        orderby = orderby_posts
        
    for post in wp_blog.objects.order_by(orderby):
        newpblock = get_post_info(post, pblock)
        if newpblock is not None: pblock = newpblock
        # get view count
        #pblock[post.slug] = ["views: " + str(post.view_count)]
    return pblock


def get_files_info(orderby=None):
    pblock = print_block()
    if file_tracker.objects.count() == 0:
        return pblock
    
    filetrackers = file_tracker.objects.all()
    if filetrackers is None:
        return pblock
    elif filetrackers == []:
        return pblock
    
    if orderby is None:
        orderby = orderby_files
    if not hasattr(filetrackers[0], orderby.strip('-')):
        orderby = orderby_files
    
    for filetracker in filetrackers.order_by(orderby):
        newpblock = get_file_info(filetracker, pblock)
        if newpblock is not None: pblock = newpblock
    
    return pblock


def get_file_info(filetrack_obj, pblock=None):
    if filetrack_obj is None: return None
    if pblock is None: pblock = print_block()
    
    try:
        pblock[filetrack_obj.shortname] = ["downloads: " + str(filetrack_obj.download_count)]
        pblock[filetrack_obj.shortname].append("    views: " + str(filetrack_obj.view_count))
    except Exception as ex:
        print "unable to retrieve file tracker info!\n" + str(ex)
        return None
    return pblock

def get_post_info(post_object, pblock=None):
    if post_object is None: return None
    if pblock is None: pblock = print_block()
    
    try:
        pblock[post_object.slug] = ["views: " + str(post_object.view_count)]
    except Exception as ex:
        print "unable to retrieve blog post info!\n" + str(ex)
        return None
    
    return pblock

def get_object_info(obj):
    """ pass it an object from 'get_object_byname' and this will
        decide whether its a blog or project, and return its info.
    """
    
    if obj is None: return None
    
    if hasattr(obj, 'posted'):
        return get_post_info(obj)
    elif hasattr(obj, 'name'):
        return get_project_info(obj)
    elif hasattr(obj, 'shortname'):
        return get_file_info(obj)
    else:
        return None
    
def get_project_info(proj_object, pblock=None):
    if proj_object is None: return None
    
    if pblock is None: pblock = print_block()
    
    try:
        pblock[proj_object.name] = ["downloads: " + str(proj_object.download_count)]
        pblock[proj_object.name].append("    views: " + str(proj_object.view_count))
    except Exception as ex:
        print "unable to retrieve project info!\n" + str(ex)
        return None
    return pblock

def get_most_views():
    """ finds objects with the most views """
    
    # find most popular project
    proj = wp_project.objects.order_by('-view_count')[0]
    
    # blog posts
    post = wp_blog.objects.order_by('-view_count')[0]
    
    # file trackers
    filetracker = file_tracker.objects.order_by('-view_count')[0]
    
    pblock = print_block()
    pblock['[ Projects ]'] = [' ']
    newpblock = get_project_info(proj, pblock)
    if newpblock is not None: pblock = newpblock
    # passing pblock to it adds the blog post info to the projects info. (for making a single print_block)
    pblock['[ Posts ]'] = [' ']
    postblock = get_post_info(post, pblock)
    if postblock is not None: pblock = postblock
    
    pblock['[ Files ]'] = [' ']
    fileblock = get_file_info(filetracker, pblock)
    if fileblock is not None: pblock = fileblock
        
    return pblock


def get_most_downloads():
    """ finds project with the most downloads """
    
    # find most downloaded project.
    proj = wp_project.objects.order_by('-download_count')[0]
    filetracker = file_tracker.objects.order_by('-download_count')[0]
    pblock = print_block()
    pblock['[ Project ]'] = [' ']
    newblock = get_project_info(proj, pblock)
    if newblock is not None: pblock = newblock
    
    pblock['[ File ]'] = [' ']
    fileblock = get_file_info(filetracker, pblock)
    if fileblock is not None: pblock = fileblock
    
    return pblock

# START OF SCRIPT
if __name__ == "__main__":
    args = sys.argv[1:]
    sys.exit(main(args))