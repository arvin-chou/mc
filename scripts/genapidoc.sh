#! /bin/bash
DIR=$(dirname $0)

PACKAGE_PATH=./package.json
PACKAGE=$(cat <<EOF
{
  "name": "mc",
  "version": "0.1.0",
  "description": "mc api doc",
  "apidoc": {
    "name": "mc apidoc",
    "version": "0.0.4",
    "description": "mc project",
    "title": "mc restful api doc",
    "url" : "http://$IP",
    "template": {
      "withCompare": true,
      "withGenerator": true
    }
  }
}
EOF
);
echo $PACKAGE > $PACKAGE_PATH

${DIR}/../node_modules/apidoc/bin/apidoc -c ./ -i module -o www/apidoc
#if [ ! -z $IP ]; then 
#  find www/apidoc -type f -exec sed -i "s/localhost/$IP/g" {} \;
#fi
rm $PACKAGE_PATH

#curl -i http://localhost/apidoc/index.html
