# -*- coding: utf-8 -*-
'''
Created on 2013-3-14

@author: shaofei.ma
'''
import urllib2
import urllib
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers  

import os
import time
import logging
from logging.handlers import RotatingFileHandler

import xml.etree.ElementTree as ET
import ConfigParser
import auto_declare_bug

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
VERSION_LIST =[]
ZIP_VERSION = ""


LOGPATH = os.getcwd() + "/log"
LOGNAME = "log.txt"
CONFFILE = os.getcwd() + "/dump.conf"

#use 10.10.2.72
VERSION_PATH_8 = r'\\10.10.2.72\nas\DVDFab_Dump\DVDFab\___DVDFab8'
VERSION_PATH_9 = r'\\10.10.2.72\nas\DVDFab_Dump\DVDFab\___DVDFab9'
NAS_DOWNLOAD_DUMP_PATH = r"\\10.10.2.72\nas\DVDFab_Dump\DVDFab"


def get_time():
    s_end = time.strftime('%Y-%m-%d %H:%M:%S')
    start = time.time() - 1 * 3600 * 24.0
    start = time.localtime(start)
    
    if start[1] < 10:
        start_mon = '0' + str(start[1])
    else:
        start_mon = str(start[1])
    if start[2] < 10:
        start_day = '0' + str(start[2])
    else:
        start_day = str(start[2])
    if start[3] < 10:
        start_hour = '0' + str(start[3])
    else:
        start_hour = str(start[3])
    if start[4] < 10:
        start_min = '0' + str(start[4])
    else:
        start_min = str(start[4])
    if start[5] < 10:
        start_sec = '0' + str(start[5])
    else:
        start_sec = str(start[5])
    s_start = str(start[0]) + '-' + start_mon + '-' + start_day + ' ' +  start_hour + ':' +  start_min + ':' +  start_sec
    return s_end


def get_version(version_path):
    return os.listdir(version_path)


def update_conf_file(new_version_list):
    sum = ""
    for version in new_version_list:
        sum += "," + version
    fp = open(CONFFILE, "a+")
    fp.write(sum)
    fp.close()


def get_params(all_version_list):
    params_list = []
    new_version_list = []
    version_list = []
    special_version = read_ini("Params","special_version").strip()
    if special_version:
        for record in special_version.split(","):
            version_list.append(record.strip())
    else:
        version = read_ini("Params","version")
        version_list1 = version.split(",")
        for record in version_list1:
            version_list.append(record.strip())
        for each_version in all_version_list:
            if each_version not in version_list:
                version_list.append(each_version)
                new_version_list.append(each_version)
        update_conf_file(new_version_list)
    for s_version in version_list:
        s_software = read_ini("Params", "software")
        s_start = read_ini("Params", "start")
        s_end = read_ini("Params", "end")
        if s_end == '':
            s_end = time.strftime('%Y-%m-%d %H:%M:%S')
        s_has_email = read_ini("Params", "has_email")
        s_has_content = read_ini("Params", "has_content")
        
        params = [s_software, s_version.strip()]
        
        if (not s_start) and (not s_end):
            cur_date = time.strftime("%Y-%m-%d", time.localtime(time.time()))
            params.append("%s 00:00:00" % cur_date)
            params.append("%s 23:59:59" % cur_date)
        else:
            if s_start:
                if s_start.count(":") == 2:
                    params.append(s_start)
                else:
                    params.append('%s 00:00:00' % s_start)
            else:
                params.append("")
                
            if s_end:
                if s_end.count(":") == 2:
                    params.append(s_end)
                else:
                    params.append('%s 00:00:00' % s_end)
            else:
                params.append("")
        
        if s_has_email:
            params.append("1")
        else:
            params.append("")
            
        if s_has_content:
            params.append("1")
        else:
            params.append("")
        params_list.append(params)
    return params_list

#post http info to server
def poster_post_search(params):
    result = ""
    
    try:
        register_openers()          
        
        #datagen, headers = multipart_encode({'d':open(dest_file, 'rb'), "t":3, "l":"en"})
        datagen, headers = multipart_encode({"software":params[0], "version":params[1], "start":params[2], "end":params[3], "has_email":params[4], "has_content":params[5]})
        #datagen, headers = multipart_encode(params)
        #print "HTTP post is: ", HTTPPOST
        # Create a Request object
        request = urllib2.Request(HTTPPOST, datagen, headers)     
        
        # Actually do POST request
        response = urllib2.urlopen(request)   
        
        result = response.read() 
        response.close()     

    except Exception as e:
        log("Post search error: %s" % str(e))

    return result

