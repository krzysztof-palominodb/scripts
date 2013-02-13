import threadpool
import subprocess
import re
import time #to simulate a long process
 
def long_process(argument): #simulate a long process with args
    print( 'Starting process with argument %d' % argument)
    time.sleep(argument) #do lots of processing using our argument 
    print( 'Ended process with argument %d' % argument)

def get_db_list():
    p = subprocess.Popen(['/home/kksiazek/palominodb/scripts/show_nodes_in_cluster.sh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    print out
    m = re.match(r".*,(db.*).*", out)
    print m.group(0)
 
def process_tasks():
    pool = threadpool.ThreadPool(4)
 
    argument_list = [1, 6, 2, 4, 5, 6, 7, 8]
 
    #let threadpool format your requests into a list
    requests = threadpool.makeRequests(long_process, argument_list)
 
    #insert the requests into the threadpool
    for req in requests:
        pool.putRequest(req) 
 
    #wait for them to finish (or you could go and do something else)
    pool.wait()
 
if __name__ == '__main__': 
#    process_tasks()
    get_db_list()
