#!/bin/sh
set -e

if command -v curl >/dev/null 2>&1; then
  URL_FETCHER_COMMAND='curl'
else
  URL_FETCHER_COMMAND='wget -O-'
fi

echo "This script requires superuser access to install meocloud's rpm package using yum."
echo "You will be prompted for your password by sudo."

# clear any previous sudo permission
sudo -k

# add sapo repository to yum
sudo sh -c "$URL_FETCHER_COMMAND http://repos.sapo.pt/rpm/sapo.repo > /etc/yum.repos.d/sapo.repo"

# verify and install sapo repository's GPG key for package verification
TMPKEY=`mktemp`
$URL_FETCHER_COMMAND http://repos.sapo.pt/rpm/gpg-key-sapo-packages > $TMPKEY
if echo "4d74575c6d07ba9b72776f421b2d2318  $TMPKEY" | md5sum -c --status -
then
    sudo rpm --import $TMPKEY
    rm $TMPKEY

    # install the meocloud
    sudo yum install meocloud -y
else
    echo "ERROR: failed to verify integrity of the repository's GPG key!"
    echo "Please try again, and if it does not work, please contact the support at http://ajuda.cld.pt/"
fi
