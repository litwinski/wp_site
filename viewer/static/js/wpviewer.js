/* Welborn Productions - Viewer
   Handles file-viewer actions on the client side.
   - Christopher Welborn 2013 -desc added in 2014 :)
*/

// Store current relative filename here. The template sends it on the first
// page load, and then it is set with JS when doing ajax calls. 
var wpviewer = {
    // current relative path for file. (/static/file.py)
    current_file : '',
    // current short name (file.py)
    current_name : '',

    enable_link : function (linkelem, enabled) {
        /* Make a menu item enabled/disabled */
        var menutarget = $(linkelem).attr('onclick');
        var linkitem = $(linkelem).children();
        if (!menutarget) { 
            console.log('can\'t find href for element: ' + linkelem);
            return false;
        }
        if (enabled) {
            // ensure this link is 'enabled'
            if (menutarget.indexOf('false') < 0) {
                // change 'false' to 'true' because view_file(filename, true)
                // means 'do not load this file', cancel = true
                $(linkelem).attr('onclick', menutarget.replace('true', 'false'));
                $(linkelem).removeClass('vertical-menu-item-disabled');
                $(linkitem).removeClass('vertical-menu-item-disabled');
                return true;
            } else {
                // already enabled.
                return true;
            }

        } else {
            // ensure this link is 'disabled' (true means disabled)
            if (menutarget.indexOf('true') < 0) {
                $(linkelem).attr('onclick', menutarget.replace('false', 'true'));
                $(linkelem).addClass('vertical-menu-item-disabled');
                $(linkitem).addClass('vertical-menu-item-disabled');
                return true;
            } else {
                // already disabled.
                return true;
            }
        }
    },

    make_menu_item : function (menuname, menufilename, disabledval) {
        /* Create a menu item/link from a name, filename, and enabled/disabled value.
            Arguments:
                menuname      : short file name (file.py)
                menufilename  : relative file name (/static/blah/file.py)
                disabledval   : 'true', or 'false' (sent to onclick: view_file() )
                                must be string value. default is 'false'
        */
        if (!disabledval) { disabledval = 'false'; }

        var menulink = document.createElement('a');
       
        $(menulink).attr('href', 'javascript: void(0);');
        $(menulink).attr('class', 'vertical-menu-link');
        // add child list element/name
        var menuitem = document.createElement('li');
        $(menuitem).addClass('vertical-menu-item');
        if (disabledval == 'true') {
            $(menuitem).addClass('vertical-menu-item-disabled');
        }
        // add child span element/name
        var menutext = document.createElement('span');
        $(menutext).addClass('vertical-menu-text');
        // make text a child of list, which is a child of the link.
        $(menutext).text(menuname);
        $(menuitem).append(menutext);
        $(menulink).append(menuitem);

        $(menulink).attr('onclick', 
            'javascript: view_file(\'' + menufilename + '\', ' + disabledval + ');');
        
        // needs disabled class?
        if (disabledval == 'true') {
            $(menulink).addClass('vertical-menu-item-disabled');
        }
        // return menu link item
        return menulink;        
    },

    set_current_file : function (filename) {
        if (filename) {
            if (filename[0] == '/') {
                wpviewer.current_file = filename;
            } else {
                wpviewer.current_file = '/' + filename;
            }
            // set shortname for file.
            var nameparts = wpviewer.current_file.split('/');
            wpviewer.current_name = nameparts[nameparts.length -1];
            
        }
    }

};

/* This all needs to be contained in 'wpviewer', but i'll leave that for
   another day.
*/
function change_content(s) {
    /* Change ace editor content, move selection to start. */
    wp_content.setValue(s);
    wp_content.selection.selectFileStart();
}

