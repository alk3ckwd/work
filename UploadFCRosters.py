# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 13:53:27 2017

@author: mmcvicar
"""
import json
import http.client
import os
import mimetypes
import time
import urllib


def authenticate(hostname, client_id, client_secret, username, password):
    """ Authenticate via username/password. Returns json token object.
     
    Args:
    string hostname - hostname like "myaccount.sharefile.com"
    string client_id - OAuth2 client_id key
    string client_secret - OAuth2 client_secret key
    string username - my@user.name
    string password - my password """
 
    uri_path = '/oauth/token'
     
    headers = {'Content-Type':'application/x-www-form-urlencoded'}
    params = {'grant_type':'password', 'client_id':client_id, 'client_secret':client_secret,
              'username':username, 'password':password}
     
    https = http.client.HTTPSConnection(hostname)

    https.request('POST', uri_path, urllib.parse.urlencode(params), headers=headers)
    response = https.getresponse()
    str_response = response.read().decode('utf-8')
     
    #print(response.status, response.reason)
    token = None
    if response.status == 200:
        token = json.loads(str_response)
        #print('Received token info', token)
     
    https.close()
    return token
 
def get_authorization_header(token):
    return {'Authorization':'Bearer %s'%(token['access_token'])}
     
def get_hostname(token):
    return '%s.sf-api.com'%(token['subdomain'])

def upload_file(token, folder_id, local_path):
    """ Uploads a File using the Standard upload method with a multipart/form mime encoded POST.
 
    Args:
    dict json token acquired from authenticate function
    string folder_id - where to upload the file
    string local_path - the full path of the file to upload, like "c:\\path\\to\\file.name" """
     
    uri_path = '/sf/v3/Items(%s)/Upload'%(folder_id)
    http2 = http.client.HTTPSConnection(get_hostname(token))
    http2.request('GET', uri_path, headers=get_authorization_header(token))
 
    response = http2.getresponse()

    str_response = response.read().decode('utf-8')
    upload_config = json.loads(str_response)
    if 'ChunkUri' in upload_config:
        upload_response = multipart_form_post_upload(upload_config['ChunkUri'], local_path)
        print(upload_response.status, upload_response.reason)
    else:
        print('No Upload URL received')

def multipart_form_post_upload(url, filepath):
    """ Does a multipart form post upload of a file to a url.
     
    Args:
    string url - the url to upload file to
    string filepath - the complete file path of the file to upload like, "c:\path\to\the.file
     
    Returns:
    the http response """
     
    newline = '\r\n'
    filename = os.path.basename(filepath)
    data = []
    headers = {}
    boundary = '----------%d' % int(time.time())
    headers['content-type'] = 'multipart/form-data; boundary=%s' % boundary
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"; filename="%s"' % ('File1', filename))
    data.append('Content-Type: %s' % get_content_type(filename))
    data.append('')
    file = open(filepath, mode='rb').read().decode('ISO 8859-1')
    
    data.append(file)
    data.append('--%s--' % boundary)
    data.append('')
    data_str = newline.join(data)
    headers['content-length'] = len(data_str)
     
    uri = urllib.parse.urlparse(url)
    http2 = http.client.HTTPSConnection(uri.netloc)
    http2.putrequest('POST', '%s?%s'%(uri.path, uri.query))
    for hdr_name, hdr_value in headers.items():
        http2.putheader(hdr_name, hdr_value)
    http2.endheaders()
    http2.send(data_str.encode('ISO 8859-1'))
    return http2.getresponse()
    
def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'      

if __name__ == '__main__':
    hostname = "challiance.sharefile.com"
    username = "mmcvicar@ch-alliance.org"
    password = "chachf5901"
    client_id = 'rVD369bgeGQARhvuYBSk5GFfpdIqEgwD'
    client_secret = 'zYfDGg3q6HZh27dGr3z0wduf4LwoJMnseT5F6uvrwl4v1NPN'

    token = authenticate(hostname, client_id, client_secret, username, password)
    base_path = 'S:/Health Plans/FamilyCare/PHI Claims Data/Reconciliation Folders by Year/2017/02 February/'
    ##PARSE SETTINGS
    with open('FCRosterSFFolders.json') as settings:
        folderMapping = json.load(settings)

    if token:
        for k,v in folderMapping.items():
            print("Uploading: ", k)
            upload_file(token,v,base_path+k)
        #