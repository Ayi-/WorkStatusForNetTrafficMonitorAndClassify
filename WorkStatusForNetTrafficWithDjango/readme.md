#这是一个用于分析并显示个人浏览网站的行为的项目
##项目结构说明
- `jieba`文件夹需要覆盖到`pip`安装的jieba分词，对源码进行了修改，以便适应词典结构

##其他
本项目包含mysql-python，需要安装依赖libmysqlclient-dev(ubuntu 14.04)

##配置Docker
暂未完成文档编写
启动nginx

```shell
docker run \
    --name app-nginx \
    -d \
    -p 80:80 \
    -v /code/python/project/WorkStatusForNetTrafficWithDjango/docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro \
    -v /code/python/project/WorkStatusForNetTrafficWithDjango/docker/nginx/conf.d:/etc/nginx/conf.d \
    -v /code/python/project/WorkStatusForNetTrafficWithDjango/:/home/code \
    --link app:app \
    daocloud.io/nginx:1.10.2
```
启动app
```shell
docker run \
    -v /code/python/project/WorkStatusForNetTrafficWithDjango/:/home/code \
    -p 8081:8081 \
    -u root \
    -d \
    --name app \
    python:2.7.12 \
    /home/aiiyi/.pyenv/versions/wsfnt/bin/supervisord -n -c /home/code/supervisord.conf

```

