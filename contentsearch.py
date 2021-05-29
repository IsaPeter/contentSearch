#!/usr/bin/env python3
"""
Content Search
"""
import argparse,requests,threading,queue,os,time,re,sys


class contentSearch():
    def __init__(self,url=''):
        self.url = url                  # Target URL
        self.word_queue = queue.Queue() # Queue for the wordlist
        self.current_status = 0         # count of the probed words
        self.words_count = 0           # count of the wordlist
        self.wordist_path = ''         # path of the given wordlist
        self.extensions = []
        self.threads = 10
        self.workers = []
        self.status_codes = [200,204,301,302,307,401,403]
        self.regex_pattern = ''
        self.enable_regex_search = False
        self.content_length = 0
        self.enable_content_lenght_search = False
        self.timeout = 10
        self.send_timeout = 0
        self.user_agent = 'content-searcher/1.0'
        self.proxy = '127.0.0.1:8080'
        self.response_contains = ''
        self.enable_response_contains_search = False
        self.cookies = {}
        self.headers = {}
        self.verify_ssl = True
        self.output_string = ''
        self.output_file = ''
        
        self.set_user_agent(self.user_agent) # Set the custom made user-agent
        
    def start(self):
        words = self._read_words_file(self.wordist_path)  # reading words from file
        self.words_count = len(words)
        # Put words into the queue
        for w in words:
            self.word_queue.put(w)
        # print the banner
        self._print_banner()
        self._create_working_threads(self.threads) # Create the workers and start them
        
        while not self.word_queue.empty():
            self._print_percentage()
            time.sleep(0.8)
        # Finished job, join all the workers
        for wt in self.workers:
            wt.join()     
        
        if self.output_file != '':
            self._write_output()
        
    def stop(self):
        pass
    def pause(self):
        pass

    # setters of the application
    def set_url(self,url):
        self.url = url
    def set_wordlist(self,path):
        if os.path.isfile(path):
            self.wordist_path = path
        else:
            print("Invalid wordlist File. Not exists.")
    def add_extension(self,ext):
        if ext not in self.extensions:
            self.extensions.append(ext)
    def set_extensions(self,ext_list):
        if type(ext_list) == type([]):
            self.extensions = ext_list
        elif type('str') == type(ext_list):
            self.extensions = ext_list.replace(' ','').split(',')
            
    def set_threads(self,threads):
        if int(threads) > 0:
            self.threads = int(threads)
    def add_status_code(self,code):
        if int(code) not in self.status_codes:
            self.status_codes.append(int(code))
    def set_status_codes(self,code_list):
        if type(code_list) == type([]):
            self.status_codes = code_list
        elif type('str') == type(code_list):
            self.status_codes.clear()
            codes = code_list.replace(' ','').split(',')
            for c in codes:
                self.status_codes.append(int(c))
            
    def set_regex(self,regex):
        self.enable_regex_search = True
        self.regex_pattern = regex
    def set_content_length(self,cl):
        self.enable_content_lenght_search = True
        self.content_length = int(cl)
    def set_timeout(self,t):
        self.timeout = int(t)
    def set_send_timeout(self,st):
        self.send_timeout = int(st)
    def set_user_agent(self,ua):
        self.user_agent = ua
        self.headers['User-Agent'] = ua
    def set_response_contains(self,rc):
        self.enable_response_contains_search = True
        self.response_contains = rc
    def add_cookie(self,cookie):
        if cookie not in self.cookies:
            self.cookies.update(cookie)
    def set_cookies(self,cookie_list):
        if type(cookie_list) == type({}):
            self.cookies = cookie_list
        elif type('str') == type(cookie_list):
            carr = cookie_list.split(';')
            for c in carr:
                k,v = c.split('=',1)
                self.cookies.update({k:v})
            
    def add_header(self,h):
        if h not in self.headers:
            self.headers.update(h)
    def set_headers(self,h):
        if type(h) == type({}):
            self.headers = h  
        elif type([]) == type(h):
            for hitem in h:
                k,v = hitem[0].split(':')
                self.headers.update({k:v})
    
       
    def disable_ssl(self):
        self.verify_ssl = False
        
    def set_outfile(self,path):
        self.output_file = path
        
    # Private methods of the application  
    def _print_banner(self):
        print("[+] URL: "+self.url)
        print("[+] Threads: "+str(self.threads))
        print("[+] Wordlist: "+self.wordist_path)
        print("[+] Status Codes: ["+str(', '.join(map(str,self.status_codes)))+"]")
        print("[+] Extensions: ["+str(', '.join(self.extensions))+"]")
        print("################################################\n")        
            
    def _read_words_file(self,filepath):
        if os.path.isfile(filepath):
            with open(filepath,'r') as f:
                lines = f.readlines()
                self.words_count = len(lines) # Set the words count
                return lines
        else:
            print(f"The Wordlist File: {filepath} does not exists!")
            os.sys.exit(1)  
    def _print_percentage(self):
        if self.current_status > 0:
            percentage = round((self.current_status / self.words_count)*100,2)
        else:
            percentage = 0
        print(f"Status: {self.current_status}/{self.words_count} ({str(percentage)}%)\r",end='')


    def _join_uri(self,url,word):
        result = ''
        if url.endswith('/'):
            if word.startswith('/'):
                word = word.lstrip('/')
        else:
            if not word.startswith('/'):
                word = '/'+word
        return url+word.rstrip('\n')
    def _join_extension(self,uri,ext):
        result = ''
        if ext.startswith('.'):
            result = uri + ext
        else:
            result = uri +'.'+ext
        return result
    def _create_working_threads(self,threadnum):
        # Create working threads
        for i in range(threadnum):
            t = threading.Thread(target=self._worker,args=(i,))
            self.workers.append(t)
            t.start()
    def _handle_http_response(self,response,uri):
        printable = True
        if self.enable_content_lenght_search:
            if self.content_length == len(response.text):
                printable = True
            else:
                printable = False
        if self.enable_regex_search:
            match = re.search(self.regex_pattern,response.text,re.M|re.I)
            if len(match) > 0:
                printable = True
            else:
                printable = False
        if self.enable_response_contains_search:
            if self.response_contains in response.text:
                printable = True
            else:
                printable = False
        if printable:
            print(f"{uri} [{str(response.status_code)}]")
            if self.output_file != '':
                self.output_string += f"{uri} [{str(response.status_code)}]\n"
            
    def _worker(self,number):
        workernumber = number        
        
        while not self.word_queue.empty():
            next_word = self.word_queue.get()
            uri = self._join_uri(self.url,next_word)
            response = requests.get(uri)    # Try the base uri without extensions
            if response.status_code in self.status_codes:
                self._handle_http_response(response,uri) # Handling the response
            
            if len(self.extensions) > 0:
                for e in self.extensions:
                    uri_ext = self._join_extension(uri,e)
                    response = requests.get(uri_ext, verify=self.verify_ssl, headers=self.headers, cookies=self.cookies, timeout=self.timeout)
                    if response.status_code in self.status_codes:
                        self._handle_http_response(response,uri_ext)   
            self.current_status += 1
    def _write_output(self):
        with open(self.output_file,'w') as o:
            o.write(self.output_string)
        
        
        
