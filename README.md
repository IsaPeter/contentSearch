# contentSearch
This tool is a Python implementation of Gobuster and other directory brute-force tools. This tool is not intended to replace other tools, the reason why I wrote this, that educational purposes only. I would like to know better what, and how directory brute-forcing works, so I wrote this tool.


## Usage

```bash
usage: contentSearch.py [-h] [-u] [-w] [-e] [-t] [-s] [-R] [-cl] [-T] [-st] [-k] [-proxy] [-rc] [-c] [--header  [...]] [-ua] [-o]

optional arguments:
  -h, --help            	show this help message and exit
  -u , --url            	The page URL
  -w , --wordlist       	The wordlist
  -e , --extensions     	The extensions to probe
  -t , --thread         	The number of the working threads
  -s , --status-codes   	The status codes to watch
  -R , --regex          	Use Regex pattern to filter response
  -cl , --content-length 	The length of the reponse
  -T , --timeout        	The timeout to wait a worker for an answer
  -st , --send-timeout 		The sending timeout between requests
  -k, --avoid-ssl       	Avoid to verrify SSL certificate
  --proxy                	Set up proxy. HOST:PORT
  -rc , --response-contains The response is contains a word
  -c , --cookies        	Use Cookies for the request
  --header  [ ...]      	Header fields of the requests
  -ua , --user-agent    	The UserAgent String for use the requests
  -o , --output         	Write result into outfile.
```

 ## Examples

**Simple content listing**

```bash
$ contentSearch.py -u http://samplepage.com/ -w /path/to/wordlist.txt -t 120 -e php,txt -o output.txt
```



## Functions of the future

- The proxy switch is not implemented yet, only the help menu shows this existence.
- create groups for argparse to more clear help menu.
- implement content-length options (greater than, less than..)
