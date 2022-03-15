import tarfile
import os
import dateutil


def unzip_all_modis_fire_files(output_path):
    """Function pulls all modis fire data from CEDA archive within Jasmin from 2001 - 2020 and unzips it into output folder. Deals with different file structure for 2019 and 2007 folders.

    output_path = path for unzipped files to be stored e.g. '/home/users/graceebc/MODIS/'

    imports needed: os, tarfile (install tar), dateutil
        import tarfile
        import os
        import dateutil
    """
    print("Pulling and unzipping the MODIS files, start()... ")
    print("Check output directory..")

    # Check path exists
    if os.path.isdir(output_path) is False:
        os.makedirs(output_path)

    # Check that annual folders exist also
    for year in range(2001, 2021):
        if os.path.isdir(output_path + str(year) + "/") is False:
            os.makedirs(output_path + str(year) + "/")

    print("Output directory ready.")
    print("Creating list of files to pulll..")

    # Access all files and unzip - need to treat 2007 and 2019 differently as there was restated data
    year_list = [x for x in range(2001, 2021) if (x != 2007 and x != 2019)]
    months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

    # Create list of files - 2007 has different folder structure + 2019
    file_part1 = [
        "/neodc/esacci/fire/data/burned_area/MODIS/pixel/v5.1/compressed/{0}/{0}{1}01-ESACCI-L3S_FIRE-BA-MODIS-AREA_3-fv5.1.tar.gz".format(
            year, month
        )
        for year in year_list
        for month in months
    ]
    file_part2 = [
        "/neodc/esacci/fire/data/burned_area/MODIS/pixel/v5.1/compressed/2007/new-corrected/2007{0}01-ESACCI-L3S_FIRE-BA-MODIS-AREA_3-fv5.1.tar.gz".format(
            month
        )
        for month in months
    ]
    file_part3 = [
        "/neodc/esacci/fire/data/burned_area/MODIS/pixel/v5.1/compressed/2019/2019{0}01-ESACCI-L3S_FIRE-BA-MODIS-AREA_3-fv5.1.tar.gz".format(
            month
        )
        for month in months[:9]
    ]
    file_part4 = [
        "/neodc/esacci/fire/data/burned_area/MODIS/pixel/v5.1/compressed/2019/new-corrected/2019{0}01-ESACCI-L3S_FIRE-BA-MODIS-AREA_3-fv5.1.tar.gz".format(
            month
        )
        for month in months[-3:]
    ]
    files = file_part1 + file_part2 + file_part3 + file_part4
    print("List of files created.")

    print("Start unzipping files..")
    for file_name in files:

        try:
            dat = dateutil.parser.parse(
                str(file_name[68:80].replace("/", " ")), fuzzy="yes"
            )
            name = dat.strftime("%Y%m%d")

        except:
            dat = dateutil.parser.parse(
                str(file_name[80:95].replace("/", " ")), fuzzy="yes"
            )
            name = dat.strftime("%Y%m%d")
        file_id = "{0}-ESACCI-L3S_FIRE-BA-MODIS-AREA_3-fv5.1-LC.tif".format(name)
        year = name[:4]

        # check if file already unzipped
        if file_id not in os.listdir(output_path + year + "/"):

            # Open file
            file = tarfile.open(file_name)

            # Extracting file
            file.extractall(output_path + year + "/")

            file.close()

    print("Unzipped all MODIS files, bye!")

#Now run the unzip
if __name__ == '__main__':
    outdir = '/home/users/graceebc/test/'
    unzip_all_modis_fire_files(outdit)
