from rpy2 import robjects
from rpy2.robjects.packages import importr


def tcs():
    ratio = "8"
    # in:
    # fasfile
    # region information/taxon/sex/....
    # ratio
    # out:
    # 1. table of edge(from, to ,value): firstL
    # 2. coordinate of each nodes: cx,cy
    # 3. group information: R
    r_script = '''
    library(ape) 
    library(pegas)
    library(tidygraph)
    library(ggraph)
    
    fasfile <- read.dna(file="./datafile/fornet.fas",format="fasta")
    
    h <- haplotype(fasfile, labels = NULL, strict = FALSE, trailingGapsAsN = TRUE)  
    g <- haploNet(h)
    
    attr(g,"alter.links") <- NULL
    
    sz <- attr(g,"freq")
    
    link <- g[, 1:2, drop = FALSE]
    l1 <- g[, 1]
    l2 <- g[, 2]
    ld <- g[, 3] * ''' + ratio + '''
    
    tab <- tabulate(link)
    n <- length(tab)
    
    size <- rep(sz, length.out = n)
    ld <- ld + (size[l1] + size[l2])/2
    mld <- max(ld)+1
    layoutw <- (mld- ld)/mld
    
    rownum <- nrow(g)
    firstL <- g[1:rownum,1:3]
    colnames(firstL) <- c("from", "to", "value")
    firstL <- as.data.frame(firstL)
    firstN <- as.data.frame(attr(g,"label"))
    names(firstN)[1] <- "name"

    ggrapht <- tbl_graph(nodes = firstN, edges = firstL)
    t <- ggraph(ggrapht, layout = "fr")
    o <- list(x = t[["data"]][["x"]],y = t[["data"]][["y"]])
    
    regionfile <- read.table("./datafile/group.txt",sep = "\t")
    g.labs <- attr(g, "labels")
    
    region <- regionfile[,2]
    R <- haploFreq(fasfile, fac = region, haplo = h)
    if (ncol(R) == 1){
    groupname <- colnames(R)
    R <- R[g.labs, ]
    R <- as.data.frame(R)
    colnames(R) <- groupname
    }else R <- R[g.labs, ]
    
    country <- regionfile[,1]
    C <- haploFreq(fasfile, fac = country, haplo = h)
    if (ncol(C) == 1){
    groupname <- colnames(C)
    C <- C[g.labs, ]
    C <- as.data.frame(C)
    colnames(C) <- groupname
    }else C <- C[g.labs, ]
    
    world <- regionfile[,3]
    W <- haploFreq(fasfile, fac = world, haplo = h)
    if (ncol(W) == 1){
    groupname <- colnames(W)
    W <- W[g.labs, ]
    W <- as.data.frame(W)
    colnames(W) <- groupname
    }else W <- W[g.labs, ]
    
    taxon <- regionfile[,4]
    T <- haploFreq(fasfile, fac = taxon, haplo = h)
    if (ncol(T) == 1){
    groupname <- colnames(T)
    T <- T[g.labs, ]
    T <- as.data.frame(T)
    colnames(T) <- groupname
    }else T <- T[g.labs, ]
    
    write.table(R,file = "./datafile/network/pie_region.txt", quote = FALSE, sep = "\t", row.names = FALSE)
    write.table(C,file = "./datafile/network/pie_country.txt", quote = FALSE, sep = "\t", row.names = FALSE)
    write.table(W,file = "./datafile/network/pie_world.txt", quote = FALSE, sep = "\t", row.names = FALSE)
    write.table(T,file = "./datafile/network/pie_taxon.txt", quote = FALSE, sep = "\t", row.names = FALSE)
    
    write.table(o,file = "./datafile/network/xy.txt", quote = FALSE, sep = "\t", row.names = FALSE)
    write.table(firstL, file = "./datafile/network/edge.txt", quote = FALSE, sep = "\t", row.names = FALSE)
    write.table(sz, file = "./datafile/network/size.txt", quote = FALSE, sep = "\t", row.names = FALSE, col.names = FALSE)
    '''
    pro = robjects.r(r_script)
    # country, region, world, spices


