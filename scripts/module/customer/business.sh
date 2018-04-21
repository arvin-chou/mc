#! /bin/bash
DIR=$(dirname $0)
source ${DIR}/../../common.sh
URI=/rest/customer/businesses

if [ $# -lt 1 ]
then
  echo "Usage: $0 [getone|getall|put|post|del] id"
  exit
fi

id=$2
COOKIES=`curl -i -s  -X POST -H "Authentication:ZETA" -H "login:admin" -H "passHash:d864934644cd577757afa824138ae169fd5ecbed" ${TARGET}/rest/admin/login --referer "${TARGET}" | tr '\n' ' ' |  tr '\r' ' '| sed 's/ //g;s/:/=/g; s/,/;/g;s/{"admin"={//g; s/}//g;'`

case "$1" in
"post")
  for i in `seq 1 1 1`
  do
    BODY=$(cat <<EOF
{"subtype": "overview", "type": "business", "data": {"deal": 200, "dist": 12245, "deals": [{"title": "10% Off Any Order", "description": "Use this promo code and save on coffee, tea, and..."}], "images_url": {"bg": "/img/business/1/bg", "icon": "/img/business/1/icon"}, "close": "2200", "open": "0600", "name": "Starbucks Coffee $i", "description": "early Bird Special: Get $2 off.", "long": 23.5383, "cat": 1, "lat": 120.678, "meals": "this is meals", "features": "this is features", "address": "this is address"}}
EOF
);

    curl -i -X POST -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" ${TARGET}${URI}
    done
  ;;
"put")
  for i in `seq 1 1 1`
  do
    BODY=$(cat <<EOF
    {"subtype": "overview", "type": "business", "data": {"deal": 200, "dist": 12245, "deals": [{"title": "10% Off Any Order", "description": "Use this promo code and save on coffee, tea, and..."}], "images_url": {"bg": "/img/business/1/bg", "icon": "/img/business/1/icon"}, "close": "2200", "open": "0600", "name": "Starbucks Coffee 30", "description": "early Bird Special: Get  off.", "long": 23.5383, "cat": 1, "lat": 120.678, "meals": "this is meals", "features": "this is features", "address": "this is address"}}
EOF
);

    URI=/rest/customer/business
    curl -i -X PUT -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" ${TARGET}${URI}"/${id}"
  done
  ;;

"getall")

  curl -X GET -v -b $COOKIES -H "Content-Type:application/json" ${TARGET}${URI}
  #curl -X GET -v -b $COOKIES -H "Content-Type:application/json" ${TARGET}${URI}"?pages=1"
  #curl -X GET -v -b $COOKIES -H "Content-Type:application/json" ${TARGET}${URI}"?itemsPerPage=50&page=1&orderBy=name&desc=true"
  ;;
"getone")
  URI=/rest/customer/business
  curl -X GET -v -b $COOKIES -H "Content-Type:application/json" ${TARGET}${URI}"/${id}"
  ;;
"del")
  curl -X DELETE -v -b $COOKIES -H "Content-Type:application/json" ${TARGET}${URI}"?businesses=${id}"
  ;;
*) echo "not support action"
  ;;
esac
