<!-- markdownlint-disable MD033 MD036 MD041 -->

<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>

<div align="center">

# NoneBot Plugin DataStore

_✨ NoneBot 数据存储插件 ✨_

</div>

<p align="center">
  <a href="https://raw.githubusercontent.com/he0119/nonebot-plugin-datastore/main/LICENSE">
    <img src="https://img.shields.io/github/license/he0119/nonebot-plugin-datastore.svg" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-datastore">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-datastore.svg" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.7.3+-blue.svg" alt="python">
  <a href="https://codecov.io/gh/he0119/nonebot-plugin-datastore">
    <img src="https://codecov.io/gh/he0119/nonebot-plugin-datastore/branch/main/graph/badge.svg?token=jd5ufc1alv"/>
  </a>
</p>

## 使用方式

加载插件后直接导入

```python
# 先声明依赖
from nonebot import require
require("nonebot_plugin_datastore")
# 接着直接导入
from nonebot.params import Depends
from nonebot_plugin_datastore import PluginData, get_session
from sqlmodel.ext.asyncio.session import AsyncSession

DATA = PluginData("plugin_name")

@matcher.handle()
def handle(session: AsyncSession = Depends(get_session)):
    await session.exec()
```

## 配置项

配置方式：直接在 `NoneBot` 全局配置文件中添加以下配置项即可。

### datastore_cache_dir

- 类型: `str`
- 默认: [nonebot_plugin_localstore](https://github.com/nonebot/plugin-localstore) 插件提供的缓存目录
- 说明: 缓存目录

### datastore_config_dir

- 类型: `str`
- 默认: [nonebot_plugin_localstore](https://github.com/nonebot/plugin-localstore) 插件提供的配置目录
- 说明: 配置目录

### datastore_data_dir

- 类型: `str`
- 默认: [nonebot_plugin_localstore](https://github.com/nonebot/plugin-localstore) 插件提供的数据目录
- 说明: 数据目录

### datastore_enable_database

- 类型: `bool`
- 默认: `True`
- 说明: 是否启动数据库

### datastore_database_url

- 类型: `str`
- 默认: `sqlite+aiosqlite:///data_dir/data.db`
- 说明: 数据库连接字符串，默认使用 SQLite 数据库

### datastore_database_echo

- 类型: `bool`
- 默认: `False`
- 说明: 是否显示数据库执行的语句与其参数列表

## 计划

- [x] 调整配置为 K-V 存储
- [x] 调整配置存放位置至专门的配置目录
- [x] 数据库为可选项
- [ ] 支持将配置存放至数据库中
- [ ] 支持 Alembic
