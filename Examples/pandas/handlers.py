# -*- coding: utf-8 -*-
from __future__ import print_function

import codecs
import os
import logging

from exhibitionist.toolbox import ( getLogger, http_handler,
                                    JSONRequestHandler, StaticFileHandler,
                                    HTTPError)
context = None # eliminate tooling "symbol not found"
logger = getLogger(__name__)

from tornado.template import Template


@http_handler(r'/pandas/df/{{objid}}$', view_name="dfView")
class GetDataFrameView(JSONRequestHandler):
    def prepare(self):
        tmpl_file = os.path.join(self.get_template_path(),"jqgrid_view.html")
        if not(os.path.isdir(self.get_template_path())):
            self.set_status(500)
            self.finish("Template path does not exist")
            return
        with codecs.open(tmpl_file) as f:
            self.tmpl = Template(f.read())


    def get(self, objid):
        import pandas as pd
        # by default the object is placed in self.object
        if not isinstance(context.object, pd.DataFrame):
            self.set_status(500)
            self.finish("Object exists, but is not a dataframe")
            return

        base = "http://{host}/pandas".format(host=self.request.host)
        body = self.tmpl.generate(api_url=base,
                                  objid=objid,
                                  static_url=self.static_url)

        self.write(body)


@http_handler(r'/pandas/(?P<noun>columns|rows|edit)/{{objid}}$')
class jqGridPandasAjax(JSONRequestHandler):
    def get(self, objid, noun):
        import math
        import pandas as pd
        # logger.info(self.request.arguments)
        def listify(o):
            if not isinstance(o, (list, tuple)):
                o = [o, ]
            return list(o)

        df = context.object # we set @http_handler(obj_attr='the_object')

        if not isinstance(df, pd.DataFrame):
            raise (HTTPError(500, "Object exists, but is not a dataframe"))

        if len(df.columns) == 0:
            cidx_nlevels = 0
        else:
            cidx_nlevels = 1 if not hasattr(df.columns, "levels") else len(df.columns[0])

        if len(df.index) == 0:
            ridx_nlevels = 0
        else:
            ridx_nlevels = 1 if not hasattr(df.index, "levels") else len(df.index[0])

        if noun == "columns":
            def mk_col(index, headings, width=80, cssClass="", formatter=None, **kwds):
                d = dict(index=index, headings=headings,
                         width=width, cssClass=cssClass, formatter=formatter)
                d.update(kwds)
                return d

            if (cidx_nlevels == 0):
                raise (HTTPError(500, "no columns"))

            # fake multirow header for pandas Column MultiIndex as multiple lines of text

            # the name field contains a list of string (possibly singleton)
            # one per level of column index
            if cidx_nlevels == 1:
                cols = [[""] * cidx_nlevels] * ridx_nlevels + map(lambda x: [unicode(x)], list(df.columns))
            else:
                cols = [[""] * cidx_nlevels] * ridx_nlevels + map(lambda x: map(unicode, x), list(df.columns))

            columns = [mk_col(i, headings=headings, cssClass="", is_index=i < ridx_nlevels)
                       for i, headings in enumerate(cols)]
            payload = dict(columns=columns)
            self.write_json(payload)

        elif noun == "rows":
            # the returned json schema is forced by jqGrid
            rows = int(self.get_argument("rows")) # rows per page
            page = int(self.get_argument("page")) # #page requesed

            offset = ((page - 1) * rows)
            count = rows
            logger.info(offset)
            payload = dict(total=int(math.ceil(len(df) // rows)), # total number of pages
                           page=page, # current page number
                           records=len(df)) # total rows in dataframe

            if offset < 0 or count < 0 or offset >= len(df):
                # empty response, probably shouldn't happen, try to recover
                payload.update(dict(rows=[]))
                logger.warn("Bad request: offset:%s count:%s" % (offset, count))
            else:
                count = min(count, len(df) - offset) # num rows to return
                # all data gets converted to string, circumvent
                # the dtypes trap. json can't serialize int64, NaNs, etc
                rows = []
                payload['rows'] = rows
                for i in range(offset, offset + count):
                    vals = listify(df.index[i]) + list(df.irow(i).tolist())
                    # rows.append(dict(id=i,cell=map(unicode,vals)))
                    a = {j:unicode(val) for j,val in enumerate(vals)}
                    a.update(dict(id=i))
                    rows.append(a)

                # logger.info(payload)
            self.write_json(payload)

    def post(self, objid,noun):
        import pandas as pd

        if not noun == 'edit' and\
            isinstance(context.object, pd.DataFrame):
            self.set_status(500)
            self.finish("That's an error.")
            return

        # lost of cruddy error checking here

        # the POST bears these keys
        # {'oper': ['edit'], '2': ['R4C1'], 'id': ['5']}
        # id is 1-based row number,
        # int-string key is 1-based (que'lle horrible API!)
        # it's value (in list) is the new value

        args = self.request.arguments

        #validate
        if not all(k in args for k in ['id','oper']) and len(args) == 3:
            self.set_status(500)
            return self.finish("Couldn't parse request.")

        rid = args.pop('id')
        oper = args.pop('oper')
        col,val = None,None
        if args.items():
            col,val = args.items()[0]

        if not( len(args) == 1
                and isinstance(oper,list) and len(oper) ==1 and oper[0] == 'edit'
                and isinstance(rid,list) and len(rid) ==1
                and isinstance(val,list) and len(val) ==1
        ):
            logger.info((len(args) == 1 , oper == 'edit'
                        , isinstance(rid,list) , len(rid) ==1
                        , isinstance(val,list) , len(val) ==1))
            self.set_status(500)
            return self.finish("Couldn't parse request.")

        row = int(rid[0])

        try:
            col = int(col)-1
        except:
            self.set_status(500)
            return self.finish("Couldn't parse col.")

        val  = val[0]

        # primitive dtype coercion
        df= context.object
        old_val = df.irow(row)[col]
        try:
            val = type(old_val)(val)
        except:
            self.set_status(500)
            return self.finish("Couldn't coerce new value to proper type.")
        else:
            df.ix[row,col] = val
            logger.info("Replacing old value %s with %s at (%s, %s)" %
                        (old_val,val,row,col))


