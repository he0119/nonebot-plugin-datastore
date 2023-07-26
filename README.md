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
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">
  <a href="https://codecov.io/gh/he0119/nonebot-plugin-datastore">
    <img src="https://codecov.io/gh/he0119/nonebot-plugin-datastore/branch/main/graph/badge.svg?token=jd5ufc1alv"/>
  </a>
  <a href="https://jq.qq.com/?_wv=1027&k=7zQUpiGp">
    <img src="https://img.shields.io/badge/QQ%E7%BE%A4-730374631-orange?style=flat-square" alt="QQ Chat Group">
  </a>
</p>

## 安装

- 使用 nb-cli

```sh
nb plugin install nonebot-plugin-datastore
```

- 使用 pip

```sh
pip install nonebot-plugin-datastore
```

## 使用方式

先在插件代码最前面声明依赖

```python
from nonebot import require
require("nonebot_plugin_datastore")
```

### 插件数据相关功能

```python
from nonebot_plugin_datastore import get_plugin_data

plugin_data = get_plugin_data()

# 获取插件缓存目录
plugin_data.cache_dir
# 获取插件配置目录
plugin_data.config_dir
# 获取插件数据目录
plugin_data.data_dir

# 读取配置
await plugin_data.config.get(key)
# 存储配置
await plugin_data.config.set(key, value)
```

### 数据库相关功能，详细用法见 [SQLAlchemy](https://docs.sqlalchemy.org/orm/quickstart.html)

```python
from nonebot import on_command
from nonebot.params import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from nonebot_plugin_datastore import get_plugin_data, get_session

# 定义模型
Model = get_plugin_data().Model

class Example(Model):
    """示例模型"""

    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str]

matcher = on_command("test")

# 数据库相关操作
@matcher.handle()
async def handle(session: AsyncSession = Depends(get_session)):
    example = Example(message="matcher")
    session.add(example)
    await session.commit()

# 因为 driver.on_startup 无法保证函数运行顺序
# 如需在 NoneBot 启动时且数据库初始化后运行的函数
# 请使用 post_db_init 而不是 Nonebot 的 on_startup
from nonebot_plugin_datastore.db import post_db_init


@post_db_init
async def do_something():
  pass
```

### 命令行支持（需安装 [nb-cli 1.0+](https://github.com/nonebot/nb-cli)）

如果使用 pipx 安装的 nb-cli，则需要运行 `pip install nonebot-plugin-datastore[cli]` 安装命令行所需依赖。

#### 数据存储路径

```shell
# 获取当前数据存储路径
nb datastore dir
# 获取指定插件的数据存储路径
nb datastore dir --name plugin_name
```

#### 数据库管理，详细用法见 [Alembic](https://alembic.sqlalchemy.org/en/latest/)

生成迁移文件

```shell
# 生成项目内所有启用数据库插件的迁移文件（不包括 site-packages 中的插件）
nb datastore migrate
# 生成指定插件的迁移文件
nb datastore migrate --name plugin_name -m example
```

升级插件数据库

```shell
# 升级所有启用数据库插件的数据库
nb datastore upgrade
# 升级指定插件的数据库
nb datastore upgrade --name plugin_name
# 升级至指定版本
nb datastore upgrade --name plugin_name revision
```

降级插件数据库

```shell
# 降级所有启用数据库插件的数据库
nb datastore downgrade
# 降级指定插件的数据库
nb datastore downgrade --name plugin_name
# 降级至指定版本
nb datastore downgrade --name plugin_name revision
```

## 注意

### 数据库迁移

推荐启动机器人前运行 `nb datastore upgrade` 升级数据库至最新版本。因为当前插件自动迁移依赖 `NoneBot` 的 `on_startup` 钩子，很容易受到其他插件影响。

