from xml.dom.minidom import parse
from tkinter import filedialog


def is_pt_in_poly(pt, poly):
    nvert = len(poly)
    vertx = []
    verty = []
    testx = pt[0]
    testy = pt[1]
    for item in poly:
        vertx.append(item[0])
        verty.append(item[1])

    j = nvert - 1
    res = False
    for i in range(nvert):
        if (verty[j] - verty[i]) == 0:
            j = i
            continue
        x = (vertx[j] - vertx[i]) * (testy - verty[i]) / (verty[j] - verty[i]) + vertx[i]
        if ((verty[i] > testy) != (verty[j] > testy)) and (testx < x):
            res = not res
        j = i
    return res


def readxml(docname):
    datadic = {}

    geodic = {}
    geo = open("./datafile/geo/coo.txt", "r")
    header = ""
    for line in geo:
        if line.startswith('>'):
            header = line[1:].rstrip('\n')
            geodic.setdefault(header, [])
        elif not line.startswith('#'):
            data = line.rstrip('\n')
            coo = data.split("\t")
            coo[0] = float(coo[0])
            coo[1] = float(coo[1])
            geodic[header].append(coo)
    geo.close()

    doc = parse(docname)
    rootnode = doc.documentElement
    records = rootnode.getElementsByTagName("record")
    for record in records:
        # extract species name (taxonomy-species-taxon-name)
        taxonomy = record.getElementsByTagName("taxonomy")
        if len(taxonomy) != 0:
            species = taxonomy[0].getElementsByTagName("species")
            if len(species) != 0:
                speciesname = species[0].getElementsByTagName("name")
                spe_name = speciesname[0]
                spe_name_out = spe_name.childNodes[0].data
            else:
                genus = taxonomy[0].getElementsByTagName("genus")
                if len(genus) != 0:
                    speciesname = genus[0].getElementsByTagName("name")
                    spe_name = speciesname[0]
                    spe_name_out = spe_name.childNodes[0].data
                else:
                    family = taxonomy[0].getElementsByTagName("family")
                    if len(family) != 0:
                        speciesname = family[0].getElementsByTagName("name")
                        spe_name = speciesname[0]
                        spe_name_out = spe_name.childNodes[0].data
                    else:
                        order = taxonomy[0].getElementsByTagName("order")
                        if len(order) != 0:
                            speciesname = order[0].getElementsByTagName("name")
                            spe_name = speciesname[0]
                            spe_name_out = spe_name.childNodes[0].data
                        else:
                            spe_name_out = "Unknown species"
        else:
            spe_name_out = "Unknown species"

        # extract sex
        sex = record.getElementsByTagName("sex")
        if len(sex) != 0:
            if len(sex[0].childNodes) != 0:
                sexin = sex[0].childNodes[0].data
            else:
                sexin = "Unknown"
        else:
            sexin = "Unknown"

        # extract geographic sites
        country = record.getElementsByTagName("country")
        if len(country) != 0:
            if len(country[0].childNodes) != 0:
                countryin = country[0].childNodes[0].data
            else:
                countryin = "Unknown"
        else:
            countryin = "Unknown"

        # extract identification information
        # provider
        iden1 = record.getElementsByTagName("identification_provided_by")
        if len(iden1) != 0:
            if len(iden1[0].childNodes) != 0:
                iden_provider = iden1[0].childNodes[0].data
            else:
                iden_provider = "Unknown"
        else:
            iden_provider = "Unknown"

        # coordinates
        lat = record.getElementsByTagName("lat")
        lon = record.getElementsByTagName("lon")
        georegion = ""
        if len(lat) != 0:
            if len(lat[0].childNodes) != 0:
                coo_lat = lat[0].childNodes[0].data
                coo_lon = lon[0].childNodes[0].data
                textp = [float(coo_lat), float(coo_lon)]

                # get new world/old world
                if textp[1] < -25:
                    world = "New world"
                else:
                    world = "Old world"

                for region, coordinates in geodic.items():
                    # get geo region
                    if is_pt_in_poly(textp, coordinates):
                        georegion = region
                if georegion == "":
                    georegion = "Others"
            else:
                georegion = "Unknown"
                world = "Unknown"
        else:
            georegion = "Unknown"
            world = "Unknown"

        # extract sequence
        seqindex = record.getElementsByTagName("nucleotides")
        seq = seqindex[0].childNodes[0].data

        # extract process id
        idindex = record.getElementsByTagName("processid")
        processid = idindex[0].childNodes[0].data

        # store information in dic
        datadic.setdefault(processid, [])
        datadic[processid].extend([seq, spe_name_out, countryin, sexin, iden_provider, georegion, world])

    return datadic


def readfasta(docname):
    faspath = docname
    fasfile = open(faspath, 'r')
    datadic = {}

    # Read data to create a dictionary(id:[seq, spe_name_out, countryin, sexin, iden_provider, georegion, world]).
    iid = ""
    species = ""
    country = ""
    sex = ""
    provider = ""
    georegion = ""
    world = ""
    for iline in fasfile:
        if iline.startswith('>'):
            # extract header name
            header = iline[1:].rstrip('\n')
            content = header.split("|")
            iid = content[0]
            species = content[1]
            country = content[2]
            sex = content[3]
            provider = content[4]
            georegion = content[5]
            world = content[6]
            datadic.setdefault(iid, [])
        else:
            seq = iline.rstrip("\n")
            datadic[iid].extend([seq, species, country, sex, provider, georegion, world])

    return datadic


def readaligned(alignedpath):
    alignedfile = open(alignedpath, 'r')
    sequences = {}

    # Read through data to create a dictionary(length:[[seq1,header],[seq2,header], ...,[seqN, header]]).
    header = ""
    for line in alignedfile:
        if line.startswith('>'):
            # extract spider's name
            header = line[1:].rstrip('\n')
        else:
            seq = line.rstrip("\n")
            seq = seq.rstrip("-")
            seqlen = len(seq)
            sequences.setdefault(seqlen, [])
            sequences[seqlen].append([seq, header])

    return sequences


if __name__ == '__main__':
    print(1)
    # geodic = {}
    # geo = open("./datafile/geo/coo.txt", "r")
    # for line in geo:
    #     if line.startswith('>'):
    #         header = line[1:].rstrip('\n')
    #         geodic.setdefault(header, [])
    #         coo = []
    #     elif not line.startswith('#'):
    #         data = line.rstrip('\n')
    #         coo = data.split("\t")
    #         coo[0] = float(coo[0])
    #         coo[1] = float(coo[1])
    #         geodic[header].append(coo)
    # textp = [21, -102]
    # for region, coordinates in geodic.items():
    #     if is_pt_in_poly(textp, coordinates):
    #         print(region)
    #
    # geo.close()
