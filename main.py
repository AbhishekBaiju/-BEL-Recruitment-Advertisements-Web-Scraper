import requests
from bs4 import BeautifulSoup
import urllib3
import pandas as pd
from retry import retry
import webbrowser  

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = 'https://bel-india.in/CareersGridbind.aspx?MId=29&LId=1&subject=1&link=0&issnno=1&name=Recruitment+-+Advertisements'

@retry(tries=3, delay=2)
def fetch_data():
    response = requests.get(url, verify=False, timeout=10)
    response.raise_for_status()
    return response.content

def format_link(href):
    if href.lower().endswith('.pdf'):
        return f"https://bel-india.in/{href}"
    else:
        return href

try:
    html_content = fetch_data()

    soup = BeautifulSoup(html_content, 'html.parser')

    table = soup.find('table', {'id': 'ctl00_TopContent_gvbinddate'})

    data = []
    for row in table.find_all('tr')[1:]:
        columns = row.find_all('td')
        sl_no = columns[0].text.strip()
        post = columns[1].text.strip()

        links = [{'text': a.text.strip(), 'href': format_link(a['href'])} for a in columns[2].select('a')]
        advertisement_links = [f"<a href='{link['href']}'>{link['text']}</a>" for link in links]
        
        advertisement = '<br>'.join(advertisement_links)
        last_date = columns[3].text.strip()

        data.append({'Sl. No.': sl_no, 'Post': post, 'Advertisement': advertisement, 'Last Date To Apply': last_date})

    df = pd.DataFrame(data)

    html_string = f'''
    <html>
        <head>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
            <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
        </head>
        <body>
            <div class="container">
                <h1 class="mt-4 mb-4 text-center"><span><a href="https://bel-india.in">BEL </a></span> - RECRUITMENT - ADVERTISEMENTS</h1>
                <p class="font-weight-bold text-center"><span class="text-danger">**This website is not affiliated with <a href="https://bel-india.in" target="_blank">Bharat Electronics Limited (BEL)</a></span>. The original data source can be found at <a href="{url}" target="_blank">bel-india/Careers**</a>.</p>
                {df.to_html(classes='table table-bordered table-striped', index=False, escape=False)}
            </div>
            <footer class="text-center mt-4">
                <p class="font-weight-bold"><span class="text-danger">**This website is not affiliated with <a href="https://bel-india.in" target="_blank">Bharat Electronics Limited (BEL)</a></span>. The original data source can be found at <a href="{url}" target="_blank">bel-india/Careers**</a>.</p>
            </footer>
        </body>
    </html>
    '''

    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(html_string)

    print(f"Data saved to index.html")

    webbrowser.open('index.html', new=2)

except requests.RequestException as e:
    print(f"Error during request: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
