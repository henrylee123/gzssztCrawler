import  requests as req
import cx_Oracle

def connect_oracle():
    conn_dct = {
        "user": "hiibase",
        "password": "hiibase",
        "dsn": "200.100.100.69:1521/dgr"
    }

    conn  = cx_Oracle.connect(**conn_dct)
    cur = conn.cursor()

    insert_sql = "insert into hiibase.gzsszt_tbs_listhtml (farticle, furl, fpagenum) values (:1, :2, :3)"
    cur.prepare(insert_sql)
    return cur, conn

h = {

}

def  get_html():
    for i in range(4983, 260762):
        u = f"http://cri.gz.gov.cn/Search/Result?validateCode=rj1ia&guid=4688B14F1859168818030D669BDAD38673F840F1779230C4B7CDDDA6E78B5B94&keywords=%E5%B9%BF%E5%B7%9E%E6%B3%A8%E5%86%8C%E4%BC%81%E4%B8%9A&page={str(i)}"
        r = req.get(url=u, headers=h)
        t = r.text.encode('gbk',errors='ignore').decode('gbk')
        cur.executemany(None, [[t, u, str(i)]])
        print(i)
        conn.commit()

if __name__  == "__main__":
    cur, conn = connect_oracle()
    get_html()