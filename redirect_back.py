# Implement redirect_back
#
# See http://flask.pocoo.org/snippets/62/ for documentation

from urlparse import urlparse, urljoin
from flask import request, url_for, redirect

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target

def redirect_back(endpoint, **values):
    target = request.form['next']
    print 'redirect_back, target =', target, 'endpoint =', endpoint
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    print 'redirect_back redirecting to', target
    return redirect(target)

