Exhibitionist
=======

[![Build Status](https://travis-ci.org/Exhibitionist/Exhibitionist.png?branch=master)](https://travis-ci.org/Exhibitionist/Exhibitionist)

Exhibitionist is a Python library that let's you build tiny web-apps that serve
as views for live python objects in your favorite python shell.
It's built on top of [Tornado](http://www.tornadoweb.org/), so you can do
everything Tornado let's you [do](http://www.tornadoweb.org/documentation/overview.html).

If you want to create fully interactive views of python objects using HTML and
leveraging javascript libraries such as [d3.js](http://d3js.org) or your favorite
grid/charting library - exhibitionist allows you to do that succinctly in a way
that closely follows modern web app development practices.

The resulting views are available as urls served from a local server and are viewable directly in
the browser.  Users of [IPython-notebook](http://github.com/ipython/ipython ) can leverage it's
inline display of HTML+Javascript for seamless integration of views into their interactive workflow.

*Features:*

- Out-of-the-box support for two-way message passing between javascript and python using a PubSub mechanism mechanism built on websockets.
- Use AJAX to dynamically load data, work with large data sets, do server things on the server and
  client things on the client.
- Designed as a dependency of other libraries. Integrate it in upstream or use it to
build a UI for objects common in your own workflow.
- Develop views with your favorite HTML/JS/CSS libraries. Everything is supported.
- Supports Python 2.6+, 3.2+.
- Tested on linux, reports (and fixes) for other OS's welcome.
- Unit-tests. Coverage. Examples. yep
- BSD-licensed, go crazy.
- Repo available on github:  [http://github.com/Exhibitionist/Exhibitionist](http://github.com/Exhibitionist/Exhibitionist)

### FAQ

**Got Eyecandy?**

Sure. Here's the "pandas" example showing a view of a [pandas](http://github.com/pydata/pandas)
dataframe using [jqGrid](https://github.com/tonytomov/jqGrid). Data is loaded
using AJAX and you can edit cells in the UI to modify the underlying dataframe.

In IPython-Notebook:

[![Image](https://raw.github.com/y-p/Exhibitionist/master/misc/cross-environment/ipython-nb.png)](https://raw.github.com/y-p/Exhibitionist/master/misc/cross-environment/ipython-nb.png)

In IPython-Qtconsole:

[![Image](https://raw.github.com/y-p/Exhibitionist/master/misc/cross-environment/ipython-qtconsole.png)](https://raw.github.com/y-p/Exhibitionist/master/misc/cross-environment/ipython-qtconsole.png)

And in plain ol' Python:

[![Image](https://raw.github.com/y-p/Exhibitionist/master/misc/cross-environment/python-terminal.png)](https://raw.github.com/y-p/Exhibitionist/master/misc/cross-environment/python-terminal.png)

The inline HTML in IPython-Notebook is just an IFRAME, it looks exactly the same
when viewed directly in your browser.


**How does it work?**

By launching an in-process web-server (Tornado) in a separate thread, request
handlers gain access to live python objects in your python process without
blocking it.

You write request handlers that get handed the python object to be viewed
and return HTML or JSON (or anything) to the client as needed. You serve static
assets from wherever you put them, and keep all the source (templates,
.js,.css, images) files organized in a directory as you usually would.
The server (python) and the client(javascript) can exchange messages
via websockets. Both sides can be subscribers and/or publishers and
push messages to "channels".

**What does "hello world" look like?**

*Short.*

Copy & paste this into your IPython/python prompt:

```python
from exhibitionist.toolbox import *

@http_handler(r'/myView/{{objid}}$')
class ViewAllTheThings(JSONRequestHandler):
    def get(self,objid):
        if self.get_argument("format","") == "json":
            self.write_json(context.object)
        else:
            obj = context.object #  the object associated with objid
            self.write("<br/>".join("<b>{0}</b>:<em>{1}</em>".format(k,v)
                       for k,v in obj.items()))

server = get_server().add_handler(ViewAllTheThings).start()
obj = dict(hello="world")
view_url = server.get_view_url("ViewAllTheThings", obj)
UrlDisplay(view_url)
```

Producing the following result in IPython-Notebook:

[![Image](https://raw.github.com/y-p/Exhibitionist/master/misc/shot1.png)](https://raw.github.com/y-p/Exhibitionist/master/misc/shot1.png)

Tornado gets most of the credit for the example being this concise, Exhibitionist just
adds some sugar.

You can visit the url held in `view_url` directly in a browser, it should look
something like: `http://localhost:port/myView/{some_long_hash}`.

If you append `?format=json` to it you'll get JSON data. a client could get
that data with AJAX.

#### Here's what's going on:
1. We import everything we need from `exhibitionist.toolbox`.
2. we use the `@http_handler` **decorator** to define the "route" for this handler.
The **special marker** `{{objid}}` included in the uri tells Exhibitionist to
do some magic.
3. We define the **Request Handler class**, which derives from `JSONRequestHandler`
(and ultimately `ExhibitionistRequestHandler`), which adds a "write_json()"
method to Tornado's standard handler class.
4. The get method is invoked when a request (matching the route) is made. Because
the class route used the *{{objid}}* marker, `get()` receives and **`objid`** arg.
See Tornado's docs for more info on routes and the tricks you can do with
capture groups.
5. When inside the `get()` method, a `context` object is in scope which **magically
holds a reference** to the object associated with the `objid` extracted from the url.
6. If a `format=json` query parameter is specified, we send the object to `write_json`
to be json-encoded and returned to the client. Otherwise, we render some HTML based
on the object data and send it back to the client with a call to self_write().

That's it for the request handler class.

The remaining few lines instantiate a server, register the handler class with it
and then spawn the server in a new thread. At this point, the server is listening
for requests.

The url for a view is generated by the `get_view_url()` method, which accepts
a view name (usually the handler's class name) and an object to be rendered
by the view.
The returned url can be opened in any browser. `UrlDisplay` is a helper class
which adapts to the running environment in order to present the view's url.
In IPython-notebook it displays the url as inline HTML, in other environment,
you'd get a hotlink or simply the url itself.

**Related Projects**

[Shiny](http://rstudio.github.com/shiny/) for **R** performs a similar function,
although it goes a step further and defines a set of standard UI widgets that you
can build a UI out of, declaratively.

**Where can I see more?**

The `examples/` directory contains several examples:
- 'boilerplate', a heavily documented skeleton project to start your own views with.
- 'pingpong', a project demonstrating the use of PubSub to exchange messages
between server and client using websockets.
- 'kittengram', a silly example that uses D3 to visualize arrays as pet scatter
plots. websockets are used to trigger javascript mischief in the browser from
python. meow.
- 'pandas', a more complete example that renders [pandas](http://www.github.com/pydata/pandas) dataframes
using [jqGrid](https://github.com/tonytomov/jqGrid).
Data is loaded on-demand using AJAX and you can edit dataframe cells directly
in the grid.

To run the examples - clone the repo and install with "python setup.py install".
You need to have the example directory in your python path, it's easiest to just
change directory into the `example/{example_name}` directory.
Then run app.py and follow the prompts.

The code in app.py could just as well be part of your library's
init code, But the included examples are stand-alone.

**Doesn't having multiple threads create Thread-Safety issues?**

Yes it does, and in general you'll have to deal with that. Remember that If
your views are free of side-effects, the worst that can happen is an
inconsistent view. just hit refresh.

**What about security?**

running a local webserver (even if bound by default to localhost) opens up
security issues, certainly. You should take all the precautions appropriate to
your scenario, and bear in mind that fending off attackers was not a central
design concern.

**Doesn't IPython-Notebook already allow you to do interactive UIs?**

The IPython team is working on a big redesign to implement this functionality
using IPython-specific facilities. In Exhibitionist UIs are "just another web-app",
start to finish.

**Why is there no pypi package available?**

Eventually, there will be.
In the meantime, you can install the latest git master using:
```
pip install git+git://github.com/Exhibitionist/Exhibitionist.git
```

**I'm getting 404/500 error codes and I can't see any debug messages**

By default all logging is routed to '/dev/null'.
You need to enable logging and check see if tornado is spitting
out exceptions about what's wrong.
Have a look at `setting.py`, and use a `local_settings.py` file to get going.

**Any Gotchas?**

- The server's socket isn't released until you call server.stop(), remember
to cleanup.
- Be aware that you are exposing your data through a local web server.
By default the server binds to localhost/127.0.0.1 which usually wouldn't
be accessible to other hosts on the network. In general, you should be
running in an environment where access is not a risk.
- Tornado is currently run with debug=False, because it's autoreload
feature can cause unexpected behaviour when files are modified while
working in IPython.
- Testing stale javascript/html due to the browser catch, gets you every time.
Disable caching for development, or do a hard refresh.

**I'm going to use this, what more should I know?**

- When calling server.add_handler() to register your handlers,
you can pass in a request handler class or a module/package,
Exhibitionist will look through them and discover all handler
classes decorated with @http_handler.

- See exhibitionist/providers/websocket/handlers for documentation
of the basic message format for the websocket channel.
You can also look at the frames on the wire in
the "PingPong" example with chrome developer tools support for
monitoring websocket connections.

- Websocket clients that are both publisher and subscriber
on same channel will not receive messages they themselves publish.
on the python side, you can use the "exclude" parameter of server,notify_X()
to exclude a python callback from receiving it's own message.

- Whatever extra keyword argument you pass to @http_handler
will be passed to the initialize(self,**kwds) method of
your request handler class, see tornado documentation
or test_server.py for an example.
