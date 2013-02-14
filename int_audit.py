import subprocess
import threading
import re
import Queue
import time
 
def get_db_list(): # get a list of delayed slaves
    dblist = []
    p = subprocess.Popen(['/home/kksiazek/palominodb/scripts/show_nodes_in_cluster.sh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    x = re.compile(".*,(db.*)", re.MULTILINE)
    m = x.match(out)

    for line in out.split('\n'):
        if line.strip() != '':
            dblist.append(line.split(',')[3])
            
    return dblist


queue = Queue.Queue() # initialize queue
out_queue = Queue.Queue()


class Threads(threading.Thread): # Threads class that will be used to handle threads.
    def __init__(self, queue, threadid, limit): # we're passing queue object, threadid (to differentiant the output of multiple threads) and limit to pass to pdb-check-maxvalue 
        threading.Thread.__init__(self)
        self.queue = queue
        self.threadid = threadid
        self.limit = limit

    def run(self): # what thread does
        output = [] # array that will be used to store output for current thread
        while True:
            dic = {} # dictionary, where we'll put hostname:output_from_pdb-check-maxvalue.sh values

            host = self.queue.get() # getting the job from the queue (we're puting hostnames there)
            #print self.threadid
            
            p = subprocess.Popen(['/home/kksiazek/git/dba/pdb-check-maxvalue.sh', '-b', '10250', '-m', '-s', str(self.limit), '-i', host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate() # get the output of subprocess
            dic[host] = out # and store it n the dictionary as a value for key, which is current host.
            output.append(dic) # add dictionary to output array
            threadoutput[self.threadid] = output # add array to global threadoutput array. This should be done in a different way (after thread finish all it's jobs), but it works
            self.queue.task_done() # signal that task is done for this thread
#        threadoutput[self.threadid] = output # this doesn't work and I'm not willing to spend more time trying to find why
 
if __name__ == '__main__': 
    dblist = get_db_list() # get a db list
    dblist = ['db38', 'db42'] # temporary
    limit = 2 # limit for pdb-check-maxvalue.sh, this will be rewritten as a parameter
    threadoutput = [] 
    start = time.time() # temporary, calculating time needed to accomplish all tasks

    for i in range(5): # create (x) threads
        threadoutput.append(''); # initialize threadoutput array
        t = Threads(queue, i, limit) # launch thread
        t.setDaemon(True)
        t.start() # start thread

    for host in dblist: # initialize queue
        queue.put(host)

    queue.join() # wait till queue is empty
    print "Elapsed Time: %s" % (time.time() - start)

    for arr in threadoutput: # print the output from threadoutput array
        if (len(arr) > 0): # if thread array is not empty
            for hsh in arr: # for each task array in the thread array
                #print hsh
                for k, v in hsh.iteritems(): # print key - value pair
                    print k # print key (host name)
                    for line in v.split('\n'):
                        if ("Progress" not in line or "problem" in line): # unless that's like with "Progress", but it there's "problem" in it, print it anyway.
                            print line
            
