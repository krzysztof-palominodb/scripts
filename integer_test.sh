#!/bin/bash

replica_name='euprdb01integercheck'
master_name='euprdb01'
rep_available='0'

rds-create-db-instance-read-replica ${replica_name} --source-db-instance-identifier ${master_name} --auto-minor-version-upgrade 0 --availability-zone=eu-west-1c

exitcode=`echo $?`

if [ ${exitcode} -ne 0 ] ; then echo "Error in creating replica: ${exitcode}" ; exit ; fi

while [ "${rep_available}" != "available" ] ; do

    rep_available=`rds-describe-db-instances | grep ${replica_name} | awk '{ if (NF > 2) { if ( ($9 ~ /(available)/)  ) {print "available"} else {print "0"} } }'`
#    echo ${rep_avaliable}
    sleep 30
done

echo "${replica_name} should be ready"

/usr/bin/python /home/kksiazek/scripts/int_audit.py -l 30 -m yes -r 10 -d ${replica_name}.cxi6c8uk7ebi.eu-west-1.rds.amazonaws.com

rds-delete-db-instance ${replica_name} --force --skip-final-snapshot
