## git修改同步工具

將本地仓库修改应用到不同计算机的本地仓库而不用产生commit, 本工具分为服务端和客户端两个程序。


* 客户端：
```shell
$ ./bin/gitapply_client.py\
  --server http://127.0.0.1:1080\
  --repository /tmp/gittest\
  --remote-repository test
```


* 服务端
```
$ ./bin/gitapply_server.py\
  --repository-map test:/tmp/gittest_server\
  --repository-map test2:/tmp/gittest_server2
```

* 服务端HTTP API

| Path        | 请求           | 响应  | 描述 |
| ------------- |:-------------:| -----:| ----:|
| /api/new     | [newRequest](#newRequest) | [newResponse](#Response) | 将本地仓库新增的文件在服务端创建 |
| /api/apply      | [applyRequest](#applyRequest)      |   [applyResponse](#Response) | 将本地仓库的patch应用到服务端 |

* HTTP状态码
  * 200: 正常
  * 400: 参数错误
  * 500: 内部错误


### newRequest

```js
{
  "repository": "在服务器端定义的repository",
  "file": "xxx.py",
  "content": "xxxxx", // base64 encode
  "encoding": "base64"
}
```

### Response

```js
{
  "data": "ok",
  "msg": "", // 如果有错误发生
  "error": false // 如果有错误则为true
}
```

### applyRequest

```js
{
  "repository": "test", // 在服务器端定义的repository
  "content": "", // 本地仓库的patch
}
```
