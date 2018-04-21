#! /bin/sh
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
    BODY=$(cat <<'EOF'
    {
      "business" : {
      "description": "Early Bird Special: Get $2 off.",
      "name": "Starbucks Coffee - 1",
      "image_url": "business/icon/1",
      "cat": 1,
      "deal": 200,
      "lat": 120.678469,
      "long": 23.538302
    }
  }
EOF
);

    curl -i -X POST -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" ${TARGET}${URI}
    done
  ;;
"put")
  for i in `seq 1 1 1`
  do
    BODY=$(cat <<'EOF'
    {
      "business" : {
      "description": "Come back john! Get $5 off.",
      "id": 4,
      "name": "台北福華大飯店",
      "image_url": "business/icon/3",
      "cat": 2,
      "deal": 201,
      "lat": 120.4540969,
      "long": 23.4862023
    }
  }
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
