BitChart
====

Analyze BitCoin-Chart
https://bitchart.mmw.works

BitFlyerのAPIでtickerを取得し、1分足のローソク足チャートを作成し表示する。


## Start

### Local

```bash
$ docker-compose up -d --build
```

※ `/etc/hosts` ファイルに `0.0.0.0 [ドメイン名]` を追加すること

### Production Server

```bash
$ STAGE=production docker-compose up -d --build
```

## Structure

```bash
$ docker-compose ps
         Name                        Command               State                    Ports                  
-----------------------------------------------------------------------------------------------------------
analyzer                  python analyze.py                Up                                              
https-portal              /init                            Up      0.0.0.0:443->443/tcp, 0.0.0.0:80->80/tcp
nginx                     nginx -g daemon off;             Up      80/tcp, 0.0.0.0:8080->8080/tcp          
presenter                 gunicorn --bind unix:/run/ ...   Up                                              
watcher                   python watch.py                  Up
```
