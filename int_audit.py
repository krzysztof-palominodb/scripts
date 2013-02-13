import threadpool
import subprocess
import threading
import re
import Queue
import time
 
def get_db_list():
    dblist = []
    p = subprocess.Popen(['/home/kksiazek/palominodb/scripts/show_nodes_in_cluster.sh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    x = re.compile(".*,(db.*)", re.MULTILINE)
    m = x.match(out)

    for line in out.split('\n'):
        if line.strip() != '':
            dblist.append(line.split(',')[3])
            
    return dblist


queue = Queue.Queue()
out_queue = Queue.Queue()


class Threads(threading.Thread):
    def __init__(self, queue, threadid, limit):
        threading.Thread.__init__(self)
        self.queue = queue
        self.threadid = threadid
        self.limit = limit

    def run(self):
        output = []
        dic = {}
        while True:
            host = self.queue.get()
            print self.threadid
            
            p = subprocess.Popen(['/home/kksiazek/dba/pdb-check-maxvalue.sh', '-b', '10250', '-s', str(self.limit), '-i', host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            dic[host] = out
            output.append(dic)
#            print output
            threadoutput[self.threadid] = output
            self.queue.task_done()



#def process_tasks(args):
  #  pool = threadpool.ThreadPool(4)

 
    #let threadpool format your requests into a list
 #   requests = threadpool.makeRequests(long_process, args)
 
    #insert the requests into the threadpool
#    for req in requests:
#        pool.putRequest(req) 
 
#    #wait for them to finish (or you could go and do something else)
#    pool.wait()
 
if __name__ == '__main__': 
#    process_tasks()
    dblist = get_db_list()
    dblist = ['db38', 'db42']
    limit = 2 # limit for pdb-check-maxvalue.sh
    threadoutput = []
    start = time.time()

    for i in range(1):
        threadoutput.append('');
        t = Threads(queue, i, limit)
        t.setDaemon(True)
        t.start()

    for host in dblist:
        queue.put(host)

    queue.join()
    print "Elapsed Time: %s" % (time.time() - start)
#    print threadoutput

    for arr in threadoutput:
        if (len(arr) > 0):
            for hsh in arr:
                #print hsh
                for k, v in hsh.iteritems():
                    print k
                    for line in v.split('\n'):
                        if ("Progress" not in line or "problem" in line):
                            print line
#                    print v
            #for line in arr[1].split('\n'):
                #if ("Progress" not in line or "problem" in line):
                #    print line
            
