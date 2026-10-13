import json, sys, urllib.request, urllib.parse, os, concurrent.futures as cf
UA={'User-Agent':'ClaudeOppResearch/1.0 (personal ad research; python urllib)'}
def api(params):
    params.update(format='json')
    u='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params)
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
def search(q,n=12):
    r=api(dict(action='query',generator='search',gsrnamespace=6,gsrsearch=q,gsrlimit=n,prop='imageinfo',iiprop='url|size|mime',iiurlwidth=360))
    out=[]
    for p in sorted(r.get('query',{}).get('pages',{}).values(),key=lambda p:p.get('index',0)):
        ii=p['imageinfo'][0]
        if ii['mime'] not in ('image/jpeg','image/png','image/tiff','image/gif','image/svg+xml'): continue
        out.append(dict(title=p['title'],w=ii['width'],h=ii['height'],thumb=ii.get('thumburl'),url=ii['url']))
    return out
if __name__=='__main__':
    queries=json.load(open(sys.argv[1]))
    res={}
    def run(item):
        k,q=item
        try: return k,search(q)
        except Exception as e: return k,[]
    with cf.ThreadPoolExecutor(6) as ex:
        for k,v in ex.map(run,queries.items()): res[k]=v
    json.dump(res,open(sys.argv[2],'w'),indent=1)
    for k,v in res.items(): print(k,len(v))
