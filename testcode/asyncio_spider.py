from multiprocessing import Pool
import asyncio
import aiohttp
from spider import connect_oracle
import asyncio
import io


class AsyncFile:
    class _ReadContent:
        '''缓存读取的数据
        read 在子线程中进行
        用 _ReadContent().content 存储返回值
        '''

        def __init__(self, content=None):
            self.content = content

    def __init__(self, path: str, open_flag: str = "r", executor=None):
        # 路径
        self.path = path
        # 文件打开标记
        self.open_flag = open_flag
        # 文件
        self._f = open(path, open_flag)
        # 当前 event_loop
        self._loop = asyncio.get_event_loop()
        # 读写锁,同一时间最多只能有1个读者或者写者
        self._rw_lock = asyncio.Lock()
        # concurrent.futures 的 ThreadPoolExecutor 或者 ProcessPoolExecutor
        # 不过我不确定用 ProcessPoolExecutor 有没有用
        # 默认值为None，之后使用的就是loop的默认executor
        self._executor = executor

    def _read(self, r_content: _ReadContent, over_semaphore: asyncio.Semaphore):
        # 读操作（阻塞）
        r_content.content = self._f.read()
        # 让父协程从等待队列中唤醒
        over_semaphore.release()

    def _write(self, content, over_semaphore: asyncio.Semaphore):
        # 写操作（阻塞）
        self._f.write(content)
        # 让父协程从等待队列中唤醒
        over_semaphore.release()

    async def read(self):
        if not self._f.readable():
            raise io.UnsupportedOperation()
        async with self._rw_lock:
            # ===============================================
            # over_semaphore 信号量表示了操作是否结束
            over_semaphore = asyncio.Semaphore(0)
            _read_content = self._ReadContent()
            self._loop.run_in_executor(self._executor \
                                       , self._read, _read_content, over_semaphore)
            # over_semaphore<=0 时阻塞，被子线程release后才能继续进行
            await over_semaphore.acquire()
            # ===============================================
            return _read_content.content

    async def write(self, content):
        if not self._f.writable():
            raise io.UnsupportedOperation()
        async with self._rw_lock:
            # ===============================================
            # 原理同读方法
            over_semaphore = asyncio.Semaphore(0)
            self._loop.run_in_executor(self._executor \
                                       , self._write, content, over_semaphore)
            await over_semaphore.acquire()
            # ===============================================

    async def seek(self, offset, where=0):
        async with self._rw_lock:
            self._f.seek(offset, where)

    async def close(self):
        async with self._rw_lock:
            self._f.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        try:
            self._f.close()
        finally:
            pass


def get_url_list(num1, num2):
    targe_url=[]
    # 260762
    for i in range(num1, num2):
        guid = "A44E1D3464006331A8AB420D4F0F4BFA617ACAE4D99CF4DCEFCF81A600F4D304"
        code = "6tcab"
        u = f"http://cri.gz.gov.cn/Search/Result?validateCode={code}&guid={guid}&keywords=%E5%B9%BF%E5%B7%9E%E6%B3%A8%E5%86%8C%E4%BC%81%E4%B8%9A&page={str(i)}"
        targe_url.append((u, i))
    return targe_url


async def run(url_list):
        h = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Cookie": "UM_distinctid=1669a62b483a3-0c84fd3f3b9c33-f373567-144000-1669a62b48524e",
            "Host": "cri.gz.gov.cn",
            "Origin": "https://www.zhenai.com",
            "Referer": "https://www.zhenai.com/n/search",
            "Upgrade-Insecure-Requests": "1"
        }
        async with aiohttp.ClientSession() as session:
            for url in url_list:
                async with session.get(url[0],headers=h) as response:
                    res=await response.text()
                    t = res.encode('gbk',errors='ignore').decode('gbk')
                    print(url[1])
                    with AsyncFile(f"E:\\tmp\\{str(url[1])}.txt","r") as f:
                        await f.write(t)
                    print('end ', url[1])


def split_list(listTemp, n):
    for i in range(0, len(listTemp), n):
        yield listTemp[i:i + n]


def run_process(l):
    # cur, conn = connect_oracle()
    loop=asyncio.get_event_loop()
    tasks=[]
    for i in split_list(l, 500):
        tasks.append(asyncio.ensure_future(run(i)))
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

def error_log(s: str):
    print(s)


if __name__ == "__main__":
    l = [get_url_list((num-1)*50000+1, num*50000+1) for num in range(1, 6)]
    # 建立    两个进程池
    pool = Pool(5)
    for m in  l:
        # 执行check_run_loop    run函数
        pool.apply_async(run_process, (m,), callback=error_log)