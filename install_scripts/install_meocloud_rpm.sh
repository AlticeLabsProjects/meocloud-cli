#!/bin/sh
echo "This script requires superuser access to install MEO Cloud's rpm package using yum."
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

    # add sapo repository to yum
    retry $URL_FETCHER_COMMAND http://repos.sapo.pt/rpm/sapo.repo > /etc/yum.repos.d/sapo.repo
    if [ "$1" = "beta" ]; then
        retry sed -i 's/enabled=0/enabled=1/g' /etc/yum.repos.d/sapo.repo
    fi

    # verify and install sapo repository's GPG key for package verification
    TMPKEY=`mktemp`
    retry $URL_FETCHER_COMMAND http://repos.sapo.pt/rpm/gpg-key-sapo-packages > $TMPKEY
    if echo "4d74575c6d07ba9b72776f421b2d2318  $TMPKEY" | md5sum -c --status -
    then
        retry rpm --import $TMPKEY
        rm $TMPKEY

        # install the meocloud
        retry yum install meocloud -y
    else
        echo "ERROR: failed to verify integrity of the repository's GPG key!"
        echo "Please try again, and if it still does not work, please contact the support at https://meocloud.pt/help/"
    fi

    echo
    echo "MEO Cloud has finished installing. You can now run 'meocloud start' to start it."
SCRIPT
