#! /bin/sh
DIR=$(dirname $0)
source ${DIR}/common.sh
URI=/rest/objects/ipaddrs

#COOKIES=`curl -s  -X POST -H "Authentication:ZETA" -H "login:admin" -H "passHash:d864934644cd577757afa824138ae169fd5ecbed" ${TARGET}/rest/admin/login --referer "${TARGET}" | tr '\n' ' ' |  tr '\r' ' '| sed 's/ //g;s/:/=/g; s/,/;/g;s/{"admin"={//g; s/}//g;'`
#curl -X GET -v -b $COOKIES -H "Content-Type:application/json" ${TARGET}${URI}

for i in `seq 1 1 1`
do
  BODY=$(cat <<'EOF'
  {
    "ipaddr" : {
    "name" : "test-ipaddr-${i}",
    "type" : 1,
    "ipVersion" : 4,
    "addr1" : "1.1.1.1",
    "description" : "xxx"
  }
}
EOF
);

    curl -X POST -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" ${TARGET}${URI}
done