# Methods to delete
def parse_arguments():
    parser = argparse.ArgumentParser(prog='contentSearch.py')
    
    parser.add_argument('-u','--url',dest='url',metavar='',help='The page URL')
    parser.add_argument('-w','--wordlist',dest='wordlist',metavar='',help='The wordlist')
    parser.add_argument('-e','--extensions',dest='extensions',metavar='',help='The extensions to probe')
    parser.add_argument('-t','--thread',dest='thread',metavar='',help='The number of the working threads')
    parser.add_argument('-s','--status-codes',dest='statuscodes',metavar='',help='The status codes to watch')    
    parser.add_argument('-R','--regex',dest='regex',metavar='',help='Use Regex pattern to filter response')
    parser.add_argument('-cl','--content-length',metavar='',dest='contentlength',help='The length of the reponse')
    parser.add_argument('-T','--timeout',dest='timeout',metavar='',help='The timeout to wait a worker for an answer')
    parser.add_argument('-st','--send-timeout',dest='sendtimeout',metavar='',help='The sending timeout between requests')
    parser.add_argument('-k','--avoid-ssl',dest='avoidssl',action='store_true',help='Avoid to verrify SSL certificate')
    parser.add_argument('--proxy',dest='proxy',metavar='',help='Set up proxy. HOST:PORT')
    parser.add_argument('-rc','--response-contains',dest='rcontains',metavar='',help='The response is contains a word')
    parser.add_argument('-c','--cookies',dest='cookies',metavar='',help='Use Cookies for the request')
    parser.add_argument('--header',dest='header',action='append',nargs='+',metavar='',help='Header fields of the requests')
    parser.add_argument('-ua','--user-agent',dest='useragent',metavar='',help='The UserAgent String for use the requests')
    parser.add_argument('-o','--output',dest='output',metavar='',help='Write result into outfile.')
    
    
    args = parser.parse_args()
    return args
    
    



    

def main():
    args = parse_arguments()
    
    search = contentSearch()
    if args.url: search.set_url(args.url)
    if args.wordlist: search.set_wordlist(args.wordlist)
    if args.extensions: search.set_extensions(args.extensions)
    if args.thread: search.set_threads(int(args.thread))
    if args.statuscodes: search.set_status_codes(args.statuscodes)
    if args.regex: search.set_regex(args.regex)
    if args.contentlength: search.set_content_length(args.contentlength)
    if args.timeout: search.set_timeout(args.timeout)
    if args.sendtimeout: search.set_send_timeout(args.sendtimeout)
    if args.avoidssl: search.disable_ssl()
    if args.rcontains: search.set_response_contains(args.rcontains)
    if args.cookies: search.set_cookies(args.cookies)
    if args.useragent: search.set_user_agent(args.useragent)    
    if args.header: search.set_headers(args.header)
    if args.output: search.set_outfile(args.output)
    
    search.start()
    
    
    
if __name__ == '__main__':
    main()