#!/bin/sh
set -e

if command -v curl >/dev/null 2>&1; then
  URL_FETCHER_COMMAND='curl'
else
  URL_FETCHER_COMMAND='wget -O-'
fi

echo "This script requires superuser access to install meocloud's deb package using apt."
echo "You will be prompted for your password by sudo."

# clear any previous sudo permission
sudo -k

# add sapo repository to apt
sudo sh -c "$URL_FETCHER_COMMAND http://repos.sapo.pt/deb/sapo.list > /etc/apt/sources.list.d/sapo.list"

# verify and install sapo repository's GPG key for package verification
TMPKEY=`mktemp`
$URL_FETCHER_COMMAND http://repos.sapo.pt/deb/gpg-key-sapo-packages > $TMPKEY
if echo "57241f9d1915a5d27a8e8966b37c0554  $TMPKEY" | md5sum -c --status -
then
    sudo apt-key add $TMPKEY
    rm $TMPKEY

    # update your sources
    sudo apt-get update

    # install the meocloud
    sudo apt-get install -y meocloud
else
    echo "ERROR: failed to verify integrity of the repository's GPG key!"
    echo "Please try again, and if it does not work, please contact the support at http://ajuda.cld.pt/"
fi
