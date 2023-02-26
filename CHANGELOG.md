# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/lang/zh-CN/spec/v2.0.0.html).

## [Unreleased]

## [0.5.10] - 2023-02-26

### Added

- 添加 engine_options 配置项

### Fixed

- 修复自定义数据库连接可能会出现文件夹未创建的问题

## [0.5.9] - 2023-02-25

### Fixed

- 修复运行中删除目录导致报错的问题
- 升级数据库时只执行对应插件的 pre_db_init 函数
- 修复运行中删除文件后写入配置时报错的问题

## [0.5.8] - 2023-02-10

### Added

- 添加运行 cli 缺少依赖时的提示

### Fixed

- 添加 py.typed 文件

## [0.5.7] - 2023-02-06

### Fixed

- 修复缺少 nb_cli 模块的问题
- 数据库初始化前执行的函数运行出错，则不继续执行后续初始化
- 修复插件间模型定义冲突的问题

## [0.5.6] - 2023-01-26

### Added

- 添加查看数据存储路径的命令

### Fixed

- 修复运行升级命令时同时升级多个插件报错的问题

## [0.5.5] - 2023-01-21

### Added

- 添加 history, current, heads, check 命令
- 添加 migrate 命令

## [0.5.4] - 2023-01-16

### Changed

- 默认开启 compare_type
- 兼容以前不支持迁移的版本

## [0.5.3] - 2023-01-16

### Changed

- 默认开启 render_as_batch

## [0.5.2] - 2023-01-15

### Added

- 添加 pre_db_init 钩子

## [0.5.1] - 2023-01-15

### Fixed

- 修复迁移文件夹名称为单数的问题

## [0.5.0] - 2023-01-15

### Added

- 支持 Alembic
- 添加 get_plugin_data 函数，在插件中调用会自动返回符合当前插件名的 PluginData 实例

## [0.4.0] - 2022-10-05

### Removed

- 移除 Export 功能
- 对照 NoneBot2 移除 Python 3.7 支持

## [0.3.4] - 2022-10-05

### Changed

- 限制 NoneBot2 版本

## [0.3.3] - 2022-09-07

### Fixed

- 再次升级 SQLModel 版本，修复问题

## [0.3.2] - 2022-08-28

### Fixed

- 修复 SQLModel 与 SQLAlchemy 不兼容的问题

## [0.3.1] - 2022-05-23

### Added

- 支持下载文件至本地

### Changed

- 使用 require 确保插件加载再 import
- 优化类型提示

### Fixed

- 锁定 SQLAlchemy 版本以避免错误

## [0.3.0] - 2022-02-01

### Changed

- 默认开启数据库

## [0.2.0] - 2022-01-26

### Added

- 增加 `load_json` 与 `dump_json` 方法
- 添加 `create_session` 函数

### Changed

- 统一方法名称为 `dump`
- `dump_pkl` 和 `load_pkl` 不再自动添加 pkl 后缀

## [0.1.1] - 2022-01-24

### Changed

- 每个相同名称的插件数据只会返回同一个实例

## [0.1.0] - 2022-01-24

### Added

- 可以使用的版本。

[unreleased]: https://github.com/he0119/nonebot-plugin-datastore/compare/v0.5.10...HEAD
[0.5.10]: https://github.com/he0119/nonebot-plugin-datastore/compare/v0.5.9...v0.5.10
[0.5.9]: https://github.com/he0119/nonebot-plugin-datastore/compare/v0.5.8...v0.5.9
[0.5.8]: https://github.com/he0119/nonebot-plugin-datastore/compare/v0.5.7...v0.5.8
[0.5.7]: https://github.com/he0119/nonebot-plugin-datastore/compare/v0.5.6...v0.5.7
[0.5.6]: https://github.com/he0119/nonebot-plugin-datastore/compare/v0.5.5...v0.5.6
[0.5.5]: https://github.com/he0119/nonebot-plugin-datastore/compare/v0.5.4...v0.5.5
[0.5.4]: https://github.com/he0119/nonebot-plugin-datastore/compare/v0.5.3...v0.5.4
[0.5.3]: https://github.com/he0119/nonebot-plugin-datastore/compare/v0.5.2...v0.5.3
[0.5.2]: https://github.com/he0119/nonebot-plugin-datastore/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/he0119/nonebot-plugin-datastore/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/he0119/nonebot-plugin-datastore/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/he0119/nonebot-plugin-datastore/compare/v0.3.4...v0.4.0
[0.3.4]: https://github.com/he0119/nonebot-plugin-datastore/compare/v0.3.3...v0.3.4
[0.3.3]: https://github.com/he0119/nonebot-plugin-datastore/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/he0119/nonebot-plugin-datastore/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/he0119/nonebot-plugin-datastore/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/he0119/nonebot-plugin-datastore/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/he0119/nonebot-plugin-datastore/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/he0119/nonebot-plugin-datastore/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/he0119/nonebot-plugin-datastore/releases/tag/v0.1.0
