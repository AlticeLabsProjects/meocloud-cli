#! /bin/bash
set -e

OWN_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $OWN_DIR

EN_TMP_FILE=$(mktemp)
PT_TMP_FILE=$(mktemp)
OUT_FILE="../meocloud/client/linux/strings.py"

python convert_to_native_file.py en.txt $EN_TMP_FILE > /dev/null
python convert_to_native_file.py pt.txt $PT_TMP_FILE > /dev/null

# Clean out file
> $OUT_FILE

echo "NOTIFICATIONS = {" >> $OUT_FILE
echo "    'en': {" >> $OUT_FILE
cat $EN_TMP_FILE >> $OUT_FILE
echo "    }," >> $OUT_FILE
echo "    'pt': {" >> $OUT_FILE
cat $PT_TMP_FILE >> $OUT_FILE
echo "    }," >> $OUT_FILE
echo "}" >> $OUT_FILE

rm $EN_TMP_FILE
rm $PT_TMP_FILE
