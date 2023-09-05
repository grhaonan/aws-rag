# This scripts uses wget to crawl the input website and 
# save the downloaded files in a given directory.
echo "input args="
echo $@
if [[ "$1" == "yes" ]];
then
    WEBSITE=$2
    DOMAIN=$3
    KB_DIR=$4    
    # delete any existing folder for this data
    rm -rf ${DOMAIN} ${KB_DIR}
    mkdir -p ${KB_DIR}
    
    # download the data, this may take a few minutes or more depending upon the amount of content, network speed etc.
    wget -e robots=off --recursive --no-clobber --page-requisites --html-extension --convert-links --restrict-file-names=windows --domains ${DOMAIN} --no-parent ${WEBSITE}
    
    # we only want to keep the html files
    # and copy them into a new directory with their
    # full path name flattened into a single file
    # so /path/to/a/file becomes path_to_a_file, this
    # is done so that we can upload all files to a single 
    # prefix in S3 which allows the Sagemaker Processing Job
    # to easily split the files between instances    
    for i in `find ${DOMAIN} -name "*.html"`
    do
        flat_i=`echo "${i//\//_}"`
        echo going to copy $i to ${KB_DIR}/$flat_i
        cp $i ${KB_DIR}/$flat_i 
    done
    
    file_count=`ls | wc -l`
    echo there are $file_count files in ${DOMAIN} directory
else
    echo DOWNLOAD_DATA=$1, not downloading new data
fi