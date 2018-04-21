# -*- coding: utf-8 -*-

# sys
import json
import os
import urllib
import string
import random
import re
import traceback
from PIL import Image
from flask import Flask, request
from werkzeug.utils import secure_filename

from config.config import _logging, settings, app, db, platform_model_config
from utils import reqparse, Resource, fields, marshal, inputs
from utils.error import omitError
from module.common import GetTwoLayerRequestArgs, GetRequestArgs, ExtraParamsIsValid, _add_argument, \
        field_inputs_wrap_head

from .gallery_valid import field_inputs, resource_fields, resource_fields_wrap,\
        resource_fields_post, field_inputs_wrap
from .__init__ import \
        __pic_head__ as __head__, \
        __pic_heads__ as __heads__

from module.customer.model import CustomerBusinessPics as obj, \
        CustomerBusinesses as business

logger = _logging.getLogger(__name__)
PIC_PREFIX = settings.PIC_PREFIX
STATIC_ROOT = settings.STATIC_ROOT
REST_PIC_PREFIX = settings.REST_PIC_PREFIX
MAXWIDTH = settings.MAXWIDTH
PIC_ALLOWED_TYPE = settings.PIC_ALLOWED_TYPE

# our dir structure is just like: module/{modulename}/feature
moduleName = os.path.dirname(__file__).rsplit(os.path.sep, 1)[1]
limit = platform_model_config[moduleName]['gallery']
max = limit['max']

