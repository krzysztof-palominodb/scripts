#!/bin/bash

limit=$1
i=0

# comma separadet list of emails
emails='krzysztof@palominodb.com, krzysztof@ksiazek.info'

if [ -e check.out ] ; then rm check.out ; fi # delete output file in case it exist

#~/dba/pdb-check-maxvalue.sh -s $limit -i db31 


for db in `echo "db38 db42"`
#for db in `~/palominodb/scripts/show_nodes_in_cluster.sh | awk -F, '{print $4}'`
do
  echo -e "\n${db}" >> check.out
  ~/dba/pdb-check-maxvalue.sh -b 10250 -s $limit -i $db >> check.out 2>&1
  let i++ # checking how many hosts we have in loop. There will be the same number of lines with host names in the output file
done

#cat check.out | grep -v Progress
count=`grep -v Progress check.out | grep -v '^$' | wc -l`


if (( count > i  )) # if we have more lines than number of hosts in the loop, something was found
then
  (echo -n "Following columns passed ${1}% mark on following hosts:"; cat check.out | grep -v Progress) | mail -s "Integer audit report" ${emails}
fi
# If above won't fire, we assune that nothing has been found
i
if [ -e check.out ] ; then rm check.out ; fi # clean after ourselves

