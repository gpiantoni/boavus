"""Put in this module functions that might end up in bidso because they are
reused often.
"""

def find_labels_in_regions(electrodes, regions):

    if len(regions) > 0:
        select_regions = lambda x: x['region'] in regions
    else:
        select_regions = lambda x: True

    return electrodes.electrodes.get(filter_lambda=select_regions,
                                     map_lambda=lambda x: x['name'])