class PicGallery(Resource):
    """
    """

    def __init__(self):
        request.dataDictWrap = dict((col, request.args.get(col)) for col in request.args)
        if request.dataDictWrap:
            _add_argument(reqparse, field_inputs_wrap, location=['dataDictWrap'])

        super(PicGallery, self).__init__()

        pass

    # For a given file, return whether it's an allowed type or not
    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

    def remove_extend(self, filename):
        return re.sub(r"\..*$","", filename)

    def get(self, id):
        """Get all data, getall
        """
        """get pics by business id

        @api {get} /rest/pic/gallery/:id get pictures list with business id
        @apiVersion 0.0.5
        @apiName ListPicsUnderBusiness
        @apiGroup business
        @apiPermission registered user


        @apiDescription
        todo certificate with cookies / oauth 2.0<br />
        todo long/lat validation<br />
        todo metadata for counter of registerd devices<br />
        todo error / success return code in api

        @apiParam {Number} id business id
        @apiExample {curl} Example usage:
        curl -X GET -H "mTag: xx" -H "Content-Type:application/json" http://localhost/rest/pic/gallery/1
        {  
            "orderBy":"id",
            "itemsPerPage":25,
            "subtype":"gallery",
            "desc":0,
            "data":[  
                {  
                    "path":"/img/customer/1/BYTPH2_20160618_6615.jpg",
                    "id":5,
                    "width":1024,
                    "height":1365
                },
                {  
                    "path":"/img/customer/1/ZS0LII_10473.jpg",
                    "id":6,
                    "width":1024,
                    "height":1365
                },
                {  
                    "path":"/img/customer/1/G30SLL_20160618_6615.jpg",
                    "id":9,
                    "width":1024,
                    "height":1365
                }
            ],
            "type":"pic",
            "total":3,
            "page":1
        }

        @apiSuccess {Number}   total         total items in one business 
        @apiSuccess {String}   orderBy       the items order by column you specified
        @apiSuccess {Number}   page          page you want to request from, start with 1
        @apiSuccess {Number}   itemsPerPage  items for each request
        @apiSuccess {String}   type          request's type
        @apiSuccess {String}   subtype       request's subtype

        @apiSuccess {Object[]}   data       object

        @apiSuccess {Number}     data.id    image's id
        @apiSuccess {Number}     data.path  image's url that you could directly access
        @apiSuccess {Number}     data.height image's height(px)
        @apiSuccess {Number}     data.width image's width(px)
        """

        # check the request is validtion,
        # ex: we not allow request arg 'itemsPerPage1'

        validSet = set(field_inputs_wrap.keys())
        requestArgsSet = set(request.dataDictWrap.keys())

        if not ExtraParamsIsValid(requestArgsSet, validSet):
            return omitError(ErrorMsg=repr(requestArgsSet.difference(validSet))), 400

        # one to many
        # 1. parsing reqest
        try:
            for k, v in field_inputs.items():
                field_inputs[k]['required'] = False

            orgArgs, self.args = GetRequestArgs(None, field_inputs_wrap,
                    dict((col, request.args.get(col)) for col in request.args))
            # get default value
            # print(self.args, 'self.args', resource_fields_wrap)
            self.response = dict(marshal(self.args, resource_fields_wrap).items())

            self.args[__heads__] = []
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            #return omitError(ErrorMsg=repr(error)), 400
            return omitError('CE_INVALID_PARAM', 'not found'), 400

        itemsPerPage = self.response['itemsPerPage']
        page = self.response['page']
        orderBy = getattr(obj, self.response['orderBy'])
        isDesc = getattr(orderBy, 'desc' if self.response['desc'] else 'asc')

        # FIXME: use mapping table
        r = obj.query.filter(obj.type == 3, obj.business_id == id, obj.isdel == False).order_by(isDesc())
        _r = r.all()
        self.args['total'] = len(_r)

        if itemsPerPage is not 0:
            _r = r.offset(itemsPerPage * (page-1))\
                    .limit(itemsPerPage)\
                    .all()

        r = _r
        # 2. export to user
        self.args[field_inputs_wrap_head] = []
        for _r in r:
            __r = dict((col, getattr(_r, col)) for col in _r.__table__.columns.keys())

            # FIXME: use mapping table
            if __r['type'] == 3:
                rest_pic_prefix = os.path.join(REST_PIC_PREFIX, 'customer', str(__r['business_id']))
                __r['path'] = os.path.join(rest_pic_prefix, __r['path'])
                self.args[field_inputs_wrap_head].append(__r)


        _resource_fields_wrap = resource_fields_wrap.copy()
        _resource_fields_wrap.pop('gallery_nr', None)
        _resource_fields_wrap[field_inputs_wrap_head] = fields.List(fields.Nested(resource_fields_post))

        self.args['type'] = "pic"
        self.args['subtype'] = "gallery"

        return marshal(self.args, _resource_fields_wrap), 200


    def post(self):
        """upload pics to business

        @api {post} /rest/pic/gallery upload multiple pictures to business
        @apiVersion 0.0.5
        @apiName UploadPicsToBusiness
        @apiGroup business
        @apiPermission registered user


        @apiDescription
        todo certificate with cookies / oauth 2.0<br />
        todo long/lat validation<br />
        todo metadata for counter of registerd devices<br />
        todo error / success return code in api

        @apiHeader {String}         file[]      upload file path 
        @apiHeader {Number}         business_id upload to business
        @apiHeader {String={customer}}         type      upload type
        @apiExample {curl} Example usage:
        curl -v -i -X POST -H "Content-Type: multipart/form-data" -F "file[]=@20160618_6615.jpg" -F "business_id=1" -F type="customer" -F "file[]=@10473.jpg" http://localhost/rest/pic/gallery

        {  
            "type":"pic",
            "data":[  
                {  
                    "id":9,
                    "path":"/img/customer/1/G30SLL_20160618_6615.jpg",
                    "height":1365,
                    "width":1024
                },
                {  
                    "id":10,
                    "path":"/img/customer/1/3AZGA4_10473.jpg",
                    "height":1365,
                    "width":1024
                }
            ],
            "page":1,
            "subtype":"gallery",
            "gallery_nr":2,
            "total":6
        }

        @apiSuccess {Number}   total         total items in one business 
        @apiSuccess {String}   orderBy       the items order by column you specified
        @apiSuccess {Number}   page          page you want to request from, start with 1
        @apiSuccess {Number}   gallery_nr    current upload files number
        @apiSuccess {String}   type          request's type
        @apiSuccess {String}   subtype       request's subtype

        @apiSuccess {Object[]}   data       object

        @apiSuccess {Number}     data.id    image's id
        @apiSuccess {Number}     data.path  image's url that you could directly access
        @apiSuccess {Number}     data.height image's height(px)
        @apiSuccess {Number}     data.width image's width(px)
        """


        try:
            orgArgs, self.args = GetTwoLayerRequestArgs(None, field_inputs, request.form)
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            return omitError('CE_INVALID_PARAM', 'not found'), 400

        id = self.args['business_id']
        type = self.args['type']
        #print(self.args, 'self.args', id, type)
        #self.args = {}
        #id = request.form.get('business_id')
        #type = request.form.get('type')

        #if type not in PIC_ALLOWED_TYPE:
        #    logger.debug('%s not in PIC_ALLOWED_TYPE', type)
        #    type = None

        #if not id or not type:
        #    return omitError('CE_INVALID_PARAM', 'id {} not found'.format(id)), 400

        print("galleryed_files", request.files, "form data=", request.form)

        # 1. check id exist
        r = business.query.filter(business.id == id, business.isdel == False).scalar()

        if r is None:
            return omitError('CE_NOT_EXIST', 'id {} not found'.format(id)), 400

        # if dir not exist, create it
        # /img/business/1/
        pic_dir = os.path.join(STATIC_ROOT, PIC_PREFIX, type, str(id))
        rest_pic_prefix = os.path.join(REST_PIC_PREFIX, type, str(id))

        if not os.path.exists(pic_dir):
            os.makedirs(pic_dir)

        # TODO: review trigger time
        # 2. check last status that records are same with local
        _pics = []
        count = 0
        filenames = next(os.walk(pic_dir))[2]
        _filenames = filenames.copy()
        print("filenames=", _filenames)
        ps = obj.query.filter(obj.business_id == id).all()
        for v in ps:
            #print("filenames=", filenames, "v.path=", v.path)
            if v.path in filenames:
                count += 1
                _filenames.remove(v.path)
            else:
                # prepare remove
                _pics.append(v)

        # TODO: need check duplicate record?
        # 2.1. commit to delete not relationship records
        try:
            for v in _pics:
                db.session.delete(v)

            db.session.flush()
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.warning('session commit error(%s)', error)

            return omitError(ErrorMsg=repr(error)), 400

        # remove not exist db's file
        for v in _filenames:
            os.remove(os.path.join(pic_dir, v))


        # 3. validate follows spec
        if count > max:
            return omitError('CE_EXCEED_LIMIT', 'limit is {}'.format(max)), 400

        # 4. check pic name 
        _pics = []
        filenames = []
        galleryed_files = request.files.getlist("file[]")
        print("galleryed_files file[]= ", galleryed_files)

        if len(galleryed_files) == 0:
            galleryed_files = request.files.getlist("customer") # for ios
            print("galleryed_files customer= ", galleryed_files)

        for file in galleryed_files:
            # Check if the file is one of the allowed types/extensions
            if file and self.allowed_file(file.filename):
                # Make the filename safe, remove unsupported chars
                filename = secure_filename(file.filename)
                print("file.filename=",  file.filename, "filename=", filename)
                # Move the file form the temporal folder to the gallery
                # folder we setup
                p = obj()
                rs = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
                # 5FATMM_35e4183b.jpg.png -> 5FATMM_35e4183b.png
                extend = os.path.splitext(filename)[1]
                #print("self.remove_extend(filename)=", self.remove_extend(filename))
                p.path = '_'.join([rs, self.remove_extend(filename)]) + extend
                p.business_id = id
                # (1, 'icon'), (2, 'bg'), (3, 'gallery')
                p.type = 3

                _pics.append(p)
                filenames.append(filename)

        # 4. move to pic dir
        # FIXME: check file exist if abnormal error that db record save but pic not exist 
        self.args[field_inputs_wrap_head] = []
        path = []
        _filenames = []
        for k, v in enumerate(_pics):
            filename = os.path.join(pic_dir, filenames[k])
            n_filename = os.path.join(pic_dir, v.path)

            try:
                # FIXME: handle <FileStorage: '35e4183b.jpg.png' ('application/octet-stream')>)
                galleryed_files[k].save(filename)
                #import shutil
                #shutil.copy(filename, n_filename)
                os.rename(filename, n_filename)
                _filenames.append(n_filename)

                print("n_filename = ", n_filename, "filename=", filename)
                img = Image.open(n_filename)
                s = img.size; 
                ratio = 0
                v.width = s[0]
                v.height = s[1]
                if s[0] > MAXWIDTH:
                    ratio = MAXWIDTH/s[0]; 
                    v.width = MAXWIDTH
                    v.height = int(round(s[1]*ratio))
                    img.thumbnail((v.width, v.height), Image.ANTIALIAS)
                print("img = ", img, "n_filenam=", n_filename, "format:", img.format,
                        "width:", MAXWIDTH, ", height: ", int(round(s[1]*ratio)),
                        "orgsize:", s)
                #img.save(n_filename, img.format)
                # FIXME: open 35e4183b.jpg.png error
                img.save(n_filename)

            except IOError:
                #for v in _filenames:
                #    os.remove(v)

                return omitError('CE_IMAGE_RESIZE', 'image resize {} error'.format(filenames[k])), 400



        # 5. commit to save
        try:
            for v in _pics:
                db.session.add(v)

            db.session.flush()
            db.session.refresh(r)

            for v in _pics:
                _pic = dict((col, getattr(v, col)) for col in v.__table__.columns.keys())
                print("_pic:", _pic)
                _pic['path'] =  os.path.join(rest_pic_prefix, v.path)
                self.args[field_inputs_wrap_head].append(_pic)


            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.warning('session commit error(%s)', error)

            return omitError(ErrorMsg=repr(error)), 400



        #output = {"type": "pic", "subtype": "gallery", 
        #        "imgs": {"total": count, "gallery_nr": len(_pics), "path": (path)}} 

        for v in ['itemsPerPage', 'desc', 'orderBy']:
            resource_fields_wrap.pop(v, None)

        _resource_fields = {}
        resource_fields_wrap[field_inputs_wrap_head] = fields.List(fields.Nested(resource_fields_post))

        self.args['total'] = len(obj.query.filter(obj.business_id == id, obj.isdel == False).all())
        self.args['gallery_nr'] = len(_pics)
        self.args['type'] = "pic"
        self.args['subtype'] = "gallery"
        return marshal(self.args, resource_fields_wrap), 200

    def delete(self):
        """multi delete
        """
        """delete images 

        @api {delete} /rest/pic/gallery delete image with ids
        @apiVersion 0.0.5
        @apiName DeleteImages
        @apiGroup business
        @apiPermission registered user

        @apiDescription
        todo certificate with cookies / oauth 2.0<br />
        todo long/lat validation<br />
        todo metadata for counter of registerd devices<br />
        todo error / success return code in api

        @apiParam {Number} pics pics's id
        @apiParam {String={customer}} type      upload type

        @apiDescription
        todo certificate with cookies / oauth 2.0<br />
        todo long/lat validation<br />
        todo metadata for counter of registerd devices<br />
        todo error / success return code in api

        @apiExample {curl} Example usage:

        curl -X DELETE -H "mTag: xx" -H "Content-Type:application/json" http://localhost/rest/pic/gallery?pics=7,8&type=customer
        """



        try:
            ids = request.args.get(__heads__).split(',')
        except Exception as error:
            return omitError(ErrorMsg='param `{}` not found'.format(__heads__)), 400

        type = request.args.get('type')
        if type not in PIC_ALLOWED_TYPE:
            logger.debug('%s not in PIC_ALLOWED_TYPE', type)
            type = None

        if not type:
            return omitError('CE_INVALID_PARAM', 'not found'), 400


        for id in ids:
            try:
                id = inputs.natural(id)
            except Exception as error:
                return omitError(ErrorMsg='id `{}` not int'.format(id)), 400

            # it could als cascade delete `online` user
            r = obj.query.filter(obj.id == id, obj.isdel == False).scalar()
            if r is None:
                return omitError('CE_NOT_EXIST',
                        'id {} not found'.format(id)), 400

        _r = []
        _filenames = []
        for id in ids:
            id = inputs.natural(id)

            # it could als cascade delete `online` user
            r = obj.query.filter(obj.id == id, obj.isdel == False).scalar()
            _r.append(r)
            pic_path = os.path.join(STATIC_ROOT, PIC_PREFIX, type, str(r.business_id), r.path)
            _filenames.append(pic_path)


        try:
            for v in _r:
                db.session.delete(v)

            db.session.flush()
            db.session.commit()
        except Exception as error:
            logger.warning('session commit error(%s)', error)
            db.session.rollback()
            return omitError(ErrorMsg=repr(error)), 400

        for v in _filenames:
            try:
                os.remove(v)
            except OSError:
                pass

        return '', 204
