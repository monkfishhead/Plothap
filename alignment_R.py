from rpy2.robjects.packages import importr


def seqalignment(gapopen, maxiter):
    ape = importr("ape")
    muscle = importr("muscle")
    biostrings = importr("Biostrings")
    mysequences = biostrings.readDNAStringSet("./datafile/alifas.fas")
    alignedsequences = muscle.muscle(mysequences, quiet=True, gapopen=int(gapopen), maxiters=int(maxiter))
    alignedsequences = ape.as_DNAbin(alignedsequences)
    segsites = ape.seg_sites(alignedsequences)
    savefas = ape.write_FASTA(alignedsequences, file="./datafile/aliedfas.fas")

    return segsites

if __name__ == '__main__':
    seqalignment(-400, 16)