def analyze_xml(xml_string):
    l_temp = []
    l_result = []   
    
    #u_string = xml_string.decode("SHIFT_JIS").encode("utf-8")
    #u_string = xml_string.decode("ISO-2022-JP", 'ignore').encode("utf-8")
    #print "xml string is: ", xml_string
    try:
        try:
            u_string = xml_string.decode("EUC-JP", 'ignore').encode("utf-8")
            log(u_string)
        except Exception as e:
            log("xml-string.decode error: " + str(e))
            
        try:
            xml_doc = ET.fromstring(u_string)
        except Exception as e:
            log("ET.fromsting error: " + str(e))
            
        try:
            total = xml_doc.findall("total")
        except Exception as e:
            log("xml_doc.findall error: " + str(e))
            
        try:
            total_info = "Total %s dump files." % total[0].text
            print total_info
            log( total_info)
        except Exception as e:
            log("4444444444444,  " + str(e))
        try:        
            all_items = xml_doc.findall("item")
            for item in all_items:
                for child in item.getchildren():
                    l_temp.append(child.text.strip())
                    #print child.tag, ":", child.text
                l_result.append(l_temp)
                l_temp = []
        except Exception as e:
            log("555555555555555,  " + str(e))
    except Exception as e:
        print "Analyze xml error: %s" % str(e)
        log( "Analyze xml error: %s" % str(e))
        return l_result
    return l_result



def download_dump(zip_url, version):
    #upload, date, filename = zip_url.split("/")
    date, filename = zip_url.split("/")
    local_path = os.path.join(LOCALPATH, date, version)

    if not os.path.exists(local_path):
        os.makedirs(local_path, mode=0777)
    dest_dir = os.path.join(local_path, filename)
    url_address = HTTPADDRESS + zip_url
    print "url_address: ", url_address
    try:
        if not os.path.exists(dest_dir):
            try:
                urllib.urlretrieve(url_address,dest_dir)
                print "post success"
            except Exception as e:
                print "here: ", str(e)
                log("here: " + str(e))
    except Exception as e:
        log(str(e))      
    return local_path

def remove_node_post(s_id):
    result = ""
    try:
        register_openers()   

        datagen, headers = multipart_encode({"id":s_id})
        # Create a Request object
        request = urllib2.Request(HTTPREMOVE, datagen, headers)     

        # Actually do POST request
        response = urllib2.urlopen(request)   

        result = response.read()
        response.close()
    except Exception as e:
        log("Remove dump info error: %s" % str(e))
    #finally:
    #    response.close()
    
    if result == "ok":
        log("Remove id=%s" % s_id)
        print "Remove id=%s" % s_id
    else:
        log("Remove id=%s error" % s_id)
    return


def remove_node_get():
    import httplib
    conn = httplib.HTTPConnection("report.dvdfab.com")
    conn.request("GET", "/api.php?a=remove&id=146056")
    res = conn.getresponse()
    print res.status, res.reason
    data = res.read()
    res.close()
    print data
    return
	
def get_right_analyze(version):
    if version >= 9307:
        DumpAnalyze_path = read_ini('FilePath', 'DumpAnalyze_9307_path')
    else:
        DumpAnalyze_path = read_ini('FilePath', 'DumpAnalyze_path')
    return DumpAnalyze_path
 
def changepath(local_path):
    if not (local_path.endswith("/") or local_path.endswith("\\")):
        local_path += "/" 
    return local_path

def write_file(filename, content):
    fp = open(filename, "w")
    fp.write(content)
    fp.close()
	
def write_format_file(filename, s_version, s_time):
    fp = open(filename, 'w')
    fp.write(s_version)
    fp.write(' ')
    fp.write(s_time)
    fp.close()

def get_pdb_path(version):
    PdbPath_8 = read_ini('FilePath', 'PdbPath_8')
    PdbPath_9 = read_ini('FilePath', 'PdbPath_9')
    if version.strip().startswith("8"):
        PdbPath = PdbPath_8
    elif version.strip().startswith("9"):
        PdbPath = PdbPath_9
    else:
        PdbPath = ""
    return PdbPath
    	
