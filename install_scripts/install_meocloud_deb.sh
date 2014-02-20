#!/bin/sh
echo "This script requires superuser access to install MEO Cloud's deb package using apt."
echo "You will be prompted for your password by sudo."

# clear any previous sudo permission
sudo -k

sudo sh -s $* << "SCRIPT"
    retry() {
        n=0
        until [ $n -ge 10 ]
        do
            $@ 2> /dev/null && return
            n=$(($n+1))
            sleep 1
        done
        echo
        echo "An error occurred while installing MEO Cloud!" 1>&2
        echo "Please try again, and if it still does not work, please contact the support at https://meocloud.pt/help/" 1>&2
        exit 1
    }

    if command -v curl >/dev/null 2>&1; then
        URL_FETCHER_COMMAND='curl -f'
    else
        URL_FETCHER_COMMAND='wget -O-'
    fi

    echo "Installing MEO Cloud, please wait..."
    echo

    # add sapo repository to apt
    retry $URL_FETCHER_COMMAND http://repos.sapo.pt/deb/sapo.list > /etc/apt/sources.list.d/sapo.list
    if [ "$1" = "beta" ]; then
        retry sed -i 's/stable/beta/g' /etc/apt/sources.list.d/sapo.list
    fi

    # verify and install sapo repository's GPG key for package verification
    TMPKEY=`mktemp`
    retry $URL_FETCHER_COMMAND http://repos.sapo.pt/deb/gpg-key-sapo-packages > $TMPKEY
    if echo "57241f9d1915a5d27a8e8966b37c0554  $TMPKEY" | md5sum -c --status -
    then
        retry apt-key add $TMPKEY > /dev/null
        rm $TMPKEY

        echo "Updating apt sources..."
        # update your sources
        retry apt-get update -qq

        # install the meocloud
        retry apt-get install -y meocloud
    else
        echo "ERROR: failed to verify integrity of the repository's GPG key!"
        echo "Please try again, and if it still does not work, please contact the support at https://meocloud.pt/help/"
    fi

    echo
    echo "MEO Cloud has finished installing. You can now run 'meocloud start' to start it."
SCRIPT