// handles valid responses from viewer.views.view_loader() and .ajax_contents()
function load_file_data (xhrdata) {
    var file_info = JSON.parse(xhrdata.responseText);
    
    // Server-side error.
    if (file_info.status == 'error') {
        var errmessage = file_info.message;
        if (errmessage) {
            $('#file-content-box').html('<span>' + errmessage + '</span>');
        } else {
            $('#file-content-box').html('<span>Sorry, an unknown error occurred.</span>');
        }
        return;
    }

    // Content
    if (file_info.file_content) {
        // Load content into ace editor...
        change_content(file_info.file_content);
        // Set Language
        var ace_mode = wp_modelist.getModeForPath(file_info.static_path);
        wp_content.getSession().setMode(ace_mode.mode);
        $('#file-content').fadeIn();

    } 
    else {
        $('#file-content-box').html('<span>Sorry, no content in this file...</span>');
        return;
    }

    /* Header for projects ...pythons None equates to null in JS. */
    if (file_info.project_alias !== null && file_info.project_name !== null) {
        $('#project-title-name').html(file_info.project_name);
        $('#project-link').click( function () { wptools.navigateto('/projects/' + file_info.project_alias); });
        if (file_info.project_alias) { $('#project-info').fadeIn(); }
    // Header for miscobj.
    } else if (file_info.misc_alias !== null && file_info.misc_name !== null) {
        $('#project-title-name').html(file_info.misc_name);
        $('#project-link').click( function () { wptools.navigateto('/misc/' + file_info.misc_alias); });
        if (file_info.misc_alias) { $('#project-info').fadeIn(); }
    }
    // File info
    if (file_info.file_short && file_info.static_path) {
        $('#viewer-filename').html(file_info.file_short);
        $('#file-link').click( function () { wptools.navigateto('/dl/' + file_info.static_path ); });
        if (file_info.file_short) { $('#file-info').fadeIn(); }
        // set current working filename.
        wpviewer.set_current_file(file_info.static_path);
    }
        
    // Menu builder
    var menu_items = file_info.menu_items;
    if (menu_items) {
        var menu_length = menu_items.length;
        var existing_items = $('.vertical-menu-item');
        var existing_length = existing_items.length;
        var menufilename;
        var menuname;
        // Build the menu from scratch if this is the first load.
        if (existing_length === 0 && menu_length > 0 ) {
            var menufrag = document.createDocumentFragment();
            var menuitem;
            $.each(menu_items, function () {
                menufilename = this[0].replace(/[ ]/g, '/');
                menuname = this[1];
                var disabledval = 'false';
                // Disable current file in menu.
                if (menufilename == wpviewer.current_file) {
                    // this item is disabled.
                    disabledval = 'true';
                }
                menuitem = wpviewer.make_menu_item(menuname, menufilename, disabledval);
                $(menufrag).append(menuitem);
            });
            // Add final menu and show it.
            $('#file-menu-items').append(menufrag);
            $('#file-menu').fadeIn();
        } else {
            // Re-mark current file (disable current file in menu)
            $.each($(".vertical-menu-link"), function () {
                // get name from this link.
                menuname = $(this).children().text();
                if (menuname == wpviewer.current_name) {
                    // fix onclick for view_file().
                    wpviewer.enable_link(this, false);
                } else {
                    // ensure this item is enabled.
                    wpviewer.enable_link(this, true);
                }
            });
        }
    }
        
}


// setup initial ace editor
function setup_ace (initial_filename) {
    wp_content = ace.edit('file-content');
    // highlight style
    wp_content.setTheme('ace/theme/solarized_dark');
    // various settings for ace
    wp_content.setHighlightActiveLine(true);
    wp_content.setAnimatedScroll(true);
    wp_content.setFontSize(14);
    // ensure read-only access to content
    wp_content.setReadOnly(true);
    wp_modelist = ace.require('ace/ext/modelist');

    // if an initial filename was passed, set the mode for it.
    if (initial_filename) {
        // get file mode for ace based on filename.
        var ace_mode = wp_modelist.getModeForPath(initial_filename);
        if (ace_mode) {
            wp_content.getSession().setMode(ace_mode.mode);
        }
    }
}

// update floater message and size/position
function update_loading_msg (message) {
    $('#floater-msg').html(message);
    wptools.center_element('#floater');
    var floater = $('#floater');
    var scrollpos = $(this).scrollTop();
    floater.css({'top': (scrollpos + 200) + 'px'});
    
    $('#floater').fadeIn();
}

function view_file (filename, cancel) {
    if (!filename) {
        return false;
    }

    if (cancel) {
        return false;
    }

    // JSON data to send...
	var filedata = { file: filename };

	// change the loading message for proper file name.
	update_loading_msg('<span>Loading file: ' + wpviewer.current_file + '...</span>');

	//$('#project-info').fadeOut();
	$('#file-info').fadeOut();
	
	$.ajax({
		type: 'post',
		contentType: 'application/json',
		url: '/view/file/',
		data: JSON.stringify(filedata),
		dataType: 'json',
		failure: function (xhr, status, errorthrown) {
			console.log('failure: ' + status);
		},
		complete: function (xhr, status) {
						
			// handle errors...
			if (status == 'error') {
				$('#file-content-box').html('<span class=\'B\'>Sorry, either that file doesn\'t exist, or there was an error processing it.</span>');
				console.log('wp-error response: ' + xhr.responseText);
			} 
			else {
				// Data okay to use, send it to the file loader.
				load_file_data(xhr);
			}
			// done loading success or error
			$('#floater').fadeOut();
		},
		status: {
			404: function () { console.log('PAGE NOT FOUND!'); },
			500: function () { console.log('A major error occurred.'); }
		}
	});

}