def get_content(each_line):
    content = "[Info]\r\nid=" + each_line[0] + "\r\nversion=" + each_line[1] + "\r\nsoftware_title=" + each_line[2] + "\r\nrecord_type=" + each_line[3] + "\r\nname=" + each_line[4] + \
	"\r\nemail=" + each_line[5] + "\r\nsubject=" + each_line[6] + "\r\ncontent=" + each_line[7] + "\r\nwindows_version=" + each_line[8] + "\r\ndvd_title=" + each_line[9] + "\r\nregion_code=" + \
	each_line[10] + "\r\ncountry=" + each_line[11] + "\r\nbuy_link=" + each_line[12] + "\r\nfile=" + each_line[13] + "\r\nstatus=" + each_line[14] + "\r\ntime=" + each_line[15]
    return content	
	
def create_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    
def main(num_dump):
    if num_dump == 0:
        return 
    version_8 = get_version(VERSION_PATH_8)
    version_9 = get_version(VERSION_PATH_9)
    all_version_list = version_8 + version_9
    params_list = get_params(all_version_list)  
    for params in params_list:
        print  params
        results_string = poster_post_search(params)
        l_results = analyze_xml(results_string)
        i = 0
        if l_results:
            for each_line in l_results:            
                s_id, s_version, s_software, s_email, s_download, s_time = each_line[0], each_line[1], each_line[2], each_line[5], each_line[13], each_line[15]   
                log(each_line)
                print each_line
                local_path = changepath(download_dump(s_download, s_version))
                filename = os.path.basename(s_download).replace("zip", "txt")
                content = get_content(each_line)
                write_file(local_path + filename, content)
                SimplePath = changepath(read_ini('FilePath', 'SimplePath'))
                create_folder(SimplePath)
                write_format_file(SimplePath + "version.txt", s_version, s_time)
                LocalPath = changepath(read_ini('Path', 'LocalPath'))
                zip_file_path = LocalPath + os.path.split(s_download)[0] + '\\' + s_version + '\\' + os.path.split(s_download)[1]
                try:
                    DumpAnalyze_path = get_right_analyze(int(s_version))
                except Exception as e:
                    log("get analyzed program failed, %s" % str(e))
                    continue
                log("DumpAnalyze_path is %s !" % DumpAnalyze_path)
                PdbPath = get_pdb_path(s_version)
                if not PdbPath:
                    continue
                auto_declare_bug.main(s_version, zip_file_path, DumpAnalyze_path, PdbPath)
                time.sleep(1)
                remove_node_post(s_id)       
                log("\n\n")
                #TODO: deploy AnalyzeDump.exe, and use sikuly to create a new bug on mantis
                i = i+1
                if i == num_dump:
                    break 
        else:
            log("Sorry, no dump files, please modify params in dump.conf.") 
    return

def read_ini(field, key):
    cf = ConfigParser.ConfigParser()
    cf.read(CONFFILE)
    value = cf.get(field, key)
    return value

	
def log(info):
    if not os.path.exists(LOGPATH):
        os.mkdir(LOGPATH)
    logging.basicConfig(filename = LOGPATH + '/' + LOGNAME, level = logging.NOTSET, filemode = 'a', format = '%(asctime)s : %(message)s')      
    logging.info(info) 
	

def get_count_dump(count_dump):
    if not count_dump or int(count_dump) <= 50:
	    times_request = 0
        amount_dump = int(count_dump)
    elif int(count_dump)>50:        
	    times_request = int(count_dump)/50
	    amount_dump = int(count_dump)%50
    return times_request, amount_dump
		

if __name__ == '__main__':
    while 1:	
        sleep_time = read_ini('Params', 'sleep_time')
        sleep_time = int(sleep_time)
        http_path = read_ini("Http", "Address")
        remove_path = read_ini("Http", "Remove")
        request_path = read_ini("Http", "Request")
        local_path = read_ini("Path", "LocalPath")#.decode("utf-8")
        count_dump= read_ini("SumDump", "count")
        HTTPADDRESS = "http://report.dvdfab.com/upload/" if not http_path else http_path
        HTTPADDRESS = changepath(HTTPADDRESS)
        HTTPREMOVE = HTTPADDRESS + "api.php?a=remove" if not remove_path else remove_path
        HTTPPOST = HTTPADDRESS + "api.php?a=list" if not request_path else request_path   
        LOCALPATH = r"\\10.10.2.72\nas\DVDFab_Dump\DVDFab" if not local_path else local_path
        times_request, amount_dump = get_count_dump(count_dump)
        for i in range(times_request):
            main(50)       
        print "Game over!"
        log("Game Over!\n")
        time.sleep(sleep_time*3600)
   
        
