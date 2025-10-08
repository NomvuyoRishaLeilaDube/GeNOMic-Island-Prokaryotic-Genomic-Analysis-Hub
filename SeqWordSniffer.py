import sys, os.path, string, array, math, time, shelve
import sys, os, Tkinter
path = os.getcwd()
sys.path.append(os.path.join(path,"lib"))
import cli
import lib, blast

try:
    import psyco
    psyco.profile()
except:
    pass


###############################################################################

if __name__ == "__main__":
    options = {"-c":"MGE",     # name of the scenario
               "-u":"yes",              # use BLASTN to filter rrn clusters
               "-n":"no",               # use BLASTN to search tRNA on the borders of GI
               "-l":"8000",             # sliding window length
               "-b":"2000",             # sliding window big step
               "-m":"500",              # sliding window medium step
               "-s":"100",              # sliding window small step
               "-e":"Contrasting/Iteration",    # refinement No | Contrasting | Iteration | Contrasting/Iteration 
               "-i":"input",            # input folder
               "-o":"output",           # output folder
               "-f":"fasta",            # save GI sequemces: no | fasta | gbk | gbk+fasta
               "-v":"yes"               # save SVG file
            }
    arguments = sys.argv[1:]
    if arguments:
        for i in range(0,len(arguments)-1,2):
            key = arguments[i]
            if key not in options:
                raise IOError("Unknown argument " + key + "!")
            if i <= len(arguments)-2:
                options[key] = arguments[i+1]
        oInterface = cli.Interface(options)
    else:
        oInterface = cli.Interface()
    
