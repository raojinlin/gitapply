## git修改同步工具

將本地仓库修改应用到不同计算机的本地仓库而不用产生commit, 本工具分为服务端和客户端两个程序。


* 客户端：
```shell
$ ./bin/gitapply_client.py --server http://127.0.0.1:1080 --repository /tmp/gittest --remote-repository test
```


* 服务端
```
$ ./bin/gitapply_server.py --repository-map test:/tmp/gittest_server --repository-map test2:/tmp/gittest_server2
```