def msn():
    ratio = "8"
    # in:
    # fasfile
    # region information/taxon/sex/....
    # ratio
    # out:
    # 1. table of edge(from, to ,value): firstL
    # 2. coordinate of each nodes: cx,cy
    # 3. group information: R
    r_script = '''
        library(ape) 
        library(pegas)
        library(tidygraph)
        library(ggraph)

        fasfile <- read.dna(file="./datafile/fornet.fas",format="fasta")

        h <- haplotype(fasfile, labels = NULL, strict = FALSE, trailingGapsAsN = TRUE) 
        d <- dist.dna(h, "N") 
        g <- msn(d)

        attr(g,"alter.links") <- NULL
        
        sz <- summary(h)
        g.labs <- attr(g, "labels")
        sz <- sz[g.labs]
        sz <- as.vector(sz)
        
        link <- g[, 1:2, drop = FALSE]
        l1 <- g[, 1]
        l2 <- g[, 2]
        ld <- g[, 3] * ''' + ratio + '''

        tab <- tabulate(link)
        n <- length(tab)

        size <- rep(sz, length.out = n)
        ld <- ld + (size[l1] + size[l2])/2
        mld <- max(ld)+1
        layoutw <- (mld- ld)/mld

        rownum <- nrow(g)
        firstL <- g[1:rownum,1:3]
        colnames(firstL) <- c("from", "to", "value")
        firstL <- as.data.frame(firstL)
        firstN <- as.data.frame(attr(g,"label"))
        names(firstN)[1] <- "name"

        ggrapht <- tbl_graph(nodes = firstN, edges = firstL)
        t <- ggraph(ggrapht, layout = "fr")
        o <- list(x = t[["data"]][["x"]],y = t[["data"]][["y"]])

        regionfile <- read.table("./datafile/group.txt",sep = "\t")
        g.labs <- attr(g, "labels")

        region <- regionfile[,2]
        R <- haploFreq(fasfile, fac = region, haplo = h)
        if (ncol(R) == 1){
        groupname <- colnames(R)
        R <- R[g.labs, ]
        R <- as.data.frame(R)
        colnames(R) <- groupname
        }else R <- R[g.labs, ]

        country <- regionfile[,1]
        C <- haploFreq(fasfile, fac = country, haplo = h)
        if (ncol(C) == 1){
        groupname <- colnames(C)
        C <- C[g.labs, ]
        C <- as.data.frame(C)
        colnames(C) <- groupname
        }else C <- C[g.labs, ]

        world <- regionfile[,3]
        W <- haploFreq(fasfile, fac = world, haplo = h)
        if (ncol(W) == 1){
        groupname <- colnames(W)
        W <- W[g.labs, ]
        W <- as.data.frame(W)
        colnames(W) <- groupname
        }else W <- W[g.labs, ]

        taxon <- regionfile[,4]
        T <- haploFreq(fasfile, fac = taxon, haplo = h)
        if (ncol(T) == 1){
        groupname <- colnames(T)
        T <- T[g.labs, ]
        T <- as.data.frame(T)
        colnames(T) <- groupname
        }else T <- T[g.labs, ]

        write.table(R,file = "./datafile/network/pie_region.txt", quote = FALSE, sep = "\t", row.names = FALSE)
        write.table(C,file = "./datafile/network/pie_country.txt", quote = FALSE, sep = "\t", row.names = FALSE)
        write.table(W,file = "./datafile/network/pie_world.txt", quote = FALSE, sep = "\t", row.names = FALSE)
        write.table(T,file = "./datafile/network/pie_taxon.txt", quote = FALSE, sep = "\t", row.names = FALSE)

        write.table(o,file = "./datafile/network/xy.txt", quote = FALSE, sep = "\t", row.names = FALSE)
        write.table(firstL, file = "./datafile/network/edge.txt", quote = FALSE, sep = "\t", row.names = FALSE)
        write.table(sz, file = "./datafile/network/size.txt", quote = FALSE, sep = "\t", row.names = FALSE, col.names = FALSE)
        '''
    pro = robjects.r(r_script)
    # country, region, world, spices

if __name__ == '__main__':
    tcs()

