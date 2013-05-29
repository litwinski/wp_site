# Mark generated Html as safe to view.
from django.utils.safestring import mark_safe # don't escape html with strings marked safe.

# Project Info
from projects.models import wp_project

# Local tools
from wp_main.utilities import utilities
from wp_main.utilities import responses
from wp_main.utilities import htmltools
from projects import tools


# logging
from wp_main.utilities.wp_logging import logger
_log = logger('projects').log




def index(request):
    """ Main Project Page (index/listing) """
    
    # get projects
    if wp_project.objects.count() == 0:
        projects_content = "<span>Sorry, no projects available yet.</span>"
    else:
        # list all projects...
        projects_content = "<div class='project_listing'>\n"
        for proj in [p for p in wp_project.objects.all().order_by('name') if not p.disabled]:
            projects_content += project_listing(request, proj)
        projects_content += "</div>\n"
    # get vertical projects menu
    projects_menu = tools.get_projects_menu()                  
  
    # render final page
    return responses.clean_response("projects/index.html",
                                    {'request': request,
                                     'extra_style_link_list': [utilities.get_browser_style(request)],
                                     'projects_content': mark_safe(projects_content),
                                     'projects_menu': mark_safe(projects_menu),
                                     })


def project_listing(request, project):
    """ Returns a single project listing for when building the projects index """
    
    # Build project name/link
    p_namelink = htmltools.wrap_link("<span class='header project_name'>" + project.name + "</span>", 
                       "/projects/" + project.alias)
    
    # Build project listing module
    _content = "<div class='wp-block project_container'>\n" + \
                "<div class='project_header'>\n" + \
                p_namelink + \
                "<br/>\n" + \
                "<span class='version'>version " + project.version + "</span>\n" + \
                "<br/>\n" + \
                "</div>\n" + \
                "<div class='project_desc'>\n" + \
                "<span class='desc'>" + project.description + "</span>\n" + \
                "</div></div>\n"   
    return _content


def project_page(request, project, requested_page, source=""):
    """ Project Page (for individual project) """
    
    # Set default flags
    use_screenshots = False
    # default extra style needed
    extra_style_link_list = [utilities.get_browser_style(request)]

    # default content if project is found, but has no content
    no_content = """<div class='project_container'>
                    <div class='project_title'>
                        <h1 class='project-header'>%s</h1>
                    </div>
                    <span>No information found for: %s</span>
                    </div>"""
    # initialize response (if it changes before the return then something went wrong.)
    response = None
    
    # if project matches list was sent, use it.
    if isinstance(project, (list, tuple)):
        #_log.debug("Found project matches: " + '\n    '.join([p.name for p in project]))
        shtml = tools.get_matches_html(project, requested_page)
        project_title = False
    elif project is None:
        # No project returned (probably accessing a disabled project)
        response = responses.alert_message("Sorry, I can't find that project.",
                                           "<a href='/projects'><span>Click here to go back to the projects listing.</span></a>")
    else:
        # Found Project, build page.
        project_title = project.name
        # extra html content, if any.
        scontent = tools.get_html_content(project)
        
        if scontent == "":
            # default response unless more information is loaded.
            shtml = no_content % (project_title, project_title)
        else:
            # prepare extra content from html file, adding screenshots/ads/downloads
            shtml = tools.prepare_content(project, scontent) + '\n</div>'
            # tell the template whether or not to use the screenshots box.
            use_screenshots = ("screenshots_box" in shtml)
            # gather extra style needed
            if ('<div class="highlight"' in shtml):
                extra_style_link_list.append("/static/css/highlighter.css")
           
        # track project views
        project.view_count += 1
        project.save()

    # build vertical projects menu
    projects_menu = tools.get_projects_menu()                  
    if response is None:
        return responses.clean_response("projects/project.html",
                                        {'request': request,
                                         'project_content': mark_safe(shtml),
                                         'project_title': project_title,
                                         'projects_menu': mark_safe(projects_menu),
                                         'extra_style_link_list': extra_style_link_list,
                                         'use_screenshots': use_screenshots,
                                         })
    else:
        return response


def request_any(request, _identifier):
    """ returns project by name, alias, or id 
        returns list of possible matches on failure.
        returns project on success
    """
    
    proj = get_withmatches(utilities.safe_arg(_identifier))
    return project_page(request, proj, _identifier, source="by_any")
   
   
def request_id(request, _id):
    """ returns project by id """
    
    proj = get_byid(utilities.safe_arg(_id))
    return project_page(request, proj, str(_id), source="by_id")


def request_alias(request, _alias):
    """ returns project by alias """
    
    proj = get_byalias(utilities.safe_arg(_alias))
    return project_page(request, proj, _alias, source="by_alias")


def request_name(request, _name):
    """ returns project by name """
    
    proj = get_byname(utilities.safe_arg(_name))
    return project_page(request, proj, _name, source="by_name")


def get_byname(_name):
    """ safely retrieve project
        returns None on failure. """
        
    try:
        proj = wp_project.objects.get(name=_name)
        return proj if not proj.disabled else None
    except wp_project.DoesNotExist:
        for proj in wp_project.objects.all():
            if proj.name.lower().replace(' ', '') == _name.lower().replace(' ',''):
                return proj
        return None
    except:
        return None
    
    
def get_byalias(_alias):
    """ safely retrieve project
        returns None on failure. """
        
    try:
        proj = wp_project.objects.get(alias=_alias)
        return proj if not proj.disabled else None
    except wp_project.DoesNotExist:
        return None
    except:
        return None
    
        
def get_byid(_id):
    """ safely retrieve project
        returns None on failure. """
        
    try:
        proj = wp_project.objects.get(id=_id)
        return proj if not proj.disabled else None
    except:
        return None


def get_withmatches(_identifier):
    """ safely retrieve project by name, alias, or id.
        returns project on success,
        return list of possible close matches on failure 
    """
    identifiers = str(_identifier).split(' ')
    
    try:
        _id = int(identifiers[0])
        proj = get_byid(_id)
    except:
        # not an id, try alias.
        proj = get_byalias(identifiers[0])
        if proj is None:
            # Try name
            proj = get_byname(' '.join(identifiers))
    
    # Search for matches
    if proj is None:
        lst_matches = []
        # Try all words in identifier seperately
        for _word in identifiers:
            _search = str(_word).lower()
            _strim = _search.replace(' ', '')
            # still no project, look for close matches...
            for project in [p for p in wp_project.objects.order_by('name') if not p.disabled]:
                _name = project.name.lower()
                _nametrim = _name.replace(' ', '')
                _alias = project.alias.lower()
                _desc = project.description.lower()
                _desctrim = _desc.replace(' ', '')
                _id = str(project.id)
                # try matching in various ways
                if ((_strim in _nametrim) or
                    (_nametrim in _strim) or
                    (_strim in _desctrim) or
                    (_strim in _alias) or
                    (_alias in _strim) or
                    (_strim in _id)):
                    if not project in lst_matches:
                        lst_matches.append(project)
        # return list of matching projects
        return lst_matches
    else:
        # project was found (only show if its not disabled)
        return proj if not proj.disabled else None
    
    
