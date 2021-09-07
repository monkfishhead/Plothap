from rpy2.robjects.packages import importr


def seqalignment(gapopen, maxiter):
    ape = importr("ape")
    muscle = importr("muscle")
    biostrings = importr("Biostrings")
    mysequences = biostrings.readDNAStringSet("./datafile/alifas.fas")
    alignedsequences = muscle.muscle(mysequences, quiet=True, gapopen=int(gapopen), maxiters=int(maxiter))
    alignedsequences = ape.as_DNAbin(alignedsequences)
    # segsites = ape.seg_sites(alignedsequences)
    savefas = ape.write_FASTA(alignedsequences, file="./datafile/aliedfas.fas")


def segsites():
    ape = importr("ape")
    biostrings = importr("Biostrings")
    mysequences = biostrings.readDNAStringSet("./datafile/aliedfas.fas")
    alignedsequences = ape.as_DNAbin(mysequences)
    segs = ape.seg_sites(alignedsequences)
    osegpath = "./datafile/segsites.txt"
    osegfile = open(osegpath, "w")
    segs = list(map(str, segs))
    strn = "\n"
    osegfile.write(strn.join(segs))
    osegfile.close()

if __name__ == '__main__':
    seqalignment(-400, 16)