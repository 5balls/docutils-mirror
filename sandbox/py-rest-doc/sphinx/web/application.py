# -*- coding: utf-8 -*-
"""
    sphinx.web.application
    ~~~~~~~~~~~~~~~~~~~~~~

    A simple WSGI application that serves an interactive version
    of the python documentation.

    :copyright: 2007 by Georg Brandl, Armin Ronacher.
    :license: Python license.
"""
from __future__ import with_statement

import re
import cPickle as pickle
from os import path

from .feed import Feed
from .antispam import AntiSpam
from .database import connect, set_connection, Comment
from .util import Request, Response, RedirectResponse, SharedDataMiddleware, \
     NotFound, jinja_env
from ..search import SearchFrontend
from ..util import relative_uri, shorten_result


special_urls = set(['index', 'genindex', 'modindex'])

_mail_re = re.compile(r'^([a-zA-Z0-9_\.\-])+\@'
                      r'(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,})+$')


def get_target_uri(source_filename):
    if source_filename == 'index.rst':
        return ''
    if source_filename.endswith('/index.rst'):
        return source_filename[:-9] # up to /
    return source_filename[:-4] + '/'


def render_template(req, template_name, context=None):
    context = context or {}
    tmpl = jinja_env.get_template(template_name)

    def relative_path_to(otheruri, resource=False):
        if not resource:
            otheruri = get_target_uri(otheruri)
        return relative_uri(req.path, otheruri)
    context['pathto'] = relative_path_to

    # add it here a second time for templates that don't
    # get the builder information from the environment (such as search)
    context['builder'] = 'web'

    return tmpl.render(context)


