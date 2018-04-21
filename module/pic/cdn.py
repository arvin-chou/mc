# -*- coding: utf-8 -*-

# sys
import os
import urllib

from config.config import _logging, settings

logger = _logging.getLogger(__name__)
CDN_DOMAIN = settings.CDN_DOMAIN
PIC_PREFIX = settings.PIC_PREFIX
STATIC_ROOT = settings.STATIC_ROOT

class PicCDN():
    """transfer pic request to CDN server
    """

    def __init__(self):
        pass

    def loaddef():
        with open(os.path.join(STATIC_ROOT, 'static/default/no_image.jpg'), 'rb') as f:
            img = f.read()
        return img
    
    @staticmethod
    def trans(app, request):
        """transfer pic request to CDN server
        """
        if CDN_DOMAIN:
            u = urllib.parse.urljoin(CDN_DOMAIN, PIC_PREFIX, request.path)
            try:
                req = urllib.request.Request(u)
                with urllib.request.urlopen(req) as resp:
                    img = resp.read()
            except urllib.error.URLError as e:
                logger.debug('%s encounter urllib.error.URLError.reason %s', u, e.reason)
                # todo: replace with predefined
                with open(os.path.join(STATIC_ROOT, 'static/default/no_image.jpg'), 'rb') as f:
                    img = f.read()
        else:
            try:
                # img/business/1/icon => www/__pic__/business/1
                p = '/'.join(request.path.split('/')[2:]) # strip lead slash
                with open(os.path.join(STATIC_ROOT, PIC_PREFIX, p), 'rb') as f:
                    img = f.read()
            except Exception as error:
                logger.debug('open %s error %s', os.path.join(STATIC_ROOT, PIC_PREFIX, p), error) 
                img = PicCDN.loaddef()

        return app.response_class(img, mimetype='image/png')
