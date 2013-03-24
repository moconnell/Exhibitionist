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
        import os.path as osp
        rand_hash=sha1(str(random.random())).hexdigest()
        frags_dir  = osp.abspath(osp.join(osp.dirname(__file__),"../static"))
        # This will have to become a template engine dependency
        # resistance is futile.
        markup = open(osp.join(frags_dir,"ipython_iframe.html")).read()\
            .format(url=self.url,
                    width=self.width,
                    height=self.height,
                    rand_hash=rand_hash)

        markup += open(osp.join(frags_dir,"ipython_freezing.html")).read() % (rand_hash,)
        if self.fs_btn:
            markup += open(osp.join(frags_dir,"ipython_fs_btn.html")).read()

        return markup

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