class DocumentationApplication(object):
    """
    Serves the documentation.
    """

    def __init__(self, conf):
        self.cache = {}
        self.data_root = conf['data_root_path']
        with file(path.join(self.data_root, 'environment.pickle')) as f:
            self.env = pickle.load(f)
        with file(path.join(self.data_root, 'searchindex.pickle')) as f:
            self.search_frontend = SearchFrontend(pickle.load(f))
        self.db_con = connect(path.join(self.data_root, 'sphinx.db'))
        self.antispam = AntiSpam(path.join(self.data_root, 'bad_content'))

    def search(self, req):
        """
        Search the database. Currently just a keyword based search
        """
        if not req.args.get('q'):
            return RedirectResponse('')
        return RedirectResponse('q/%s/' % req.args['q'])

    def show_source(self, req, page):
        """
        Show the highlighted source for a given page.
        """
        source_name = path.join(self.data_root, 'sources', page + '.txt')
        if not path.exists(source_name):
            return self.get_keyword_matches(req)
        with file(source_name) as f:
            return Response(f.read(), mimetype='text/plain')

    def get_page(self, req, url):
        """
        Show the requested documentation page or raise an
        `NotFound` exception to display a page with close matches.
        """
        page_id = url + '.rst'
        cache_possible = True
        comments_enabled = self.env.metadata.get(page_id, {}) \
                               .get('comments_enabled', True)

        # generate feed if wanted
        if req.args.get('feed') == 'comments':
            feed = Feed(req, 'Comments for %s' % url, 'List of comments for '
                        'the topic %s' % url, url)
            for comment in Comment.get_for_page(page_id):
                feed.add_item(comment.title, comment.author, comment.url,
                              comment.parsed_comment_body, comment.pub_date)
            return Response(feed.generate(), mimetype='application/rss+xml')

        # do the form validation and comment saving if the
        # request method is post.
        title = comment_body = ''
        author = req.session.get('author', '')
        author_mail = req.session.get('author_mail', '')
        form_error = None
        preview = None

        if comments_enabled and req.method == 'POST':
            title = req.form.get('title', '').strip()
            author = req.form.get('author', '').strip()
            author_mail = req.form.get('author_mail', '')
            comment_body = req.form.get('comment_body', '')
            fields = (title, author, author_mail, comment_body)

            if req.form.get('preview'):
                preview = Comment(page_id, title, author, author_mail,
                                  comment_body)
            elif req.form.get('homepage') or self.antispam.is_spam(fields):
                form_error = 'Your text contains blocked URLs or words.'
            else:
                if not all(fields):
                    form_error = 'You have to fill out all fields.'
                elif _mail_re.search(author_mail) is None:
                    form_error = 'You have to provide a valid mail address.'
                else:
                    self.cache.pop(url, None)
                    comment = Comment(page_id, title, author, author_mail,
                                      comment_body)
                    comment.save()
                    req.session.update(
                        author=author,
                        author_mail=author_mail
                    )
                    return RedirectResponse(comment.url)
            cache_possible = False

        # if the form validation fails the cache is used so that
        # we can put error messages and defaults to the page.
        if cache_possible:
            try:
                filename, mtime, text = self.cache[url]
            except KeyError:
                pass
            else:
                if path.getmtime(filename) == mtime:
                    return Response(text)

        # render special templates such as the index
        if url in special_urls:
            filename = path.join(self.data_root, 'specials.pickle')
            with open(filename, 'rb') as f:
                context = pickle.load(f)
            templatename = url + '.html'

        # render the page based on the settings in the pickle
        else:
            for filename in [path.join(self.data_root, url) + '.fpickle',
                             path.join(self.data_root, url, 'index.fpickle')]:
                if not path.exists(filename):
                    continue
                with open(filename, 'rb') as f:
                    context = pickle.load(f)
                    break
            else:
                raise NotFound()
            templatename = 'page.html'

        context.update(
            comments_enabled=comments_enabled,
            comments=Comment.get_for_page(page_id),
            preview=preview,
            form={
                'title':            title,
                'author':           author,
                'author_mail':      author_mail,
                'comment_body':     comment_body,
                'error':            form_error
            }
        )
        text = render_template(req, templatename, context)

        if cache_possible:
            self.cache[url] = (filename, path.getmtime(filename), text)
        return Response(text)

    def get_recent_comments_feed(self, req):
        """
        Get the feed of recent comments.
        """
        feed = Feed(req, 'Recent Comments', 'Recent Comments', '')
        for comment in Comment.get_recent():
            feed.add_item(comment.title, comment.author, comment.url,
                          comment.parsed_comment_body, comment.pub_date)
        return Response(feed.generate(), mimetype='application/rss+xml')

    def get_admin_page(self, req, page):
        """
        Get some administration pages.
        """
        raise TypeError()

    pretty_type = {
        'data': 'module data',
        'cfunction': 'C function',
        'cmember': 'C member',
        'cmacro': 'C macro',
        'ctype': 'C type',
        'cvar': 'C variable',
    }

    def get_keyword_matches(self, req, term=None, avoid_fuzzy=False):
        """
        Find keyword matches. If there is an exact match, just redirect:
        http://docs.python.org/os.path.exists would automatically
        redirect to http://docs.python.org/modules/os.path/#os.path.exists.
        Else, show a page with close matches.

        Module references are processed first so that "os.path" is handled as
        a module and not as member of os.
        """
        if term is None:
            term = req.path.strip('/')

        matches = self.env.find_keyword(term, avoid_fuzzy)
        if not matches:
            return
        if type(matches) is tuple:
            return RedirectResponse(get_target_uri(matches[1]) + '#' + matches[2])
        elif type(matches) is list:
            # get some close matches
            close_matches = []
            good_matches = 0
            for ratio, type, filename, anchorname, desc in matches:
                link = get_target_uri(filename) + '#' + anchorname
                good_match = ratio > 0.75
                good_matches += good_match
                close_matches.append({
                    'href':         relative_uri(req.path, link),
                    'title':        anchorname,
                    'good_match':   good_match,
                    'type':         self.pretty_type.get(type, type),
                    'description':  desc,
                })
            return Response(render_template(req, 'not_found.html', {
                'close_matches':        close_matches,
                'good_matches_count':   good_matches,
                'keyword':              term
            }), status=404)

    def __call__(self, environ, start_response):
        """
        Dispatch requests.
        """
        set_connection(self.db_con)
        req = Request(environ)
        if not req.path.endswith('/') and req.method == 'GET':
            query = req.environ.get('QUERY_STRING', '')
            if query:
                query = '?' + query
            resp = RedirectResponse(req.path + '/' + query)
        elif req.path.startswith('/source/'):
            sourcename = req.path[8:].strip('/')
            resp = self.show_source(req, sourcename)
        else:
            url = req.path.strip('/') or 'index'
            if url == 'search':
                resp = self.search(req)
            elif url == 'index' and 'q' in req.args:
                resp = RedirectResponse('q/%s/' % req.args['q'])
            elif url == 'index' and req.args.get('feed') == 'recent_comments':
                resp = self.get_recent_comments_feed(req)
            elif url.startswith('q/'):
                resp = self.get_keyword_matches(req, url[2:])
            elif url.startswith('admin/'):
                resp = self.get_admin_page(req, url[6:])
            else:
                try:
                    resp = self.get_page(req, url)
                except NotFound:
                    resp = self.get_keyword_matches(req)
        return resp(environ, start_response)


def make_app(conf):
    """
    Create the WSGI application based on a configuration dict.
    Handled configuration values so far:

    `data_root_path`
        the folder containing the documentation data as generated
        by sphinx with the web builder.
    """
    app = DocumentationApplication(conf)
    app = SharedDataMiddleware(app, {
        '/style':   path.join(conf['data_root_path'], 'style')
    })
    return app