这里推荐 [tiangolo/uvicorn-gunicorn](https://github.com/tiangolo/uvicorn-gunicorn-docker) 镜像，通过配置 `prestart.sh` 可确保启动机器人前运行迁移脚本。具体的例子可参考 [CoolQBot](https://github.com/he0119/CoolQBot/)。

### MySQL 数据库连接丢失

当使用 `MySQL` 时，你可能会遇到 `2013: lost connection to mysql server during query` 的报错。

如果遇到这种错误，可以尝试设置 `pool_recycle` 为一个小于数据库超时的值。或者设置 `pool_pre_ping` 为 `True`。

```env
DATASTORE_ENGINE_OPTIONS={"pool_recycle": 3600}
DATASTORE_ENGINE_OPTIONS={"pool_pre_ping": true}
```

详细介绍可查看 `SQLAlchemy` 文档的 [dealing-with-disconnects](https://docs.sqlalchemy.org/en/20/core/pooling.html#dealing-with-disconnects) 章节。

### SQLite 数据库已锁定

使用 `SQLite` 数据库时，如果在写入时遇到 `(sqlite3.OperationalError) database is locked` 错误。可尝试将 `poolclass` 设置为 `StaticPool`，保持有且仅有一个连接。不过这样设置之后，在程序运行期间，你的数据库文件都将被占用。

### 不同插件的表之间的关联关系

datastore 默认会给每个插件的 Base 模型提供独立的 registry，所以不同插件间的表无法建立关联关系。如果你需要与其他插件的表建立关联关系，请在需要关联的两个插件中都调用 use_global_registry 函数使用全局 registry。

```python
# 定义模型
db = get_plugin_data()
db.use_global_registry()

class Example(db.Model):
    """实例函数"""

    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str]

    tests: Mapped["Test"] = relationship(back_populates="example")


class Test(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    example_id: Mapped[int] = mapped_column(ForeignKey("plugin_example.id"))
    example: Mapped[Example] = relationship(back_populates="tests")

# 注意，为了避免不同插件的模型同名而报错，请一定要加上这一句，避免报错
# sqlalchemy.exc.InvalidRequestError: Multiple classes found for path "Test" in the registry of this declarative base. Please use a fully module-qualified path.
Example.tests = relationship(Test, back_populates="example")
```

## 配置项

配置方式：直接在 `NoneBot` 全局配置文件中添加以下配置项即可。

### datastore_cache_dir

- 类型: `Path`
- 默认:
  - macOS: ~/Library/Caches/nonebot2
  - Unix: ~/.cache/nonebot2 (XDG default)
  - Windows: C:\Users\<username>\AppData\Local\nonebot2\Cache
- 说明: 缓存目录

### datastore_config_dir

- 类型: `Path`
- 默认:
  - macOS: same as user_data_dir
  - Unix: ~/.config/nonebot2
  - Win XP (roaming): C:\Documents and Settings\<username>\Local Settings\Application Data\nonebot2
  - Win 7 (roaming): C:\Users\<username>\AppData\Roaming\nonebot2
- 说明: 配置目录

### datastore_data_dir

- 类型: `Path`
- 默认:
  - macOS: ~/Library/Application Support/nonebot2
  - Unix: ~/.local/share/nonebot2 or in $XDG_DATA_HOME, if defined
  - Win XP (not roaming): C:\Documents and Settings\<username>\Application Data\nonebot2
  - Win 7 (not roaming): C:\Users\<username>\AppData\Local\nonebot2
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
- 说明: `echo` 和 `echo_pool` 的默认值，是否显示数据库执行的语句与其参数列表，还有连接池的相关信息

### datastore_engine_options

- 类型: `dict[str, Any]`
- 默认: `{}`
- 说明: 向 `sqlalchemy.ext.asyncio.create_async_engine()` 传递的参数

### datastore_config_provider

- 类型: `str`
- 默认: `~json`
- 说明: 选择存放配置的类型，当前支持 json, yaml, toml, database 四种类型，也可设置为实现 `ConfigProvider` 的自定义类型。

## 鸣谢

- [`NoneBot Plugin LocalStore`](https://github.com/nonebot/plugin-localstore): 提供了默认的文件存储位置
- [`Flask-SQLAlchemy`](https://github.com/pallets-eco/flask-sqlalchemy/): 借鉴了数据库的实现思路
- [`Flask-Alembic`](https://github.com/davidism/flask-alembic): 借鉴了命令行的实现思路
