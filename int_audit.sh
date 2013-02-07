#!/bin/bash

limit=$1

for db in `~/palominodb/scripts/show_nodes_in_cluster.sh | awk -F, '{print $4}'`
do
  ~/dba/pdb-check-maxvalue.sh -s $limit -i $db
done
