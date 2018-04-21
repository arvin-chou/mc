#! /bin/sh
DIR=$(dirname $0)
source ${DIR}/common.sh
URI=/rest/objects/ipaddrs

if [ $# -lt 1 ]
then
  echo "Usage: $0 [getone|getall|put|post|del] id"
  exit
fi

id=$2
COOKIES=`curl -s  -X POST -H "Authentication:ZETA" -H "login:admin" -H "passHash:d864934644cd577757afa824138ae169fd5ecbed" ${TARGET}/rest/admin/login --referer "${TARGET}" | tr '\n' ' ' |  tr '\r' ' '| sed 's/ //g;s/:/=/g; s/,/;/g;s/{"admin"={//g; s/}//g;'`

case "$1" in
"post")
  for i in `seq 1 1 1`
  do
    BODY=$(cat <<'EOF'
    {
      "ipaddr" : {
      "name" : "test-ipaddr-${i}9",
      "type1" : "Single",
      "ipVersion" : "IPv4",
      "addr1" : "1.1.1.1",
      "description" : "xxx"
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
      "ipaddr" : {
      "name" : "test-ipaddr-${i}${id}1001",
      "type" : "Single",
      "ipVersion" : "IPv4",
      "addr1" : "1.1.1.1",
      "description" : "xxx"
    }
  }
EOF
);

    URI=/rest/objects/ipaddr
    curl -i -X PUT -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" ${TARGET}${URI}"/${id}"
  done
  ;;

"getall")

  curl -X GET -v -b $COOKIES -H "Content-Type:application/json" ${TARGET}${URI}
  #curl -X GET -v -b $COOKIES -H "Content-Type:application/json" ${TARGET}${URI}"?pages=1"
  #curl -X GET -v -b $COOKIES -H "Content-Type:application/json" ${TARGET}${URI}"?itemsPerPage=50&page=1&orderBy=name&desc=true"
  ;;
"getone")
  URI=/rest/objects/ipaddr
  curl -X GET -v -b $COOKIES -H "Content-Type:application/json" ${TARGET}${URI}"/${id}"
  ;;
"del")
  curl -X DELETE -v -b $COOKIES -H "Content-Type:application/json" ${TARGET}${URI}"?ipaddrs=${id}"
  ;;
*) echo "not support action"
  ;;
esac
