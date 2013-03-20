#!/bin/bash

monday=$(python -c "import dateutil.parser; from dateutil.relativedelta import relativedelta; x = dateutil.parser.parse('monday'); y = x + relativedelta(weeks=-1); print y.strftime('%Y-%m-%d')")

if [ "x$1" != "x--trust-me" ]; then
  echo "Running update for $monday, ENTER to confirm"
  read nothing
fi

./weekly-update.py $monday

./weekly-email.py -n $monday
./weekly-blogpost.py $monday
