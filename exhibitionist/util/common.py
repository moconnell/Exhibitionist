# -*- coding: utf-8 -*-
from __future__ import print_function

class UrlDisplay(object):# pragma: no cover
    """Displays urls as text, hotlinks, or inline HTML if in IPython

    height [default "400px"] - iframe height.
    width [default  "100%"] - iframe width.
    fs_btn [default False]- add a 'full-screen' button to the view.
    """

    def __init__(self, url, height="400px",width="100%", **kwds):

        self.url = url
        self.width = width
        self.height = height
        self.fs_btn = kwds.get('fs_btn', False)

    # noinspection PyBroadException
    @staticmethod
    def check_ipython():
        env = None
        try:
            ip = get_ipython()
            env = "ipython"

            # 0.13, 0.14/1.0dev keep the type of frontend in different places
            front_end = (ip.config.get('KernelApp') or
                         ip.config.get('IPKernelApp'))['parent_appname']
            if "qtconsole" in front_end:
                env = "qtconsole"
            elif "notebook" in front_end:
                env = "notebook"
        except:
            pass
        return env

    def notebook_repr(self):
        """ override this method"""
        from hashlib import sha1
        import random
        rand_hash=sha1(str(random.random())).hexdigest()

        tmpl = """

<iframe src=%s style="width:%s;height:%s; padding-bottom: 5px"
oAllowFullScreen msAllowFullScreen mozAllowFullScreen webkitAllowFullScreen
allowFullScreen id='%s' data-__exhibitionist_id='%s'></iframe>

<script>
// This whole bit is intended for the IPython-specific case
// of child IFrames passing a a static representation of themselves
// back to the IPython window so the view can "frozen" into the notebook
if ( window.IPython !== undefined &&  window.xbReceiveMessage === undefined ) {

    function xbReceiveMessage(event)
    {
        console.log("received postMessage notification");

    //    window.xbev = event.data

    // TODO validate origin, and data structure

        xbid = event.data.xbid;
        svg = event.data.svg;
//        console.log("setting html",xbid)
        var maps = {}
        cells = IPython.notebook.get_cells().forEach(function(c) {
            xbId=$(c.element).find("iframe").data('__exhibitionist_id')
            if (xbId) {
                maps[xbid]= c.cell_id;
            }
        });
        cell = IPython.notebook.get_cells().filter(function(c){return c.cell_id === maps[xbid]})
        if (cell.length) {
//            console.log("setting output")
            cell[0].output_area.outputs[0].html=(svg)
        };
        $("#"+xbid).parent().html(svg)
    }
    window.addEventListener("message", xbReceiveMessage, false);
}

(function f(){

    function g(){
    // TODO: make more robust.
        var xbid = '%s'
        if ( $("#"+xbid).length) {
            console.log("trying to find myself","#"+xbid,$("#"+xbid));

            $("#"+xbid)[0].contentWindow.postMessage(xbid,"*")
             // setTimeout(g,1000);
        } else {
            setTimeout(g,500);
        }
    }
     setTimeout(g,1000);
 }
)();

</script>

"""

        result = tmpl % (self.url, self.width,self.height,rand_hash,rand_hash,rand_hash)

# Source: public domain icon from wikimedia commons
        if self.fs_btn:
            result+="""
<img src="data:image/png;base64,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"
width="20" height="20" alt="FullScreen" id="btn" style="position:absolute; right: 0;top: 0; " onclick='a()'>

<style>
    #btn {
        opacity: 0.3;
    }
    #btn:hover {
        opacity: 1;
    }
</style>

<script>
var a = function() {

    var el = $("iframe");
    var goFullScreen = el[0].requestFullScreen ||
            el[0].mozRequestFullScreen ||
            el[0].webkitRequestFullScreen ||
            el[0].oRequestFullScreen ||
            el[0].msRequestFullScreen;
       console.log(goFullScreen);
    if (goFullScreen) {
        goFullScreen.apply(el[0]);
    } else {
        $("#btn").hide();
    }
};
</script>


"""
        return result

    def qtconsole_repr(self):
        """ override this method"""
        return 'Open this <a href="%s">link</a>  to View the object' % (self.url)

    def __repr__(self):
        return self.url

    def _repr_html_(self):

        if self.check_ipython() == 'notebook':
            return self.notebook_repr()
        elif self.check_ipython() == 'qtconsole':
            return self.qtconsole_repr()
        else:
            raise NotImplementedError()
