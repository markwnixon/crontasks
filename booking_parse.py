def bookparse(s5s, txtfile):
    error = 0
    ntyp = 4
    hitems = list(range(ntyp))
    hitems[0] = ['seaship_book', 'vessel', 'port', 'confirmation', 'maple',
                 'reference', 'steamship', 'commodity', 'hazardous', 'disch', 'terminal', 'pier', 'negotiated']
    hitems[1] = ['troy_book', 'troy', 'container', '27 west street', 'vessel', 'shipper', 'contact', 'intended delivery',
                 'lcldocs2@troylines.com', 'freight forwarder compensation', 'discharge', 'coload', 'taken', 'shipper/forwarder'
                 'troy container line ltd', 'booking confirmation', '732-345-0818', 'troy container line', 'troylines.com',
                 'NO DOCS-NO LOAD', 'Charge Description', 'Chassis Surcharge', 'VGM Processing Fee', 'VESSEL/VOY/FLAG', 'CONSIGNEE (NOT NEGOTIABLE',
                 'booking', 'bill of lading', 'export references', 'port of loading']
    hitems[2] = ['hoegh', 'hoegh', 'hoegh', 'hoegh', 'hoegh', 'hoegh', 'hoegh', 'hoegh', 'hoegh', 'hoegh',
                 'container', 'vessel', 'shipper', 'contact', 'intended delivery',
                 'freight forwarder compensation', 'discharge', 'coload', 'taken', 'shipper/forwarder',
                 'booking confirmation', '732-345-0818', 'troy container line', 'troylines.com',
                 'Charge Description', 'Chassis Surcharge', 'VGM Processing Fee',
                 'booking', 'bill of lading', 'export references', 'port of loading']
    hitems[3] = ['maersk', 'maersk', 'maersk', 'maersk', 'maersk', 'maersk', 'maersk', 'maersk',
                 'container', 'vessel', 'shipper', 'contact', 'intended delivery',
                 'freight forwarder compensation', 'discharge', 'coload', 'taken', 'shipper/forwarder',
                 'booking confirmation', '732-345-0818', 'troy container line', 'troylines.com',
                 'Charge Description', 'Chassis Surcharge', 'VGM Processing Fee',
                 'booking', 'bill of lading', 'export references', 'port of loading']

    longs = open(s5s+txtfile).read()
    ss = longs.lower()
    counts = [0]*ntyp
    for i in range(ntyp):
        for item in hitems[i]:
            if item.lower() in ss:
                counts[i] = counts[i]+1

    best = counts.index(max(counts))
    print(counts)
    print(best)
    if best == 0:
        import seaship_parse
        seaship_parse(s5s, txtfile, longs)
    if best == 1:
        from troy_parse import troyparser
        troyparser()
    if best == 2:
        import hoegh_parse
        hoegh_parse.main()
    if best == 3:
        from maersk_parse import maerskparser
        newfile = maerskparser(s5s, txtfile, longs)

    return newfile, error
