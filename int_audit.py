import subprocess
import threading
import re
import Queue
import time
import sys
from optparse import OptionParser


def parse_args():
    parser = OptionParser()
    parser.add_option("-l", "--limit", dest="limit", default=1, help="Script will return columns with usage over this limit")
    parser.add_option("-d", "--host", dest="host", default="all", help="Script will check given hosts only - coma separated list (default - all)")
    parser.add_option("-r", "--row-count-max-ratio", dest="ratio", default=50, help="If table row count is less than this value, exclude this column from display.")
    parser.add_option("-m", "--display-row-count-max-ratio-columns", dest="display", default="no", help="In separate section, display columns containing high values compared to maximum for the column datatype, but number of rows is less than the value of --row-count-max-ratio.")
    (options, args) = parser.parse_args()
    return options

def get_db_list(): # get a list of delayed slaves
    dblist = []
    p = subprocess.Popen(['/home/kksiazek/palominodb/scripts/show_nodes_in_cluster.sh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate() # need to add error handling

    for line in out.split('\n'):
        if line.strip() != '':
            dblist.append(line.split(',')[3])

    return dblist


queue = Queue.Queue() # initialize queue
out_queue = Queue.Queue()


class outThread(threading.Thread): # Thread for processing the output queue
    def __init__(self, outq):
        threading.Thread.__init__(self)
        self.queue = outq

    def run(self):
        while True:
            out = self.queue.get() # get the output
            print out
            self.queue.task_done() # signal that task is done for this thread


class Threads(threading.Thread): # Threads class that will be used to handle threads.
    def __init__(self, queue, threadid, limit, ratio, display, outq): # we're passing queue object, threadid (to differentiant the output of multiple threads) and limit to pass to pdb-check-maxvalue
        threading.Thread.__init__(self)
        self.queue = queue
        self.threadid = threadid
        self.limit = limit
        self.ratio = ratio
        self.display = display
        self.outq = outq

    def run(self): # what thread does
        output = [] # array that will be used to store output for current thread
        while True:
            endout = ''
            dic = {} # dictionary, where we'll put hostname:output_from_pdb-check-maxvalue.sh values

            host = self.queue.get() # getting the job from the queue (we're puting hostnames there)

            if ( self.display == "yes" ):

                p = subprocess.Popen(['/home/kksiazek/scripts/pdb_check_maxvalue.py', '-T', '4', '-t', '10', '-i', 'information_schema,mysql', '--config', '/home/kksiazek/scripts/pdbchkmaxv.cfg', '--row-count-max-ratio', str(self.ratio), '--display-row-count-max-ratio-columns', '-c', str(self.limit), '-H', host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                p = subprocess.Popen(['/home/kksiazek/scripts/pdb_check_maxvalue.py', '-T', '4', '-t', '10', '-i', 'information_schema,mysql', '--config', '/home/kksiazek/scripts/pdbchkmaxv.cfg', '--row-count-max-ratio', str(self.ratio), '-c', str(self.limit), '-H', host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while True:
                out = p.stdout.readline() # read one line of output
                endout = endout+out # add line by line to the thread output that we'll send further
                if out == '' and p.poll() != None:
                    break
                if out != '':
                    self.outq.put("Thread for host "+host+": "+out.rstrip()) # send the line of output to the logging queue, strip it from whitespaces


            dic[host] = endout # and store it n the dictionary as a value for key, which is current host.
            output.append(dic) # add dictionary to output array
            threadoutput[self.threadid] = output # add array to global threadoutput array. This should be done in a different way (after thread finish all it's jobs), but it works
            self.queue.task_done() # signal that task is done for this thread

def sort_output(input_arr):
    block_crit = 0
    block_display_row_count = 0
    crit_list = []
    display_row_count_list = []
    for line in input_arr:
        if ("CRIT:" in line):
            block_crit = 1
            block_display_row_count = 0
        if ("Columns containing high values compared to maximum for the column datatype" in line):
            block_crit = 0
            block_display_row_count = 1

        if ( block_crit == 1 ):
            crit_list.append(line)
        if ( block_display_row_count == 1 ):
            display_row_count_list.append(line)


    output_sorted = []
    if (len(crit_list) > 0):
        output_sorted.append(crit_list[0])
        for line in sorted(crit_list[1:]):
            output_sorted.append(line)
        output_sorted.append('\n')

    if (len(display_row_count_list) > 0):
        output_sorted.append(display_row_count_list[0])
        for line in sorted(display_row_count_list[1:]):
            output_sorted.append(line)
        output_sorted.append('\n')
    return output_sorted

if __name__ == '__main__':

    options=parse_args()
    dblist = filter(None, options.host.split(',')) # parse --host arguments

    if (dblist[0] == 'all'): # if host is set to all (i.e. by default, get the list of hosts
        dblist = get_db_list() # get a db list

    limit = options.limit # limit for pdb-check-maxvalue.sh, this will be rewritten as a parameter
    threadoutput = []
    start = time.time() # temporary, calculating time needed to accomplish all tasks

    outtrd = outThread(out_queue) # create output thread
    outtrd.setDaemon(True)
    outtrd.start() # start it

    for i in range(16): # create (x) threads
        threadoutput.append(''); # initialize threadoutput array
        t = Threads(queue, i, options.limit, options.ratio, options.display, out_queue) # launch thread
        t.setDaemon(True)
        t.start() # start thread

    for host in dblist: # initialize queue
        queue.put(host)

    queue.join() # wait till queue is empty
    print "Elapsed Time: %s" % (time.time() - start)

    output = []
    tempout = []
    dic = {}
    for arr in threadoutput: # print the output from threadoutput array
        if (len(arr) > 0): # if thread array is not empty
            for hsh in arr: # for each task array in the thread array
                for k, v in hsh.iteritems(): # print key - value pair
                    tempout = []

                    for line in v.split('\n'):
                        if ("now processing" not in line):
                            if ("Thread for host" not in line):
                                if ("Thread #" not in line): # unless that's like with "Progress", but it there's "problem" in it, print it anyway.
                                    tempout.append(line)
                    dic[k] = tempout
    output.append(dic)

    time.sleep(10)
    
    output_sorted = ['Threshold was set to '+str(limit)+'%']
    output_sorted.append('row-count-max-ratio was set to '+str(options.ratio)+'%')

    for dic in output:
        for k, v in dic.iteritems():
            output_sorted.append(k)
            output_sorted.append('\n')
            for line in sort_output(v):
                output_sorted.append(line)







    print "============SENDING EMAIL========="
    print '\n'.join(output_sorted)
    p = subprocess.Popen(["/bin/mail", "-s", "Integer Overflow Report", "krzysztof@palominodb.com"], stdin=subprocess.PIPE)
    p.communicate('\n'.join(output_sorted))
