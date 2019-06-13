from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
import conf

app = Flask(__name__)

chart_list = conf.product_code_list


@app.route('/')
def index():
    chart_list_with_current_prices = {}
    for product_code in chart_list:
        df = pd.read_csv(f'data/{product_code}.resample.tsv', sep='\t')
        chart_list_with_current_prices[product_code] = df.iloc[-1]['close']
    return render_template('index.html', chart_list=chart_list_with_current_prices)


@app.route('/chart/<name>')
def chart(name):
    # チャートのタグ作成にBokehのcomponentsを使うと複数チャート表示時の横幅がずれるためHTMLをパースして使う
    html = Path(f'static/chart/{name}.html').read_text()
    soup = BeautifulSoup(html, "html.parser")
    graphs = str(soup.body.div)
    script = ''.join(str(tag) for tag in soup.body.find_all('script'))
    return render_template('chart.html', name=name, graphs=graphs, script=script)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
