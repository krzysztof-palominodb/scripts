#!/bin/bash

for db in `~/palominodb/scripts/show_nodes_in_cluster.sh | awk -F, '{print $4}'`
do
  echo $db
done
