#!/bin/sh
set -e

ARCH=$(uname -m)
case $ARCH in
  i386 ) ;;
  x86_64 ) ;;
  i586 )
    ARCH=i386 ;;
  i686 )
    ARCH=i386 ;;
  amd64 )
    ARCH=x86_64 ;;
  armv6l )
    ARCH=armv6l ;;
  armv6hl )
    ARCH=armv6l ;;
  * )
    echo "We are very sorry but only i386, x86_64 and armv6l architectures are supported as of now."
    exit 1 ;;
esac

if [ "$1" = "beta" ]; then
    MEOCLOUD_CLIENT_URL="https://meocloud.pt/binaries/linux/$ARCH/meocloud-latest_${ARCH}_beta.tar.gz"
else
    MEOCLOUD_CLIENT_URL="https://meocloud.pt/binaries/linux/$ARCH/meocloud-latest_$ARCH.tar.gz"
fi

if command -v curl >/dev/null 2>&1; then
  URL_FETCHER_COMMAND='curl -f'
else
  URL_FETCHER_COMMAND='wget -O-'
fi

echo "This script requires superuser access to install meocloud."
echo "You will be prompted for your password by sudo."

# clear any previous sudo permission
sudo -k

# attempt to uninstall previous version
sudo rm -rf /opt/meocloud
sudo rm -f /usr/bin/meocloud

$URL_FETCHER_COMMAND $MEOCLOUD_CLIENT_URL | sudo tar xz -C / --no-overwrite-dir

echo "Installation complete"
