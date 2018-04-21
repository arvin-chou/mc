#! /bin/sh
TARGET=http://0.0.0.0:8080
URI=/rest/object/sec
#TARGET=http://192.168.20.166:8080
#URI=/rest/profiles/ip/packages

#COOKIES=`curl -s  -X POST -H "Authentication:ZETA" -H "login:admin" -H "passHash:d864934644cd577757afa824138ae169fd5ecbed" ${TARGET}/rest/admin/login --referer "${TARGET}" | tr '\n' ' ' |  tr '\r' ' '| sed 's/ //g;s/:/=/g; s/,/;/g;s/{"admin"={//g; s/}//g;'`
#curl -X GET -v -b $COOKIES -H "Content-Type:application/json" ${TARGET}${URI}

for i in `seq 1 1 1`
do
#    curl -X POST -b $COOKIES -H "Content-Type:application/json" -d '{"tcpolicy":{"name":"TC policy '${i}'","description":"","enabled":"Enabled","tcprofiles":[{"id":"2"}],"logOnly":"Disabled"}}' http://localhost:8080/rest/policies/tc
#BODY='{ "secpolicy" : { "name" : "test-${i}", "interface" : { "ifName" : "ifname" }, "srcIpGroups" : [ { "id" : 1 } ], "srcIpAddrs" : [ { "id" : 1 } ], "dstIpGroups" : [ { "id" : 1 } ], "dstIpAddrs" : [ { "id" : 1 } ], "vlanGroups" : [ { "id" : 1 } ], "vlans" : [ { "id" : 1 } ], "servGroups" : [ { "id" : 1 } ], "servs" : [ { "id" : 1 } ], "userGroups" : [ { "id" : 1 } ], "schds" : [ { "id" : 1 } ], "ipprofile" : { "id" : 1 }, "ipprofileLogOnly" : "true", "acprofile" : { "id" : 1 }, "acprofileLogOnly" : "true", "scprofile" : { "id" : 1 }, "scprofileLogOnly" : "true", "action" : "Enabled", "logging" : "Enabled", "Enabled" : "Enabled", "description" : "xxx" } }'
  BODY=$(cat <<'EOF'
    {
          "secpolicy" : {
            "name" : "test-${i}",
            
            "srcIpAddrs" : [
            {
              "id" : 1
            }
              ],
            "dstIpGroups" : [
            {
              "id" : 1
            }
              ],
            "dstIpAddrs" : [
            {
              "id" : 1
            }
              ],
            "vlanGroups" : [
            {
              "id" : 1
            }
              ],
            "vlans" : [
            {
              "id" : 1
            }
              ],
            "servGroups" : [
            {
              "id" : 1
            }
              ],
            "servs" : [
            {
              "id" : 1
            }
              ],
            "userGroups" : [
            {
              "id" : 1
            }
              ],
            "schds" : [
            {
              "id" : 1
            }
            ],
              "ipprofile" : {
              "id" : 1
              },
              "ipprofileLogOnly" : "true",
              "acprofile" : {
              "id" : 1
              },
              "acprofileLogOnly" : "true",
              "scprofile" : {
              "id" : 1
              },
              "scprofileLogOnly" : "true",
              "action" : "Enabled",
              "logging" : "Enabled",
              "Enabled" : "Enabled",
              "description" : "xxx"
          }
        }
EOF
);

    curl -X POST -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" ${TARGET}${URI}
done
