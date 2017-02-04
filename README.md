# WorkStatusForNetTrafficMonitorAndClassify

这是一个监控浏览器HTTP/HTTPS请求信息，并分析其网址标题对应上网行为的项目。

### WorkStatusForNetTrafficWithDjango

这是该项目的服务端。

使用Python的Django框架搭建后台服务端，提供数据上传、数据分析、数据显示功能。

通过Celery进行任务调度，启动服务端的数据分析任务，避免阻塞。

网页标题通过jieba分词进行分词，通过修改源码以适应英文单词和词组。

使用scikit-learn的朴素贝叶斯分类进行数据分类，将每一个网址根据其标题成分，分类成娱乐、搜索、学习等等，由数据库设置。

### WorkStatusFromproxy

这是该项目的客户端。

使用mitmproxy进行中间人代理，以便监测HTTP(S)的请求，以此获取每一次浏览网页的标题，地址等信息。

通过Celery进行后台数据上传。